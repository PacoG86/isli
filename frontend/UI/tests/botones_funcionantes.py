import sys
import os
import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSizePolicy, QGraphicsView,
    QGraphicsScene, QVBoxLayout, QFrame, QGraphicsTextItem,
    QTableWidgetItem, QMessageBox
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
    def __init__(self, base_folder):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("ISLI - Control de Calidad")

        # Directorio base donde se encuentran las subcarpetas
        self.base_folder = base_folder
        
        # Inicializar variables
        self.folder = None  # La carpeta actual seleccionada
        self.images = []
        self.index = 0
        self.analisis_completado = False
        self.timer = None
        
        # Configurar UI
        self.configurar_combobox()
        self.configurar_tabla()
        self.reemplazar_qlabels()
        self.ui.progressBar.setValue(0)
        
        # Conectar señales
        self.ui.pushButton_5.clicked.connect(self.iniciar_control_calidad)  # Botón "Iniciar Control de Calidad"
        self.ui.pushButton_2.clicked.connect(self.limpiar_pantalla)  # Botón "Limpiar pantalla"
        self.ui.pushButton_4.clicked.connect(self.interrumpir_control)  # Botón "Interrumpir control"

    def configurar_combobox(self):
        """Configura el ComboBox con las subcarpetas del directorio base"""
        # Primero limpiar cualquier ítem existente
        self.ui.comboBox.clear()
        
        # Añadir un ítem inicial vacío
        self.ui.comboBox.addItem("-- Seleccione una carpeta --")
        
        # Obtener las subcarpetas y añadirlas al comboBox
        try:
            subcarpetas = [d for d in os.listdir(self.base_folder) 
                          if os.path.isdir(os.path.join(self.base_folder, d))]
            
            # Si hay subcarpetas, añadirlas al comboBox
            if subcarpetas:
                self.ui.comboBox.addItems(subcarpetas)
                print(f"📁 Se encontraron {len(subcarpetas)} carpetas en {self.base_folder}")
            else:
                # Si no hay subcarpetas, añadir el directorio base como opción única
                self.ui.comboBox.addItem(os.path.basename(self.base_folder))
                print(f"📁 No se encontraron subcarpetas. Usando directorio base: {self.base_folder}")
        except Exception as e:
            print(f"❌ Error al cargar subcarpetas: {e}")
            QMessageBox.warning(self, "Error", f"No se pudo acceder al directorio: {self.base_folder}\n{str(e)}")

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
        
        # Mostrar mensaje inicial en los visores
        self.image_view1.showMessage("Seleccione una carpeta\ny haga clic en\nIniciar Control de Calidad", "#2C7873")
        self.image_view2.showMessage("Seleccione una carpeta\ny haga clic en\nIniciar Control de Calidad", "#2C7873")

    def cargar_imagenes(self, folder):
        """Carga la lista de rutas de imágenes válidas en la carpeta"""
        extensiones = (".png", ".jpg", ".jpeg", ".bmp")
        try:
            archivos = [os.path.join(folder, f) for f in os.listdir(folder) 
                       if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(extensiones)]
            
            if not archivos:
                print(f"⚠️ No se encontraron imágenes en la carpeta: {folder}")
                QMessageBox.information(self, "Información", f"No se encontraron imágenes en la carpeta: {os.path.basename(folder)}")
            else:
                print(f"📷 Se encontraron {len(archivos)} imágenes para mostrar")
                
            return archivos
        except Exception as e:
            print(f"❌ Error al cargar imágenes: {e}")
            QMessageBox.warning(self, "Error", f"Error al cargar imágenes: {str(e)}")
            return []

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
        
        # Desplazarse a la última fila
        self.ui.tableWidget.scrollToBottom()

    def iniciar_control_calidad(self):
        """Inicia el proceso de control de calidad con la carpeta seleccionada"""
        # Detener cualquier control previo
        self.interrumpir_control()
        
        # Obtener la carpeta seleccionada
        seleccion = self.ui.comboBox.currentText()
        
        # Verificar si se ha seleccionado una carpeta válida
        if seleccion == "-- Seleccione una carpeta --":
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione una carpeta primero.")
            return
        
        # Determinar la ruta completa de la carpeta seleccionada
        if seleccion == os.path.basename(self.base_folder):
            self.folder = self.base_folder
        else:
            self.folder = os.path.join(self.base_folder, seleccion)
        
        # Cargar imágenes de la carpeta seleccionada
        self.images = self.cargar_imagenes(self.folder)
        
        # Resetear variables de control
        self.index = 0
        self.analisis_completado = False
        
        # Limpiar la tabla y restablecer la barra de progreso
        self.ui.tableWidget.setRowCount(0)
        if self.images:
            self.ui.progressBar.setMaximum(len(self.images))
        else:
            self.ui.progressBar.setMaximum(1)
        self.ui.progressBar.setValue(0)
        
        # Mostrar mensaje si no hay imágenes
        if not self.images:
            self.image_view1.showMessage("No se encontraron\nimágenes en la carpeta", "#D32F2F")
            self.image_view2.showMessage("No se encontraron\nimágenes en la carpeta", "#D32F2F")
            self.ui.label_5.setText("Sin imágenes")
            self.ui.label_6.setText("Sin imágenes")
            return
            
        # Iniciar el temporizador para mostrar imágenes
        self.timer = QTimer()
        self.timer.timeout.connect(self.mostrar_siguiente_imagen)
        self.timer.start(2000)  # 2000 ms = 2 segundos
        
        # Mostrar la primera imagen inmediatamente
        self.mostrar_siguiente_imagen()

    def limpiar_pantalla(self):
        """Limpia los visores de imágenes y detiene cualquier procesamiento"""
        self.interrumpir_control()
        
        # Limpiar visores
        self.image_view1.showMessage("Pantalla limpiada", "#2C7873")
        self.image_view2.showMessage("Pantalla limpiada", "#2C7873")
        
        # Restablecer etiquetas y barra de progreso
        self.ui.label_5.setText("Detalles imagen")
        self.ui.label_6.setText("Detalles imagen")
        self.ui.progressBar.setValue(0)
        
        # Opcional: limpiar la tabla
        self.ui.tableWidget.setRowCount(0)

    def interrumpir_control(self):
        """Detiene el proceso de control de calidad"""
        if self.timer and self.timer.isActive():
            self.timer.stop()
            print("⏹️ Control de calidad interrumpido")
            
            # Mostrar mensaje de interrupción si no estaba completado
            if not self.analisis_completado and self.images:
                self.image_view1.showMessage("Control interrumpido", "#F57C00")
                self.image_view2.showMessage("Control interrumpido", "#F57C00")
                self.ui.label_5.setText("Control interrumpido")
                self.ui.label_6.setText("Control interrumpido")

    def mostrar_siguiente_imagen(self):
        if not self.images or self.index >= len(self.images):
            if not self.analisis_completado and self.images:
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
        
        print(f"🔄 Mostrando imagen: {nombre} ({self.index + 1}/{len(self.images)})")
        self.index += 1

    def mostrar_analisis_completado(self, mensaje="Análisis completado", color="#2E7D32"):
        if self.analisis_completado:
            return
        
        print("✅ Análisis de imágenes completado")
        
        if self.timer and self.timer.isActive():
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
        
        # Agregar una fila de resumen a la tabla
        if self.images:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fila_actual = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(fila_actual)
            
            self.ui.tableWidget.setItem(fila_actual, 0, QTableWidgetItem(timestamp))
            self.ui.tableWidget.setItem(fila_actual, 1, QTableWidgetItem("RESUMEN"))
            self.ui.tableWidget.setItem(fila_actual, 2, QTableWidgetItem(f"Total: {len(self.images)} imágenes"))
            
            # Hacer la fila de resumen destacada (fondo verde claro)
            for col in range(3):
                item = self.ui.tableWidget.item(fila_actual, col)
                item.setBackground(QBrush(QColor("#C8E6C9")))
                item.setFont(QFont("Arial", 10, QFont.Bold))
            
            self.ui.tableWidget.scrollToBottom()
        
        self.analisis_completado = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Directorio base donde se encuentran las subcarpetas con imágenes
    base_folder = r"C:\Users\pgago\Desktop\arboles"
    
    ventana = MainWindow(base_folder)
    ventana.show()
    
    sys.exit(app.exec())