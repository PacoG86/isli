from passlib.context import CryptContext
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conexion = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3306))
)

#cursor = conexion.cursor()
#cursor.execute("DELETE FROM usuario")
usuarios = [
    ("Pedro García", "op_pedrog@isli.com", "1234", "administrador"),
    ("Pepa Gutiérrez", "admin2@isli.com", "abcd", "administrador"),
    ("Lucía Hernández", "operario1@isli.com", "qwerty", "operario"),
    ("Manuel Ruiz", "operario2@isli.com", "admin123", "operario")
]

cursor = conexion.cursor()
for nombre, email, raw_pass, rol in usuarios:
    cursor.execute("SELECT * FROM usuario WHERE email_usuario = %s", (email,))
    if cursor.fetchone():
        print(f"⚠️ Usuario ya existe: {email} → no insertado")
        continue

    hashed = pwd_context.hash(raw_pass)
    cursor.execute("""
        INSERT INTO usuario (nombre_usuario, email_usuario, password, rol, activo)
        VALUES (%s, %s, %s, %s, 1)
    """, (nombre, email, hashed, rol))
    print(f"✅ Insertado: {email} ({rol})")

conexion.commit()
cursor.close()
conexion.close()

print("\n✅ Inserción finalizada.")
