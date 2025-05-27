"""Módulo de autenticación del backend ISLI.

Gestiona el login de usuarios, verificación de contraseñas y generación de tokens JWT.
Usado por el endpoint /login.
"""
from fastapi import APIRouter, HTTPException, Body
from db import get_connection
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt  # Importar bcrypt directamente
from unidecode import unidecode

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "superclave")
ALGORITHM = "HS256"
# Cambia aquí el tiempo de expiración del token (por ejemplo, 8 horas = 480 minutos)
ACCESS_TOKEN_EXPIRE_MINUTES = 480

login_router = APIRouter()

# In-memory token blacklist (for demo; use DB for production)
REVOKED_TOKENS = set()

def verificar_contrasena(plain_password, hashed_password):
    """
    Verifica si una contraseña en texto plano coincide con un hash bcrypt.

    Args:
        plain_password (str or bytes): Contraseña proporcionada por el usuario.
        hashed_password (str or bytes): Contraseña almacenada en la base de datos.

    Returns:
        bool: True si coinciden, False si no o si ocurre un error.
    """
    try:
        # Convertir contraseña a bytes si es string
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        
        # Convertir hash a bytes si es string
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
            
        # Verificar contraseña usando bcrypt directamente
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Error al verificar contraseña: {e}")
        return False

def hashear_contrasena(plain_password):
    """
    Genera un hash para una contraseña en texto plano.
    Útil para crear nuevos usuarios o actualizar contraseñas.
    Usa bcrypt con semilla aleatoria. Se recomienda para creación y actualización de usuarios.
    """
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password, salt)

def crear_token(data: dict):
    """
    Genera un token JWT a partir de un diccionario de datos.

    - Elimina acentos y normaliza strings antes de codificar.
    - Añade una fecha de expiración automática.

    Args:
        data (dict): Diccionario con los datos del usuario (ej. ID, rol, nombre...).

    Returns:
        str: Token JWT firmado.
    """
    to_encode = {}

    for key, value in data.items():
        if isinstance(value, str):
            to_encode[key] = unidecode(value)  # elimina acentos como é → e
        else:
            to_encode[key] = value

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@login_router.post("/login")
def login(usuario: dict):
    """
    Endpoint de autenticación de usuarios.

    - Verifica que el email exista y que el usuario esté activo.
    - Comprueba la contraseña usando bcrypt.
    - Si es válido, devuelve un token JWT con los datos clave del usuario.

    Args:
        usuario (dict): Diccionario con claves 'correo' y 'contrasenia'.

    Returns:
        dict: Información del usuario autenticado y token de acceso.

    Raises:
        HTTPException: Si las credenciales no son válidas o el usuario está inactivo.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar usuario activo por correo
    cursor.execute("""
        SELECT * FROM usuario
        WHERE email_usuario = %s AND activo = 1
    """, (usuario["correo"],))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    # Verificar si el usuario existe y la contraseña es correcta
    if not user or not verificar_contrasena(usuario["contrasenia"], user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas o usuario inactivo")
    
    # Generar token JWT
    token = crear_token({
        "sub": str(user["id_usuario"]),
        "rol": user["rol"],
        "nombre": user["nombre_usuario"]
    })
    
    # Devolver respuesta
    return {
        "access_token": token,
        "token_type": "bearer",
        "nombre_usuario": user["nombre_usuario"],
        "rol": user["rol"],
        "id_usuario": user["id_usuario"]
    }

@login_router.post("/logout")
def logout(payload: dict = Body(...)):
    """
    Endpoint para revocar/invalidate un token JWT (logout).
    Guarda el token en una blacklist temporal.
    """
    token = payload.get("token")
    print(f"Revoking token: {token!r}")
    if not token:
        raise HTTPException(status_code=400, detail="Token requerido")
    REVOKED_TOKENS.add(token)
    print(f"Current blacklist: {REVOKED_TOKENS}")
    return {"detail": "Token revocado"}

@login_router.get("/validate_token")
def validate_token(token: str):
    print(f"Validating token: {token!r}")
    print(f"Current blacklist: {REVOKED_TOKENS}")
    from jose import JWTError
    try:
        if token in REVOKED_TOKENS:
            print("Token is revoked!")
            raise HTTPException(status_code=401, detail="Token revocado")
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True}
    except JWTError:
        print("Token is invalid or expired!")
        raise HTTPException(status_code=401, detail="Token inválido o expirado")