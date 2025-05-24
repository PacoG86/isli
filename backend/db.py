import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    """
    Establece y devuelve una conexión a la base de datos MySQL usando variables de entorno.

    Returns:
        mysql.connector.connection.MySQLConnection: Conexión activa con la base de datos.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )
