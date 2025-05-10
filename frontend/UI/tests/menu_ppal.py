import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSizePolicy, QGraphicsView,
    QGraphicsScene, QVBoxLayout, QFrame
)
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import Qt
from UI.menu_principal_v2 import Ui_MainWindow  # Asegúrate que este .py esté generado y actualizado


class HighQualityImageView(QGraphicsView):
    """Visor personalizado de imágenes con calidad escalada y suavizada."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Mejor calidad de renderizado
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)

        # Configuraciones visuales
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.image_item = None
        self.pixmap = None

    def setImage(self, image_path):
        """Carga una imagen desde el disco y la muestra"""
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene and not self.scene.itemsBoundingRect().isNull():
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("ISLI - Control de Calidad")

        self.image_path = r"C:\Users\pgago\Downloads\arbol_etiquetado.png"

        self.reemplazar_qlabels()
        self.cargar_imagenes()

    def reemplazar_qlabels(self):
        """Elimina los QGraphicsView originales y coloca los personalizados."""
        layout = self.ui.frame_3.layout()

        # Eliminar widgets existentes
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Crear visores personalizados
        self.image_view1 = HighQualityImageView()
        self.image_view2 = HighQualityImageView()

        # Añadir visores al layout
        layout.addWidget(self.image_view1)
        layout.addWidget(self.image_view2)

    def cargar_imagenes(self):
        """Carga la imagen en ambos visores."""
        self.image_view1.setImage(self.image_path)
        self.image_view2.setImage(self.image_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
