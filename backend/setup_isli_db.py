import mysql.connector
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Load environment variables for DB connection
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "isli_db")

SQL_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01_crear_base_datos_isli_v3.sql"))

# Usuarios iniciales a insertar
usuarios = [
    ("Pedro García", "pedrog_op@isli.com", "Pedro_op!86", "administrador"),
    ("Pepa Gutiérrez", "pepag_admin@isli.com", "Abcd!86", "administrador"),
    ("Lucía Hernández", "luciah_op@isli.com", "Qwerty!81", "operario"),
    ("Manuel Ruiz", "operario2@isli.com", "Manuelr_op!56", "operario"),
    ("Admin Master", "admin1@isli.com", "Admin!123", "administrador")
]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def run_sql_script(cursor, sql):
    # Salta a siguiente línea si es un comentario o línea vacía
    import re
    statements = [s.strip() for s in re.split(r';\s*(?=CREATE|DROP|INSERT|ALTER|USE|--|$)', sql, flags=re.IGNORECASE) if s.strip()]
    for stmt in statements:
        if stmt.startswith('--') or not stmt:
            continue
        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"Error executing statement: {stmt[:60]}...\n{e}")

if __name__ == "__main__":
    # 1. Conectar a MySQL con credenciales de root
    print("Conectando a MySQL...")
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print("Ejecutando DROP y CREATE DATABASE...")
    with open(SQL_FILE, encoding="utf-8") as f:
        sql = f.read()
    # 2. Ejectuar DROP y CREATE DATABASE y desconectar
    for stmt in sql.split(';'):
        if 'DROP DATABASE' in stmt or 'CREATE DATABASE' in stmt:
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"Error executing statement: {stmt[:60]}...\n{e}")
    conn.commit()
    cursor.close()
    conn.close()

    # 3. Conectar nuevamente a MySQL para evitar errores de conexión
    print(f"Conectando a la base de datos {DB_NAME} para crear tablas...")
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    cursor = conn.cursor()
    # 4. Ejecutar el resto del script SQL para crear tablas
    for stmt in sql.split(';'):
        if ('CREATE TABLE' in stmt or 'ALTER TABLE' in stmt or 'USE ' in stmt) and 'DATABASE' not in stmt:
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"Error executing statement: {stmt[:60]}...\n{e}")
    conn.commit()
    print("Base de datos y tablas creadas.")
    cursor.close()
    conn.close()

    # 5. Conectar a la recién creada base de datos para poblar usuarios
    print(f"Conectando a la base de datos {DB_NAME} para poblar usuarios...")
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    cursor = conn.cursor()
    for nombre, email, raw_pass, rol in usuarios:
        cursor.execute("SELECT * FROM usuario WHERE email_usuario = %s", (email,))
        if cursor.fetchone():
            print(f"Usuario ya existe: {email} → no insertado")
            continue
        hashed = pwd_context.hash(raw_pass)
        cursor.execute("""
            INSERT INTO usuario (nombre_usuario, email_usuario, password, rol, activo)
            VALUES (%s, %s, %s, %s, 1)
        """, (nombre, email, hashed, rol))
        print(f"Insertado: {email} ({rol})")
    conn.commit()
    cursor.close()
    conn.close()
    print("\nSetup finalizado. La base de datos ISLI está lista.")
