import unittest
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
from frontend.utils_informes import generar_pdf_completo
import os
import sys

class TestGeneracionInformePDF(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def test_generar_pdf(self):
        # Crear tabla simulada
        tabla = QTableWidget(2, 3)
        tabla.setHorizontalHeaderLabels(["Imagen", "Resultado", "Tipo defecto"])
        tabla.setItem(0, 0, QTableWidgetItem("img_001.png"))
        tabla.setItem(0, 1, QTableWidgetItem("nok"))
        tabla.setItem(0, 2, QTableWidgetItem("punto-negro"))
        tabla.setItem(1, 0, QTableWidgetItem("img_002.png"))
        tabla.setItem(1, 1, QTableWidgetItem("ok"))
        tabla.setItem(1, 2, QTableWidgetItem(""))

        # Simulación de imágenes procesadas (pueden ser rutas falsas)
        imagenes_procesadas = ["img_001_proc.png", "img_002_proc.png"]

        # Ruta de destino
        ruta_destino = "C:/Users/pgago/Downloads/informe_test.pdf"

        # Llamar a la función real
        generar_pdf_completo(
            id_control=999,
            nombre_usuario="Lucía Hernández",
            rol_usuario="operario",
            tablewidget=tabla,
            imagenes_procesadas=imagenes_procesadas,
            tolerancia_tamano=0.5,
            tolerancia_cantidad=3,
            ruta_destino=ruta_destino,
            logo_path=None,
            parent_widget=None
        )

        self.assertTrue(os.path.exists(ruta_destino))

if __name__ == "__main__":
    unittest.main()
