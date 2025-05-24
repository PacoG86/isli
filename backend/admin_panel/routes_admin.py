from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from fastapi import Query
from fastapi import Form
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from db import get_connection

load_dotenv()

# Configuración de plantillas
ruta_templates = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=ruta_templates)

# Seguridad JWT
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "superclave")
ALGORITHM = "HS256"

admin_router = APIRouter()

@admin_router.get("/admin", response_class=HTMLResponse)
def mostrar_panel_admin(request: Request, token: str = Query(None)):
    """
    Muestra el panel de administración si el token es válido y el usuario es administrador.

    Valida el token JWT proporcionado por URL, verifica el rol y carga:
    - Lista de usuarios.
    - Rollos controlados.
    - Solicitudes pendientes de cambio de contraseña.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido en la URL")

    try:
        token = token.strip()  # eliminar espacios invisibles
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Payload decodificado:", payload)
        rol = payload.get("rol")
        if rol != "administrador":
            raise HTTPException(status_code=403, detail="Acceso restringido a administradores")
    except JWTError as e:
        print(f"Error al decodificar token: {e}")
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Obtener usuarios desde la base de datos
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Obtener usuarios y verificar si tienen solicitudes pendientes
    cursor.execute("""
        SELECT u.id_usuario, u.nombre_usuario, u.email_usuario, u.rol, u.activo,
            EXISTS (
                SELECT 1 FROM SOLICITUD_CAMBIO_PASSWORD s
                WHERE s.email_usuario = u.email_usuario AND s.estado_solicitud = 'pendiente'
            ) AS tiene_solicitud_pendiente
        FROM usuario u
    """)
    usuarios = cursor.fetchall()

    
    cursor.execute("SELECT id_rollo, ruta_local_rollo, estado_rollo FROM rollo WHERE estado_rollo = 'controlado'")
    rollos = cursor.fetchall()

    cursor.execute("""
        SELECT email_usuario FROM SOLICITUD_CAMBIO_PASSWORD
        WHERE estado_solicitud = 'pendiente'
    """)
    solicitudes_pendientes = {row["email_usuario"] for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "usuarios": usuarios,
        "rollos": rollos,
        "token": token,
        "solicitudes_pendientes": solicitudes_pendientes
    })

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@admin_router.post("/admin/usuarios/crear")
async def crear_usuario_desde_panel(
    request: Request,
    nombre_usuario: str = Form(...),
    email_usuario: str = Form(...),
    password: str = Form(...),
    rol: str = Form(...),
    token: str = Form(...)
):
    conn = get_connection()
    cursor = conn.cursor()
    """
    Crea un nuevo usuario desde el panel si el correo no está registrado.

    Hashea la contraseña, asigna rol y marca el usuario como activo.
    """
    try:
        # Verificar si ya existe ese email
        cursor.execute("SELECT * FROM usuario WHERE email_usuario = %s", (email_usuario,))
        if cursor.fetchone():
            print(f"Usuario ya existe: {email_usuario}")
        else:
            hashed = pwd_context.hash(password)
            cursor.execute("""
                INSERT INTO usuario (nombre_usuario, email_usuario, password, rol, activo)
                VALUES (%s, %s, %s, %s, 1)
            """, (nombre_usuario, email_usuario, hashed, rol))
            conn.commit()
            print(f"Usuario creado desde el panel: {email_usuario} ({rol})")
    except Exception as e:
        print(f"Error al crear usuario: {e}")
    finally:
        cursor.close()
        conn.close()

    # Redirigir de nuevo al panel (para evitar reenvíos de formulario)
    return RedirectResponse(url=f"/admin?token={token}", status_code=303)

@admin_router.post("/admin/usuarios/toggle_activo")
async def toggle_usuario_activo(id_usuario: int = Form(...), token: str = Form(...)):
    """
    Activa o desactiva un usuario alternando su estado entre 1 y 0.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener estado actual
    cursor.execute("SELECT activo FROM usuario WHERE id_usuario = %s", (id_usuario,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nuevo_estado = 0 if result[0] == 1 else 1
    cursor.execute("UPDATE usuario SET activo = %s WHERE id_usuario = %s", (nuevo_estado, id_usuario))
    conn.commit()

    cursor.close()
    conn.close()
    return RedirectResponse(url=f"/admin?token={token}", status_code=303)


@admin_router.post("/admin/usuarios/cambiar_rol")
async def cambiar_rol_usuario(id_usuario: int = Form(...), token: str = Form(...)):
    """
    Cambia el rol de un usuario entre 'operario' y 'administrador'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT rol FROM usuario WHERE id_usuario = %s", (id_usuario,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nuevo_rol = "administrador" if result[0] == "operario" else "operario"
    cursor.execute("UPDATE usuario SET rol = %s WHERE id_usuario = %s", (nuevo_rol, id_usuario))
    conn.commit()

    cursor.close()
    conn.close()
    return RedirectResponse(url=f"/admin?token={token}", status_code=303)

@admin_router.post("/admin/rollos/devolver")
async def devolver_rollo_al_almacen(id_rollo: int = Form(...), token: str = Form(...)):
    """
    Devuelve un rollo al estado 'disponible' en el sistema.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE rollo SET estado_rollo = 'disponible' WHERE id_rollo = %s", (id_rollo,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return RedirectResponse(url=f"/admin?token={token}", status_code=303)

@admin_router.post("/admin/usuarios/reiniciar_password")
async def reiniciar_contrasena_usuario(email_usuario: str = Form(...), token: str = Form(...)):
    """
    Reinicia la contraseña de un usuario según una solicitud pendiente.

    - Busca la solicitud más reciente.
    - Hashea la nueva contraseña.
    - Actualiza la base de datos y marca la solicitud como atendida.

    Args:
        email_usuario (str): Correo del usuario con solicitud pendiente.
        token (str): Token JWT del administrador (para redirección).

    Returns:
        RedirectResponse: Redirección al panel administrativo.

    Raises:
        HTTPException: Si no hay solicitud o si ocurre un error de base de datos.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Buscar la última solicitud pendiente para ese email
        cursor.execute("""
            SELECT id_solicitud, password_nueva
            FROM SOLICITUD_CAMBIO_PASSWORD
            WHERE email_usuario = %s AND estado_solicitud = 'pendiente'
            ORDER BY id_solicitud DESC
            LIMIT 1
        """, (email_usuario,))
        solicitud = cursor.fetchone()

        if not solicitud:
            raise HTTPException(status_code=404, detail="No hay solicitud pendiente para este usuario")

        id_solicitud, password_nueva = solicitud

        # Hashear la nueva contraseña
        hashed = pwd_context.hash(password_nueva)

        # Actualizar la contraseña del usuario
        cursor.execute("""
            UPDATE USUARIO SET password = %s WHERE email_usuario = %s
        """, (hashed, email_usuario))

        # Marcar la solicitud como atendida
        cursor.execute("""
            UPDATE SOLICITUD_CAMBIO_PASSWORD SET estado_solicitud = 'atendida'
            WHERE id_solicitud = %s
        """, (id_solicitud,))

        conn.commit()
        print(f"Contraseña reiniciada para: {email_usuario}")
    except Exception as e:
        conn.rollback()
        print(f"Error al reiniciar contraseña: {e}")
        raise HTTPException(status_code=500, detail="Error al reiniciar la contraseña")
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/admin?token={token}", status_code=303)
