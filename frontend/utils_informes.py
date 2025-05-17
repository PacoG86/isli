import os
import sys
import requests
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PySide6.QtWidgets import QMessageBox


def generar_pdf_completo(
    id_control,
    nombre_usuario,
    rol_usuario,
    tablewidget,
    imagenes_procesadas,
    tolerancia_tamano,
    tolerancia_cantidad,
    ruta_destino,
    logo_path=None,
    parent_widget=None
):
    """
    Genera un informe PDF y lo guarda en la ruta especificada.
    - Se puede pasar un logo opcional.
    - Si se proporciona `parent_widget`, se usa para mostrar QMessageBox.
    """

    try:
        c = canvas.Canvas(ruta_destino, pagesize=A4)
        width, height = A4
        y = height - 50

        # Logo
        if logo_path and os.path.exists(logo_path):
            c.drawImage(logo_path, 40, y - 60, width=100, height=40)

        c.setFont("Helvetica-Bold", 14)
        c.drawString(150, y, "Informe de Control de Calidad")
        y -= 30

        c.setFont("Helvetica", 10)
        datos = [
            f"ID Control: {id_control}",
            f"Operario: {nombre_usuario} ({rol_usuario})",
            f"Fecha de informe: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Tolerancia máxima tamaño: {tolerancia_tamano} mm",
            f"Tolerancia máxima cantidad: {tolerancia_cantidad} imágenes",
        ]
        for d in datos:
            c.drawString(40, y, d)
            y -= 15

        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "Resumen del análisis")
        y -= 20

        c.setFont("Helvetica", 9)
        for row in range(tablewidget.rowCount()):
            if y < 100:
                c.showPage()
                y = height - 50
            linea = []
            for col in range(tablewidget.columnCount()):
                item = tablewidget.item(row, col)
                linea.append(item.text() if item else "")
            c.drawString(40, y, " | ".join(linea))
            y -= 12

        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "Visores de análisis")
        y -= 20

        for img_path in imagenes_procesadas[:6]:
            if y < 120:
                c.showPage()
                y = height - 50
            if os.path.exists(img_path):
                try:
                    c.drawImage(img_path, 40, y - 100, width=200, height=100)
                    c.drawString(250, y - 60, os.path.basename(img_path))
                    y -= 120
                except Exception as e:
                    print(f"❌ Error al insertar imagen en PDF: {e}")

        c.save()

        # Mostrar mensaje de éxito y abrir el PDF
        if parent_widget:
            QMessageBox.information(parent_widget, "Informe generado", f"Informe guardado en:\n{ruta_destino}")

        abrir_pdf(ruta_destino)

    except Exception as e:
        print(f"❌ Error al generar el PDF: {e}")
        if parent_widget:
            QMessageBox.critical(parent_widget, "Error al generar informe", f"Error al crear el informe:\n\n{str(e)}")


def abrir_pdf(ruta_pdf):
    """Abre el PDF según el sistema operativo"""
    import subprocess
    try:
        if sys.platform.startswith("darwin"):
            subprocess.call(("open", ruta_pdf))
        elif os.name == "nt":
            os.startfile(ruta_pdf)
        elif os.name == "posix":
            subprocess.call(("xdg-open", ruta_pdf))
    except Exception as e:
        print(f"❌ No se pudo abrir el PDF: {e}")

def guardar_registro_informe(id_control, ruta_pdf, generado_por):
    """
    Envía al backend la información del informe generado para registrar en la tabla INFORME_CONTROL.
    """
    payload = {
        "id_control": id_control,
        "ruta_pdf": ruta_pdf,
        "generado_por": generado_por,
        "fecha_generacion": datetime.now().isoformat(),
        "notas": ""  # se podrá actualizar más adelante desde la pantalla de histórico
    }

    try:
        response = requests.post("http://localhost:8000/controles/informe/nuevo", json=payload)
        if response.status_code == 200:
            print("✅ Informe registrado correctamente.")
            return True
        else:
            print(f"❌ Error al registrar informe: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Excepción al registrar informe: {e}")
        return False