from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

# Alternativa de seguridad basada en cabecera HTTP Authorization, pensada para producción.
"""
def obtener_rol_desde_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    print("🪪 Token recibido:", credentials.credentials)
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print("✅ Payload decodificado:", payload)
        rol = payload.get("rol")
        if rol != "administrador":
            raise HTTPException(status_code=403, detail="Acceso restringido a administradores")
        return rol
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


#@admin_router.get("/admin", response_class=HTMLResponse)
#def mostrar_panel_admin(request: Request, rol: str = Depends(obtener_rol_desde_token)):
#    return templates.TemplateResponse("dashboard.html", {"request": request})
"""
@admin_router.get("/admin", response_class=HTMLResponse)
def mostrar_panel_admin(request: Request, token: str = Query(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido en la URL")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("✅ Payload decodificado:", payload)
        rol = payload.get("rol")
        if rol != "administrador":
            raise HTTPException(status_code=403, detail="Acceso restringido a administradores")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # 🔹 Obtener usuarios desde la base de datos
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, nombre_usuario, email_usuario, rol, activo FROM usuario")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "usuarios": usuarios,
        "token": token
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
    try:
        # Verificar si ya existe ese email
        cursor.execute("SELECT * FROM usuario WHERE email_usuario = %s", (email_usuario,))
        if cursor.fetchone():
            print(f"⚠️ Usuario ya existe: {email_usuario}")
        else:
            hashed = pwd_context.hash(password)
            cursor.execute("""
                INSERT INTO usuario (nombre_usuario, email_usuario, password, rol, activo)
                VALUES (%s, %s, %s, %s, 1)
            """, (nombre_usuario, email_usuario, hashed, rol))
            conn.commit()
            print(f"✅ Usuario creado desde el panel: {email_usuario} ({rol})")
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
    finally:
        cursor.close()
        conn.close()

    # Redirigir de nuevo al panel (para evitar reenvíos de formulario)
    return RedirectResponse(url=f"/admin?token={token}", status_code=303)

@admin_router.post("/admin/usuarios/toggle_activo")
async def toggle_usuario_activo(id_usuario: int = Form(...), token: str = Form(...)):
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

