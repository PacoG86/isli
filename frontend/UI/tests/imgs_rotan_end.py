import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSizePolicy, QGraphicsView,
    QGraphicsScene, QVBoxLayout, QFrame, QGraphicsTextItem
)
from PySide6.QtGui import QPixmap, QImage, QPainter, QFont, QColor, QBrush
from PySide6.QtCore import Qt, QTimer, QRectF
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
        self.text_item = None
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
        
    def showMessage(self, message, bgColor="#2C7873", textColor="#FFFFFF"):
        """Muestra un mensaje en el centro del visor"""
        self.scene.clear()
        
        # Crear un rectángulo que ocupe todo el espacio del visor
        rect = QRectF(0, 0, 600, 400)  # Tamaño base para el rectángulo
        background = self.scene.addRect(rect, brush=QBrush(QColor(bgColor)))
        
        # Añadir texto centrado
        self.text_item = QGraphicsTextItem(message)
        font = QFont("Arial", 14, QFont.Bold)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(textColor))
        
        # Centrar el texto en el rectángulo
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
        
        # Configurar la barra de progreso
        if self.images:
            self.ui.progressBar.setMinimum(0)
            self.ui.progressBar.setMaximum(len(self.images))
            self.ui.progressBar.setValue(0)
        else:
            self.ui.progressBar.setMinimum(0)
            self.ui.progressBar.setMaximum(1)
            self.ui.progressBar.setValue(0)
        
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
            self.mostrar_analisis_completado("No se encontraron imágenes", "#D32F2F")
            return
            
        if self.index >= len(self.images):
            # Ya se han mostrado todas las imágenes
            if not self.analisis_completado:
                self.mostrar_analisis_completado()
            return
        
        ruta_imagen = self.images[self.index]
        
        # Cargar la imagen en ambos visores
        self.image_view1.setImage(ruta_imagen)
        self.image_view2.setImage(ruta_imagen)
        
        # Actualizar las etiquetas de detalles con el nombre de la imagen
        nombre_archivo = os.path.basename(ruta_imagen)
        self.ui.label_5.setText(f"Imagen: {nombre_archivo}")
        self.ui.label_6.setText(f"Imagen: {nombre_archivo}")
        
        # Actualizar la barra de progreso
        self.ui.progressBar.setValue(self.index + 1)
        
        print(f"🔄 Mostrando imagen: {nombre_archivo} ({self.index + 1}/{len(self.images)})")
        
        # Avanzar al siguiente índice (sin rotación circular)
        self.index += 1
        
    def mostrar_analisis_completado(self, mensaje="Análisis Completado", color="#2E7D32"):
        """Muestra un mensaje de análisis completado en ambos visores"""
        if self.analisis_completado:
            return
            
        print("✅ Análisis de imágenes completado")
        
        # Detener el temporizador
        self.timer.stop()
        
        # Mostrar mensaje en ambos visores
        self.image_view1.showMessage(f"{mensaje}\n{len(self.images)} imágenes procesadas", color)
        self.image_view2.showMessage(f"{mensaje}\n{len(self.images)} imágenes procesadas", color)
        
        # Actualizar las etiquetas de detalles
        self.ui.label_5.setText("Análisis finalizado")
        self.ui.label_6.setText("Análisis finalizado")
        
        # Asegurar que la barra de progreso esté al 100%
        if self.images:
            self.ui.progressBar.setValue(len(self.images))
        else:
            self.ui.progressBar.setValue(1)
        
        # Marcar como completado para evitar repetir
        self.analisis_completado = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ruta de la carpeta con imágenes
    image_folder = r"C:\Users\pgago\Desktop\arboles"
    
    window = MainWindow(image_folder)
    window.show()
    
    sys.exit(app.exec())