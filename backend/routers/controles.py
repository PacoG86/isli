import os, json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from datetime import datetime, time
from schemas.schemas_controles import ControlCalidadInput, InformeControlInput, ActualizarNotasInput, SolicitudCambioPassword
from db import get_connection
from typing import List, Optional

router = APIRouter(prefix="/controles", tags=["Controles"])

@router.post("/nuevo")
def guardar_control_calidad(control: ControlCalidadInput):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Insertar CONTROL_CALIDAD
        cursor.execute("""
            INSERT INTO CONTROL_CALIDAD (id_usuario, umbral_tamano_defecto, num_defectos_tolerables_por_tamano, fecha_control, observacs)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            control.id_usuario,
            control.umbral_tamano_defecto,
            control.num_defectos_tolerables_por_tamano,
            control.fecha_control,
            ""
        ))
        id_control = cursor.lastrowid

        # Extraer nombre del rollo desde la ruta
        nombre_rollo = os.path.basename(control.rollo.ruta_local_rollo).strip().lower()

        print(f"🔎 Buscando id_rollo para nombre_rollo='{nombre_rollo}'")
        # Buscar ROLLO por nombre_rollo en lugar de ruta
        cursor.execute("SELECT id_rollo FROM ROLLO WHERE TRIM(LOWER(nombre_rollo)) = %s", (nombre_rollo.strip().lower(),))
        rollo_existente = cursor.fetchone()
        print(f"📦 Resultado de búsqueda en ROLLO: {rollo_existente}")

        if rollo_existente:
            id_rollo = rollo_existente[0]
        else:
            cursor.execute("""
                INSERT INTO ROLLO (ruta_local_rollo, nombre_rollo, num_defectos_rollo, estado_rollo)
                VALUES (%s, %s, %s, %s)
            """, (
                control.rollo.ruta_local_rollo,
                nombre_rollo,  # ⬅️ usamos el normalizado
                control.rollo.num_defectos_rollo,
                "controlado"
            ))
            id_rollo = cursor.lastrowid


        # Insertar ROLLO_CONTROLADO
        rollo = control.rollo
        print(f"🧩 Insertando ROLLO_CONTROLADO con orden_analisis = {rollo.orden_analisis}")
        cursor.execute("""
            INSERT INTO ROLLO_CONTROLADO (id_rollo, id_control, total_defectos_intolerables_rollo, resultado_rollo, orden_analisis)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            id_rollo,
            id_control,
            rollo.total_defectos_intolerables_rollo,
            rollo.resultado_rollo,
            rollo.orden_analisis
        ))

        # Insertar IMG_DEFECTO y relaciones 
        for img in control.imagenes:
            cursor.execute("""
                INSERT INTO IMG_DEFECTO (id_rollo, id_control, nombre_archivo, fecha_captura, max_dim_defecto_medido, clasificacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                id_rollo,
                id_control,
                img.nombre_archivo,
                img.fecha_captura,
                img.max_dim_defecto_medido,
                img.clasificacion
            ))
            id_imagen = cursor.lastrowid

            # Leer JSON con detalles si existe
            carpeta_json = control.rollo.ruta_local_rollo  # asumimos que esto es la ruta
            nombre_json = os.path.splitext(img.nombre_archivo)[0] + ".json"
            json_path = os.path.join(carpeta_json, nombre_json)
            defectos = []
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        contenido = json.load(f)
                        defectos = contenido.get("defectos", [])
                except Exception as e:
                    print(f"❌ Error leyendo JSON {json_path}: {e}")

            for defecto in defectos:
                cursor.execute("""
                    INSERT INTO DEFECTO_MEDIDO (id_imagen, area, clasificacion)
                    VALUES (%s, %s, %s)
                """, (
                    id_imagen,
                    defecto["area"],
                    defecto["clasificacion"]
                ))
        cursor.execute("UPDATE rollo SET estado_rollo = 'controlado' WHERE id_rollo = %s", (id_rollo,))

        conn.commit()
        return {"msg": "Control de calidad guardado exitosamente", "id_control": id_control}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/ultimo_id_control")
def obtener_ultimo_id_control():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(id_control) FROM CONTROL_CALIDAD")
        resultado = cursor.fetchone()
        ultimo_id = resultado[0] if resultado and resultado[0] is not None else 0
        return {"siguiente_id": ultimo_id + 1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# backend/rutas/controles.py
@router.get("/historico", response_model=List[dict])
def obtener_historico_controles(
    max_defectos: Optional[int] = Query(None),
    max_dim: Optional[float] = Query(None),
    usuario: Optional[str] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None)
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT c.id_control,
                   u.nombre_usuario,
                   c.fecha_control,
                   c.umbral_tamano_defecto,
                   c.num_defectos_tolerables_por_tamano,
                   c.observacs,
                   i.notas,
                   CASE WHEN i.id_informe IS NOT NULL THEN 1 ELSE 0 END AS tiene_informe,
                   rc.resultado_rollo
            FROM CONTROL_CALIDAD c
            JOIN USUARIO u ON c.id_usuario = u.id_usuario
            LEFT JOIN INFORME_CONTROL i ON c.id_control = i.id_control
            LEFT JOIN ROLLO_CONTROLADO rc ON c.id_control = rc.id_control
            WHERE 1=1
        """
        params = []

        if max_defectos is not None:
            query += " AND c.num_defectos_tolerables_por_tamano <= %s"
            params.append(max_defectos)

        if max_dim is not None:
            query += " AND c.umbral_tamano_defecto <= %s"
            params.append(max_dim)

        if usuario is not None:
            query += " AND u.nombre_usuario LIKE %s"
            params.append(f"%{usuario}%")

        if desde is not None:
            query += " AND c.fecha_control >= %s"
            params.append(desde)

        if hasta is not None:
            query += " AND c.fecha_control <= %s"
            params.append(hasta)

        query += " ORDER BY c.fecha_control DESC"

        cursor.execute(query, params)
        controles = cursor.fetchall()
        return controles

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/usuarios", response_model=List[str])
def obtener_lista_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT nombre_usuario FROM USUARIO ORDER BY nombre_usuario ASC")
        usuarios = [fila[0] for fila in cursor.fetchall()]
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/informe/nuevo")
def guardar_informe_control(informe: InformeControlInput):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO INFORME_CONTROL (id_control, ruta_pdf, generado_por, fecha_generacion, notas)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            informe.id_control,
            informe.ruta_pdf,
            informe.generado_por,
            informe.fecha_generacion,
            informe.notas or ""
        ))
        conn.commit()
        return {"msg": "Informe guardado correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/rollo/orden_analisis")
def obtener_orden_analisis(nombre_rollo: str):
    nombre_rollo = nombre_rollo.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verificar si el rollo existe
        cursor.execute("SELECT id_rollo FROM ROLLO WHERE LOWER(TRIM(nombre_rollo)) = %s", (nombre_rollo,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"No existe ningún rollo con nombre '{nombre_rollo}'")

        id_rollo = row[0]

        # Contar cuántos controles tiene ese rollo
        cursor.execute("SELECT COUNT(*) FROM ROLLO_CONTROLADO WHERE id_rollo = %s", (id_rollo,))
        count_row = cursor.fetchone()
        cantidad = count_row[0] if count_row else 0

        return {"siguiente_orden": cantidad + 1}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()
        conn.close()

@router.get("/informe/existe")
def verificar_existencia_informe(id_control: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ruta_pdf FROM INFORME_CONTROL WHERE id_control = %s
        """, (id_control,))
        row = cursor.fetchone()
        if row:
            return {"existe": True, "ruta_pdf": row[0]}
        else:
            return {"existe": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/informe/actualizar_notas")
def actualizar_notas_informe(datos: ActualizarNotasInput):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE INFORME_CONTROL
            SET notas = %s
            WHERE id_control = %s
        """, (datos.notas, datos.id_control))
        conn.commit()
        return {"msg": "Notas actualizadas correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/solicitud_password")
def registrar_solicitud_cambio(solicitud: SolicitudCambioPassword):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Validar existencia del correo
        cursor.execute("SELECT COUNT(*) FROM USUARIO WHERE email_usuario = %s", (solicitud.email_usuario,))
        existe = cursor.fetchone()[0]

        if not existe:
            raise HTTPException(status_code=404, detail="Correo no registrado")

        cursor.execute("""
            INSERT INTO SOLICITUD_CAMBIO_PASSWORD (email_usuario, motivo, timestamp)
            VALUES (%s, %s, %s)
        """, (
            solicitud.email_usuario,
            solicitud.motivo,
            solicitud.timestamp.isoformat()
        ))
        conn.commit()
        return {"mensaje": "Solicitud para cambio de contraseña registrada correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
