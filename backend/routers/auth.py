from fastapi import APIRouter, HTTPException
from db import get_connection
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt  # Importar bcrypt directamente

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "superclave")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

login_router = APIRouter()

def verificar_contrasena(plain_password, hashed_password):
    """
    Verifica si la contraseña en texto plano coincide con el hash almacenado.
    Maneja automáticamente la conversión entre strings y bytes.
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
    """
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password, salt)

def crear_token(data: dict):
    """
    Crea un token JWT con los datos proporcionados.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@login_router.post("/login")
def login(usuario: dict):
    """
    Endpoint para autenticar usuarios y generar tokens JWT.
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
        "sub": user["id_usuario"],
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