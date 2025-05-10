from fastapi import APIRouter, HTTPException
from db import get_connection
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "superclave")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
login_router = APIRouter()

def verificar_contrasena(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@login_router.post("/login")
def login(usuario: dict):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ⚠️ Asegura que solo se autentiquen usuarios activos
    cursor.execute("""
        SELECT * FROM usuario
        WHERE email_usuario = %s AND activo = 1
    """, (usuario["correo"],))
    
    user = cursor.fetchone()

    if not user or not verificar_contrasena(usuario["contrasenia"], user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas o usuario inactivo")

    token = crear_token({
        "sub": usuario["correo"],
        "rol": user["rol"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "nombre_usuario": user["nombre_usuario"],
        "rol": user["rol"]
    }
