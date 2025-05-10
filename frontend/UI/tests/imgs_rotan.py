import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSizePolicy, QGraphicsView,
    QGraphicsScene, QVBoxLayout, QFrame
)
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import Qt, QTimer
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
    
    def setPixmap(self, pixmap):
        """Establece un QPixmap directamente"""
        if pixmap.isNull():
            return False
        self.pixmap = pixmap
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
    def __init__(self, image_folder):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("ISLI - Control de Calidad")
        
        self.folder = image_folder
        self.images = self.cargar_imagenes(self.folder)
        self.index = 0
        
        self.reemplazar_qlabels()
        
        # Iniciar el temporizador para cambiar imágenes
        self.timer = QTimer()
        self.timer.timeout.connect(self.mostrar_siguiente_imagen)
        self.timer.start(2000)  # 2000 ms = 2 segundos
        
        # Mostrar la primera imagen
        if self.images:
            self.mostrar_siguiente_imagen()
    
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
    
    def cargar_imagenes(self, folder):
        """Carga la lista de rutas de imágenes válidas en la carpeta"""
        extensiones_validas = ('.png', '.jpg', '.jpeg', '.bmp')
        archivos = [os.path.join(folder, f) for f in os.listdir(folder) 
                   if f.lower().endswith(extensiones_validas)]
        
        if not archivos:
            print(f"⚠️ No se encontraron imágenes en la carpeta: {folder}")
        else:
            print(f"📷 Se encontraron {len(archivos)} imágenes para mostrar")
            
        return archivos
    
    def mostrar_siguiente_imagen(self):
        """Muestra la siguiente imagen en ambos visores"""
        if not self.images:
            print("❌ No hay imágenes para mostrar")
            return
        
        ruta_imagen = self.images[self.index]
        
        # Cargar la imagen en ambos visores
        self.image_view1.setImage(ruta_imagen)
        self.image_view2.setImage(ruta_imagen)
        
        print(f"🔄 Mostrando imagen: {os.path.basename(ruta_imagen)}")
        
        # Avanzar al siguiente índice (con rotación circular)
        self.index = (self.index + 1) % len(self.images)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ruta de la carpeta con imágenes
    image_folder = r"C:\Users\pgago\Desktop\arboles"
    
    window = MainWindow(image_folder)
    window.show()
    
    sys.exit(app.exec())