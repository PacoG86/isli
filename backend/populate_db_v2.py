#!/usr/bin/env python3
"""
Rellena isli_db con datos de ejemplo y genera un PDF real para cada
control de calidad.

"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
from datetime import datetime, timedelta
from pathlib import Path
import json
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import mysql.connector
from frontend.utils_informes import generar_pdf_completo

load_dotenv()

# Cargar config.json para ruta_informes
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
with open(CONFIG_PATH, encoding='utf-8') as f:
    config = json.load(f)
PDF_ROOT = Path(config.get('ruta_informes', Path.cwd() / 'pdf'))
PDF_ROOT.mkdir(parents=True, exist_ok=True)


DB_CONFIG = dict(
    host=os.getenv("MYSQL_HOST", "127.0.0.1"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASS", "dam202324"),
    database=os.getenv("MYSQL_DB", "isli_db"),
    # auth_plugin="mysql_native_password",
)


# Parámetros que definen los datos sintéticos
RANDOM_SEED = 42
DATES = [datetime(2025, 5, d, 9, 0) for d in (2, 5, 7, 8, 9, 13, 15, 22, 28, 31)]
ROLLS_PER_CONTROL = 1
DEFECT_CATEGORIES = [
    "punto-negro", "pegote-cascarilla", "burbuja", "rayadura", "fibra"
]

rng = random.Random(RANDOM_SEED)

def connect():
    return mysql.connector.connect(**DB_CONFIG)

# Crear PDF
def make_pdf(file_path: Path, control_id: int, control_dt: datetime,
             operator_name: str, roll_count: int):
    """Genera un PDF de informe usando la función estándar del frontend."""
    class DummyTable:
        def rowCount(self): return 1
        def columnCount(self): return 3
        def item(self, row, col):
            from PySide6.QtWidgets import QTableWidgetItem
            return QTableWidgetItem(f"Dato {row},{col}")
    dummy_table = DummyTable()
    imagenes_procesadas = []  # No hay imágenes reales en este contexto demo
    tolerancia_tamano = 0.5
    tolerancia_cantidad = roll_count
    generar_pdf_completo(
        id_control=control_id,
        nombre_usuario=operator_name,
        rol_usuario="operario",
        tablewidget=dummy_table,
        imagenes_procesadas=imagenes_procesadas,
        tolerancia_tamano=tolerancia_tamano,
        tolerancia_cantidad=tolerancia_cantidad,
        ruta_destino=str(file_path),
        logo_path=None,
        parent_widget=None,
        abrir_pdf_automaticamente=False  # Solo crear, no abrir
    )

# Métodos para inserción de filas
def choose_operario(cur):
    cur.execute(
        "SELECT id_usuario, nombre_usuario FROM USUARIO "
        "WHERE rol='operario' AND activo"
    )
    return rng.choice(cur.fetchall())


def insert_control(cur, dt, id_usuario):
    umbral = round(rng.uniform(0.20, 0.60), 2)
    tolerables = rng.randint(2, 6)
    cur.execute(
        """INSERT INTO CONTROL_CALIDAD
           (id_usuario, umbral_tamano_defecto,
            num_defectos_tolerables_por_tamano,
            fecha_control, observacs)
           VALUES (%s,%s,%s,%s,%s)
        """,
        (id_usuario, umbral, tolerables, dt,
         "Control rutinario" if rng.random() < 0.7 else None)
    )
    return cur.lastrowid, tolerables


def insert_roll(cur, name, dt):
    ruta = f"/data/rollos/{name}.tif"
    ndef = rng.randint(0, 30)
    cur.execute(
        """INSERT INTO ROLLO
              (nombre_rollo, ruta_local_rollo, num_defectos_rollo, estado_rollo)
           VALUES (%s,%s,%s,'disponible')""",
        (name, ruta, ndef)
    )
    return cur.lastrowid, ndef


def insert_rollo_controlado(cur, id_rollo, id_control, orden, tolerables, ndef):
    intoler = max(0, ndef - tolerables)
    cur.execute(
        """INSERT INTO ROLLO_CONTROLADO
              (id_rollo, id_control, total_defectos_intolerables_rollo,
               resultado_rollo, orden_analisis)
           VALUES (%s,%s,%s,%s,%s)""",
        (id_rollo, id_control, intoler, "ok" if intoler == 0 else "nok", orden)
    )
    return intoler


def insert_img_and_measurements(cur, id_rollo, id_control, dt, intoler):
    n_imgs = max(1, min(5, intoler or rng.randint(1, 3)))
    for i in range(1, n_imgs + 1):
        fname = f"D_{id_rollo:04d}_{i:02d}.jpg"
        ts = dt + timedelta(minutes=rng.randint(5, 300))
        size = round(rng.uniform(0.1, 1.2), 2)
        clas = "nok" if size > 0.5 else "ok"
        cur.execute(
            """INSERT INTO IMG_DEFECTO
                 (id_rollo, id_control, nombre_archivo, fecha_captura,
                  max_dim_defecto_medido, clasificacion)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (id_rollo, id_control, fname, ts, size, clas)
        )
        img_id = cur.lastrowid
        # área mínima y máxima
        for area, tipo in zip(sorted(rng.uniform(0.1, 10.0) for _ in range(2)),
                              ("min", "max")):
            cur.execute(
                """INSERT INTO DEFECTO_MEDIDO
                     (id_imagen, area_mm, tipo_valor, tipo_defecto)
                   VALUES (%s,%s,%s,%s)""",
                (img_id, round(area, 2), tipo, rng.choice(DEFECT_CATEGORIES))
            )


def insert_informe(cur, id_control, pdf_path, generated_by, dt):
    cur.execute(
        """INSERT INTO INFORME_CONTROL
             (id_control, ruta_pdf, generado_por, fecha_generacion, notas)
           VALUES (%s,%s,%s,%s,'Informe de prueba generado automáticamente')""",
        (id_control, str(pdf_path), generated_by, dt + timedelta(hours=8))
    )


# Método principal
def populate():
    rng.seed(RANDOM_SEED)
    cnx = connect()
    cur = cnx.cursor()

    for dt in DATES:
        # 1. Operario y encabezado de control
        id_op, name_op = choose_operario(cur)
        id_ctrl, tolerables = insert_control(cur, dt, id_op)

        # 2. Rollos
        for orden in range(1, ROLLS_PER_CONTROL + 1):
            roll_name = f"ROLLO_{dt:%Y%m%d}_{orden:02d}"
            id_rollo, ndef = insert_roll(cur, roll_name, dt)
            intoler = insert_rollo_controlado(
                cur, id_rollo, id_ctrl, orden, tolerables, ndef
            )
            insert_img_and_measurements(cur, id_rollo, id_ctrl, dt, intoler)

        # 3. Generación de PDF y metadatos
        pdf_path = PDF_ROOT / f"control_{id_ctrl:04d}.pdf"
        make_pdf(pdf_path, id_ctrl, dt, name_op, ROLLS_PER_CONTROL)
        insert_informe(cur, id_ctrl, pdf_path, 5, dt)

    cnx.commit()
    cur.close()
    cnx.close()
    print("\nTodos los datos y PDFs generados con éxito.")


if __name__ == "__main__":
    populate()
