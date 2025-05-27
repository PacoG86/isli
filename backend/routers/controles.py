"""Módulo de endpoints del backend para gestionar controles de calidad.

Incluye creación de controles, consulta de histórico, informes, comentarios y solicitudes de cambio de contraseña.
"""
import os
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from schemas.schemas_controles import ControlCalidadInput, InformeControlInput, ActualizarNotasInput, SolicitudCambioPassword
from db import get_connection
from typing import List, Optional

router = APIRouter(prefix="/controles", tags=["Controles"])

@router.post("/nuevo")
def guardar_control_calidad(control: ControlCalidadInput):
    """
    Guarda un nuevo control de calidad en la base de datos.

    Inserta registros en:
    - CONTROL_CALIDAD
    - ROLLO y ROLLO_CONTROLADO
    - IMG_DEFECTO y DEFECTO_MEDIDO

    Args:
        control (ControlCalidadInput): Datos completos del control, imágenes y defectos.

    Returns:
        dict: Mensaje de éxito y ID del control creado.

    Raises:
        HTTPException: Si ocurre un error en la base de datos.
    """
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

        # Buscar o insertar ROLLO
        nombre_rollo = os.path.basename(control.rollo.ruta_local_rollo).strip().lower()
        cursor.execute("SELECT id_rollo FROM ROLLO WHERE TRIM(LOWER(nombre_rollo)) = %s", (nombre_rollo,))
        rollo_existente = cursor.fetchone()

        if rollo_existente:
            id_rollo = rollo_existente[0]
        else:
            cursor.execute("""
                INSERT INTO ROLLO (ruta_local_rollo, nombre_rollo, num_defectos_rollo, estado_rollo)
                VALUES (%s, %s, %s, %s)
            """, (
                control.rollo.ruta_local_rollo,
                nombre_rollo,
                control.rollo.num_defectos_rollo,
                "controlado"
            ))
            id_rollo = cursor.lastrowid

        # Insertar ROLLO_CONTROLADO
        rollo = control.rollo
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

        # Insertar IMG_DEFECTO y DEFECTO_MEDIDO
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
                img.clasificacion  # ok / nok
            ))
            id_imagen = cursor.lastrowid

            for defecto in img.defectos:
                # Este bloque ahora guarda tipo y valor del defecto (min o max)
                cursor.execute("""
                    INSERT INTO DEFECTO_MEDIDO (id_imagen, area_mm, tipo_valor, tipo_defecto)
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_imagen,
                    defecto.area,
                    defecto.tipo_valor,       # 'min' o 'max'
                    defecto.tipo_defecto      # 'punto-negro', etc.
                ))

        # Marcar rollo como controlado
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
    """
    Obtiene el ID del último control registrado y sugiere el siguiente.

    Returns:
        dict: El siguiente ID potencial para el próximo control.
    """
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
    """
    Devuelve el listado de controles de calidad registrados, con filtros opcionales.

    Args:
        max_defectos (int, opcional): Máximo número de defectos tolerables.
        max_dim (float, opcional): Máximo umbral de tamaño de defecto.
        usuario (str, opcional): Nombre parcial del usuario.
        desde (datetime, opcional): Fecha mínima del control.
        hasta (datetime, opcional): Fecha máxima del control.

    Returns:
        List[dict]: Controles que cumplen con los filtros aplicados.
    """
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
    """
    Guarda un nuevo informe PDF generado para un control existente.

    Args:
        informe (InformeControlInput): Datos del informe (ruta, autor, notas...).

    Returns:
        dict: Confirmación de éxito.
    """
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
    """
    Calcula el siguiente número de orden para un rollo controlado.

    Args:
        nombre_rollo (str): Nombre del rollo.

    Returns:
        dict: Número de orden de análisis siguiente.

    Raises:
        HTTPException: Si el rollo no existe.
    """
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
    """
    Verifica si ya existe un informe PDF para un control específico.

    Args:
        id_control (int): ID del control.

    Returns:
        dict: Indica si existe el informe y su ruta.
    """
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
    """
    Actualiza el campo de notas de un informe existente.

    Args:
        datos (ActualizarNotasInput): Nuevas notas e ID del control asociado.
    """
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
    """
    Registra una solicitud de cambio de contraseña para un usuario.

    Verifica si el correo existe, y si es así, guarda la solicitud como 'pendiente'.

    Args:
        solicitud (SolicitudCambioPassword): Correo, motivo, nueva contraseña y timestamp.

    Returns:
        dict: Mensaje de confirmación o error.

    Raises:
        HTTPException: Si el correo no está registrado o falla la inserción.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Validar existencia del correo
        cursor.execute("SELECT COUNT(*) FROM USUARIO WHERE email_usuario = %s", (solicitud.email_usuario,))
        existe = cursor.fetchone()[0]

        if not existe:
            raise HTTPException(status_code=404, detail="Correo no registrado")

        cursor.execute("""
            INSERT INTO SOLICITUD_CAMBIO_PASSWORD (email_usuario, motivo, password_nueva, estado_solicitud, timestamp)
            VALUES (%s, %s, %s, 'pendiente', %s)
        """, (
            solicitud.email_usuario,
            solicitud.motivo,
            solicitud.password_nueva,
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
