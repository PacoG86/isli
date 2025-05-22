import os
import sys
import requests
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PySide6.QtWidgets import QMessageBox


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import sys
from datetime import datetime
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
    try:
        c = canvas.Canvas(ruta_destino, pagesize=A4)
        width, height = A4

        # ==== ENCABEZADO ====
        logo_width = 100
        logo_height = 60
        logo_x = 40
        logo_y = height - logo_height - 40  # Espacio superior

        # Logo a la izquierda
        if logo_path and os.path.exists(logo_path):
            c.drawImage(
                logo_path,
                logo_x,
                logo_y,
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
                mask='auto'
            )

        # Título alineado al centro del logo
        title_y = logo_y + logo_height / 2 - 7  # Ajuste visual fino
        c.setFont("Helvetica-Bold", 16)
        c.drawString(logo_x + logo_width + 20, title_y, "Informe de Control de Calidad")

        # ==== INFORMACIÓN BÁSICA ====
        y = logo_y - 20
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

        # ==== RESUMEN DEL ANÁLISIS ====
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

        # ==== IMÁGENES ANALIZADAS ====
        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "Visores de análisis")
        y -= 20

        for idx, img_path in enumerate(imagenes_procesadas):
            if not os.path.exists(img_path):
                continue

            if y < 120:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica-Bold", 11)
                c.drawString(40, y, "Visores de análisis (continuación)")
                y -= 20

            try:
                c.drawImage(img_path, 40, y - 100, width=200, height=100)
                c.setFont("Helvetica", 8)
                c.drawString(250, y - 60, f"{idx+1}. {os.path.basename(img_path)}")
                y -= 120
            except Exception as e:
                print(f"❌ Error al insertar imagen en PDF: {e}")

        c.save()

        # Mostrar mensaje de éxito
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