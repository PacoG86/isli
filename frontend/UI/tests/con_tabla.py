import sys
import os
import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSizePolicy, QGraphicsView,
    QGraphicsScene, QVBoxLayout, QFrame, QGraphicsTextItem,
    QTableWidgetItem
)
from PySide6.QtGui import QPixmap, QImage, QPainter, QFont, QColor, QBrush
from PySide6.QtCore import Qt, QTimer, QRectF
from UI.menu_principal_v2 import Ui_MainWindow


class HighQualityImageView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_item = None
        self.text_item = None
        self.pixmap = None

    def setImage(self, image_path):
        image = QImage(image_path)
        if image.isNull():
            print(f"❌ Error: no se pudo cargar la imagen desde {image_path}")
            return False
        self.pixmap = QPixmap.fromImage(image)
        self.updateImage()
        return True

    def updateImage(self):
        if not self.pixmap or self.pixmap.isNull():
            return
        self.scene.clear()
        self.image_item = self.scene.addPixmap(self.pixmap)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def showMessage(self, message, bgColor="#2C7873", textColor="#FFFFFF"):
        self.scene.clear()
        rect = QRectF(0, 0, 300, 200)
        self.scene.addRect(rect, brush=QBrush(QColor(bgColor)))
        self.text_item = QGraphicsTextItem(message)
        font = QFont("Arial", 14, QFont.Bold)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(textColor))
        text_width = self.text_item.boundingRect().width()
        text_height = self.text_item.boundingRect().height()
        self.text_item.setPos((rect.width() - text_width) / 2, (rect.height() - text_height) / 2)
        self.scene.addItem(self.text_item)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene and not self.scene.itemsBoundingRect().isNull():
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


class MainWindow(QMainWindow):
    def __init__(self, image_folder):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("ISLI - Control de Calidad")

        self.folder = image_folder
        self.images = self.cargar_imagenes(self.folder)
        self.index = 0
        self.analisis_completado = False

        if self.images:
            self.ui.progressBar.setMaximum(len(self.images))
        else:
            self.ui.progressBar.setMaximum(1)
        self.ui.progressBar.setValue(0)

        self.configurar_tabla()
        self.reemplazar_qlabels()

        self.timer = QTimer()
        self.timer.timeout.connect(self.mostrar_siguiente_imagen)
        self.timer.start(2000)

        if self.images:
            self.mostrar_siguiente_imagen()

    def reemplazar_qlabels(self):
        layout = self.ui.frame_3.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.image_view1 = HighQualityImageView()
        self.image_view2 = HighQualityImageView()
        layout.addWidget(self.image_view1)
        layout.addWidget(self.image_view2)

    def cargar_imagenes(self, folder):
        extensiones = (".png", ".jpg", ".jpeg", ".bmp")
        return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(extensiones)]

    def configurar_tabla(self):
        self.ui.tableWidget.setHorizontalHeaderLabels(["Fecha/Hora", "Carpeta", "Imagen"])
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.Stretch)
        self.ui.tableWidget.setRowCount(0)

    def agregar_registro_a_tabla(self, ruta_imagen):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        carpeta = os.path.basename(os.path.dirname(ruta_imagen))
        archivo = os.path.basename(ruta_imagen)

        fila = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(fila)
        self.ui.tableWidget.setItem(fila, 0, QTableWidgetItem(timestamp))
        self.ui.tableWidget.setItem(fila, 1, QTableWidgetItem(carpeta))
        self.ui.tableWidget.setItem(fila, 2, QTableWidgetItem(archivo))

    def mostrar_siguiente_imagen(self):
        if self.index >= len(self.images):
            if not self.analisis_completado:
                self.mostrar_analisis_completado()
            return

        ruta_imagen = self.images[self.index]
        self.image_view1.setImage(ruta_imagen)
        self.image_view2.setImage(ruta_imagen)

        nombre = os.path.basename(ruta_imagen)
        self.ui.label_5.setText(f"Imagen: {nombre}")
        self.ui.label_6.setText(f"Imagen: {nombre}")

        self.ui.progressBar.setValue(self.index + 1)
        self.agregar_registro_a_tabla(ruta_imagen)
        self.index += 1

    def mostrar_analisis_completado(self, mensaje="Análisis completado", color="#2E7D32"):
        if self.analisis_completado:
            return
        self.timer.stop()
        self.image_view1.showMessage(f"{mensaje}", color)
        self.image_view2.showMessage(f"{mensaje}", color)
        self.ui.label_5.setText("Análisis finalizado")
        self.ui.label_6.setText("Análisis finalizado")
        self.ui.progressBar.setValue(len(self.images))
        self.analisis_completado = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    carpeta = r"C:\Users\pgago\Desktop\arboles"
    ventana = MainWindow(carpeta)
    ventana.show()
    sys.exit(app.exec())
