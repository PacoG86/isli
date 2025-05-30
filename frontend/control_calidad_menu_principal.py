"""Ventana principal del sistema ISLI para el control de calidad de rollos industriales.

Permite al operario seleccionar rollos, ejecutar el análisis por visión artificial,
visualizar resultados procesados, registrar datos en backend y generar informes PDF.
"""
import sys
import os
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
import requests
from PySide6.QtWidgets import (
    QMainWindow, QSizePolicy, QGraphicsView,
    QGraphicsScene, QFrame, QGraphicsTextItem,
    QTableWidgetItem, QMessageBox, QFileDialog, QProgressDialog
)
from PySide6.QtGui import QPixmap, QImage, QPainter, QFont, QColor, QBrush, QIcon
from PySide6.QtCore import Qt, QTimer, QRectF, QEvent
from UI.menu_principal_v2 import Ui_MainWindow
from reportlab.lib.pagesizes import A4
from utils_ui import mostrar_datos_usuario, configurar_botones_comunes, mostrar_siguiente_id_control, obtener_ruta_informes, guardar_config_ruta
from historico_controles_app import HistoricoControlesWindow
from utils_informes import generar_pdf_completo, guardar_registro_informe
from analisis_defectos.procesador_rollos import analizar_rollo


class HighQualityImageView(QGraphicsView):
    """
    Visor de imágenes personalizado con capacidad para mostrar mensajes
    centrados sobre un fondo coloreado, además de imágenes procesadas con alta calidad.
    """
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
        self.current_message = ""
        self.current_bg_color = "#2C7873"
        self.current_text_color = "#FFFFFF"
        self.is_showing_message = False

    def setImage(self, image_path):
        image = QImage(image_path)
        if image.isNull():
            print(f"\u274c Error: no se pudo cargar la imagen desde {image_path}")
            return False
        self.pixmap = QPixmap.fromImage(image)
        self.is_showing_message = False
        self.updateImage()
        return True

    def updateImage(self):
        if not self.pixmap or self.pixmap.isNull():
            return
        self.scene.clear()
        self.image_item = self.scene.addPixmap(self.pixmap)
        # Usamos el tamaño real de la imagen como rectángulo de escena
        self.scene.setSceneRect(self.image_item.boundingRect())
        # Ajustamos la vista respetando proporción
        self.fitInView(self.image_item, Qt.KeepAspectRatio)
        self.text_item = None

    def showMessage(self, message, bgColor="#2C7873", textColor="#FFFFFF"):
        self.scene.clear()
        self.image_item = None
        self.is_showing_message = True
        self.current_message = message
        self.current_bg_color = bgColor
        self.current_text_color = textColor
        
        self._updateMessageDisplay()

    def _updateMessageDisplay(self):
        if not self.is_showing_message:
            return
            
        # Obtener el tamaño actual de la vista
        view_width = max(1, self.viewport().width())
        view_height = max(1, self.viewport().height())
        
        # Actualizar el rectángulo de la escena
        self.scene.clear()
        self.scene.setSceneRect(0, 0, view_width, view_height)
        
        # Fondo del visor completo
        rect = QRectF(0, 0, view_width, view_height)
        self.scene.addRect(rect, brush=QBrush(QColor(self.current_bg_color)))
        
        # Texto proporcional, ajustamos el tamaño de la fuente según las dimensiones actuales
        font_size = max(10, int(min(view_width, view_height) * 0.08))
        font = QFont("Arial", font_size, QFont.Bold)
        
        self.text_item = QGraphicsTextItem(self.current_message)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(self.current_text_color))
        self.scene.addItem(self.text_item)
        
        # Centrar texto
        text_rect = self.text_item.boundingRect()
        x = (view_width - text_rect.width()) / 2
        y = (view_height - text_rect.height()) / 2
        self.text_item.setPos(x, y)
        
        # Ajustar la vista al contenido
        self.fitInView(self.scene.sceneRect(), Qt.IgnoreAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        if self.is_showing_message:
            # Si estamos mostrando un mensaje, actualizamos su display
            self._updateMessageDisplay()
        elif self.image_item:
            # Si estamos mostrando una imagen, la ajustamos
            self.fitInView(self.image_item, Qt.KeepAspectRatio)


class MainWindow(QMainWindow):
    """
    Ventana principal del sistema ISLI.

    Controla todo el flujo de control de calidad: selección de rollo, análisis de imágenes,
    visualización gráfica, tabla de resultados y generación de informes.
    """
    def __init__(self, base_folder, nombre_usuario, rol_usuario, token_jwt, id_usuario):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        ruta_icono = os.path.join(os.path.dirname(__file__), "..", "logo_isli.png")
        ruta_icono = os.path.abspath(ruta_icono)
        icon = QIcon(ruta_icono)
        self.setWindowIcon(icon)
        self.showMaximized()
        self.setWindowTitle("ISLI - Control de Calidad")
        self.setupUiConnections()

        self.nombre_usuario = nombre_usuario
        self.rol_usuario = rol_usuario
        self.token_jwt = token_jwt
        self.id_usuario = id_usuario
        mostrar_datos_usuario(self.ui, nombre_usuario, rol_usuario)
        configurar_botones_comunes(self, self.ui, self.rol_usuario, self.token_jwt)

        self.ui.comboBox.installEventFilter(self)
        self.ui.spinBox.valueChanged.connect(self.configurar_combobox)
        
        # Diferir carga pesada tras mostrar la interfaz
        QTimer.singleShot(100, self.cargar_datos_iniciales)

        # Directorio base donde se encuentran las subcarpetas
        self.base_folder = base_folder
        
        # Inicializar variables
        self.folder = None  # Directorio actual seleccionado
        self.images = []
        self.index = 0
        self.analisis_completado = False
        self.timer = None
        
        # Temporizador para parpadeo del botón
        self.blink_timer = QTimer()
        self.blink_state = False
        self.blink_timer.timeout.connect(self.parpadear_boton)
        
        # Guardar el color original del botón
        self.boton_color_original = self.ui.pushButton_5.styleSheet()
        
        # Configurar UI
        self.configurar_tabla()
        self.remplazar_visores()
        self.ui.progressBar.setValue(0)
        
        # Conectar señales
        self.ui.pushButton_5.clicked.connect(self.iniciar_control_calidad)  # Botón "Iniciar Control de Calidad"
        self.ui.pushButton_2.clicked.connect(self.limpiar_pantalla)  # Botón "Limpiar pantalla"
        self.ui.pushButton_4.clicked.connect(self.confirmar_interrumpir)  # Botón "Interrumpir control"
        self.ui.pushButton_8.clicked.connect(self.guardar_resultados)
        self.ui.pushButton_historico.clicked.connect(self.abrir_ventana_historico)
        self.ui.pushButton_gAlmacen.clicked.connect(self.seleccionar_ruta_almacen)

        self.ui.pushButton_5.setEnabled(False)  # Desabilita botón 'Iniciar Control de Calidad' al arrancar la app
        self.prompt_reiniciar_on_start()

    def abrir_ventana_historico(self):
        progress = QProgressDialog("Cargando historial...", None, 0, 0, self)
        progress.setWindowTitle("ISLI - Controles")
        progress.setWindowModality(Qt.ApplicationModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.setAutoClose(True)
        progress.show()

        QTimer.singleShot(100, lambda: self._mostrar_ventana_historico(progress))

    def _mostrar_ventana_historico(self, progress_dialog):
        self.hide()
        self.historial_window = HistoricoControlesWindow(
            self.nombre_usuario,
            self.rol_usuario,
            self.token_jwt,
            self.id_usuario
        )
        self.historial_window.show()
        progress_dialog.close()

    def cargar_datos_iniciales(self):
        mostrar_siguiente_id_control(self.ui)
        self.configurar_combobox()
        self.image_view1.showMessage("Reinicia el sistema antes\nIniciar Control de Calidad", "#2C7873", textColor= '#FBC02D')
        self.image_view2.showMessage("Selecciona una carpeta\ny haz clic en\nIniciar Control de Calidad", "#2C7873")

    def configurar_combobox(self):
        """Configura el ComboBox con las subcarpetas del directorio base, filtrando por el número máximo de imágenes"""
        self.ui.comboBox.blockSignals(True)
        self.ui.comboBox.clear()
        
        try:
            max_imgs = self.ui.spinBox.value()
            if max_imgs <= 0:
                self.ui.comboBox.addItem("-- No hay rollos que cumplan con el umbral indicado --")
                print("El valor del spinBox es 0, no se cargarán carpetas.")
                return
            
            self.ui.comboBox.addItem("-- Seleccione un rollo --")

            subcarpetas = [
                d for d in os.listdir(self.base_folder)
                if os.path.isdir(os.path.join(self.base_folder, d))
            ]

            carpetas_validas = []
            for carpeta in subcarpetas:
                ruta = os.path.join(self.base_folder, carpeta)
                num_imgs = len([
                    f for f in os.listdir(ruta)
                    if os.path.isfile(os.path.join(ruta, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
                ])
                if num_imgs <= max_imgs:
                    carpetas_validas.append(carpeta)

            if carpetas_validas:
                self.ui.comboBox.addItems(carpetas_validas)
                print(f"Cargadas {len(carpetas_validas)} carpetas con ≤ {max_imgs} imágenes")
            else:
                self.ui.comboBox.addItem("-- No hay rollos que cumplan con el umbral indicado --")
                print("No se encontraron carpetas que cumplan con el criterio.")
        except Exception as e:
            print(f"Error al cargar subcarpetas: {e}")
            QMessageBox.warning(self, "Error", f"No se pudo acceder al directorio: {self.base_folder}\n{str(e)}")

        self.ui.comboBox.blockSignals(False)

    def eventFilter(self, obj, event):
        if obj == self.ui.comboBox and event.type() == QEvent.MouseButtonPress:
            self.configurar_combobox()
        return super().eventFilter(obj, event)

    def remplazar_visores(self): # Reemplaza los visores de imágenes por instancias de HighQualityImageView
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
                print(f"No se encontraron imágenes en la carpeta: {folder}")
                QMessageBox.information(self, "Información", f"No se encontraron imágenes en la carpeta: {os.path.basename(folder)}")
            else:
                print(f"Se encontraron {len(archivos)} imágenes para mostrar")
                
            return archivos
        except Exception as e:
            print(f"Error al cargar imágenes: {e}")
            QMessageBox.warning(self, "Error", f"Error al cargar imágenes: {str(e)}")
            return []

    def configurar_tabla(self):
        self.ui.tableWidget.setHorizontalHeaderLabels([
        "Fecha/ Hora", "Tipo Defecto", "REF Defecto Img", "Mayor Defecto mm2", "Resultado",  "Min_defecto"
        ])

        self.ui.tableWidget.setColumnHidden(5, True)
    
        header = self.ui.tableWidget.horizontalHeader()
        for col in range(5):
            header.setSectionResizeMode(col, header.ResizeMode.Stretch)  # que todas se estiren por igual

        self.ui.tableWidget.setRowCount(0)

    def agregar_registro_a_tabla(self, ruta_imagen_original, ruta_imagen_procesada):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        carpeta = os.path.basename(os.path.dirname(ruta_imagen_original))  # ID Rollo
        archivo = os.path.basename(ruta_imagen_original)                  # Ref. Img Defecto

        # Leer el mayor defecto desde el .txt de la imagen procesada
        _, dim_defecto, _ = self.leer_defectos_txt(ruta_imagen_procesada)
        dim_defecto = dim_defecto if dim_defecto is not None else 0.0

        umbral_usuario = float(self.ui.doubleSpinBox.value())
        result_analisis = "nok" if dim_defecto > umbral_usuario else "ok"
        minimo, maximo, _ = self.leer_defectos_txt(ruta_imagen_procesada)

        fila = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(fila)

        self.ui.tableWidget.setItem(fila, 0, QTableWidgetItem(timestamp))
        tipos = self.leer_tipos_defecto_json(ruta_imagen_procesada)
        tipos_str = ", ".join(tipos) if tipos else "—"
        self.ui.tableWidget.setItem(fila, 1, QTableWidgetItem(tipos_str))
        self.ui.tableWidget.setItem(fila, 2, QTableWidgetItem(archivo))

        item_dim = QTableWidgetItem(f"{dim_defecto:.2f}")
        item_result = QTableWidgetItem(result_analisis)

        # Estilo condicional: rojo para NOK, verde para OK
        if result_analisis == "nok":
            item_dim.setBackground(QColor("#FFCDD2"))      # rojo claro
            item_result.setBackground(QColor("#FFCDD2"))
        else:
            item_dim.setBackground(QColor("#C8E6C9"))      # verde claro
            item_result.setBackground(QColor("#C8E6C9"))

        self.ui.tableWidget.setItem(fila, 3, item_dim)
        self.ui.tableWidget.setItem(fila, 4, item_result)
        item_min = QTableWidgetItem(f"{minimo:.2f}" if minimo is not None else "0.00")
        self.ui.tableWidget.setItem(fila, 5, item_min)  # columna oculta

        # Desplazarse a la última fila
        self.ui.tableWidget.scrollToBottom()


    def parpadear_boton(self):
        """Controla el parpadeo del botón de iniciar control"""
        if self.blink_state:
            self.ui.pushButton_5.setStyleSheet("background-color: #1976D2; color: white;")
        else:
            self.ui.pushButton_5.setStyleSheet("background-color: #64B5F6; color: white;")
        self.blink_state = not self.blink_state

    def iniciar_control_calidad(self):
        """
        Ejecuta el análisis de defectos sobre las imágenes del rollo seleccionado.

        Procesa las imágenes mediante la función `analizar_rollo`,
        carga las imágenes originales/procesadas, y lanza la visualización secuencial.
        """
        if self.timer and self.timer.isActive():
            self.interrumpir_control()
            return

        seleccion = self.ui.comboBox.currentText()

        if seleccion == "-- Seleccione un rollo --":
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione una carpeta primero.")
            return

        self.folder = os.path.join(self.base_folder, seleccion)
        umbral_usuario = float(self.ui.doubleSpinBox.value())
        self.ui.label_contador.setText("📊 0 / {}".format(len(self.images)))

        # Ejecutar el análisis de imágenes antes de cargarlas
        try:
            analizar_rollo(base_path=self.base_folder, rollo=seleccion, area_umbral=umbral_usuario)
        except Exception as e:
            print(f"Error al analizar el rollo: {e}")
            QMessageBox.critical(self, "Error", f"Ocurrió un error al analizar el rollo seleccionado:\n{e}")
            return

        # Cargar imágenes desde 'originales' y 'procesado'
        carpeta_originales = os.path.join(self.folder, "originales")
        carpeta_procesadas = os.path.join(self.folder, "procesado")
        self.imagenes_originales = self.cargar_imagenes(carpeta_originales)
        self.imagenes_procesadas = self.cargar_imagenes(carpeta_procesadas)

        # Validar que ambos conjuntos estén sincronizados
        if len(self.imagenes_originales) != len(self.imagenes_procesadas):
            QMessageBox.warning(self, "Advertencia", "El número de imágenes originales y procesadas no coincide.")
            return

        self.images = list(zip(self.imagenes_originales, self.imagenes_procesadas))
        self.index = 0
        self.imagenes_procesadas = []  # Limpiar acumulación previa
        self.analisis_completado = False

        self.ui.tableWidget.setRowCount(0)
        self.ui.progressBar.setMaximum(len(self.images) if self.images else 1)
        self.ui.progressBar.setValue(0)

        if not self.images:
            self.image_view1.showMessage("No se encontraron\nimágenes en la carpeta", "#D32F2F")
            self.image_view2.showMessage("No se encontraron\nimágenes en la carpeta", "#D32F2F")
            self.ui.label_5.setText("Sin imágenes")
            self.ui.label_6.setText("Sin imágenes")
            return

        self.timer = QTimer()
        self.timer.timeout.connect(self.mostrar_siguiente_imagen)
        self.timer.start(2000)

        self.blink_timer.start(500)
        self.mostrar_siguiente_imagen()


    def limpiar_pantalla(self):
        """Limpia los visores de imágenes y detiene cualquier procesamiento"""
        self.interrumpir_control()
        
        # Limpiar visores
        self.image_view1.showMessage("Sistema reiniciado", "#2C7873")
        self.image_view2.showMessage("Sistema listo para\npróximo Control de Calidad", "#2C7873")
        
        # Restablecer etiquetas y barra de progreso
        self.ui.label_5.setText("Detalles imagen")
        self.ui.label_6.setText("Detalles imagen")
        self.ui.progressBar.setValue(0)
        
        # Limpiar la tabla
        self.ui.tableWidget.setRowCount(0)

        # Restablecer valores de los spinboxes
        self.ui.spinBox.setValue(0)
        self.ui.doubleSpinBox.setValue(0.00)

        # Revertir todas las carpetas de rollos al estado original
        for carpeta in os.listdir(self.base_folder):
            ruta_rollo = os.path.join(self.base_folder, carpeta)
            if not os.path.isdir(ruta_rollo):
                continue

            ruta_originales = os.path.join(ruta_rollo, "originales")
            ruta_procesado = os.path.join(ruta_rollo, "procesado")

            # Solo actuar si existen ambas carpetas
            if os.path.exists(ruta_originales) and os.path.exists(ruta_procesado):
                try:
                    # Mover imágenes desde 'originales/' a la raíz
                    for archivo in os.listdir(ruta_originales):
                        origen = os.path.join(ruta_originales, archivo)
                        destino = os.path.join(ruta_rollo, archivo)
                        shutil.move(origen, destino)

                    # Borrar carpetas originales y procesado
                    shutil.rmtree(ruta_originales)
                    shutil.rmtree(ruta_procesado)
                    print(f"Rollo restaurado: {carpeta}")
                except Exception as e:
                    print(f"Error al restaurar {carpeta}: {e}")

        self.ui.pushButton_5.setEnabled(True)  # Enable 'Iniciar Control de Calidad' after reinicio

    def confirmar_interrumpir(self):
        """Muestra diálogo de confirmación antes de interrumpir el control"""
        if not self.timer or not self.timer.isActive():
            return  # No hay control activo que interrumpir

        self.timer.stop()
        self.blink_timer.stop()
        self.ui.pushButton_5.setStyleSheet("")

        respuesta = QMessageBox.question(
            self,
            "Confirmar interrupción",
            "¿Desea interrumpir el control de calidad?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            # Mostrar mensaje en visores
            if not self.analisis_completado and self.images:
                self.image_view1.showMessage("Control cancelado", "#F57C00")
                self.image_view2.showMessage("Control cancelado", "#F57C00")
                self.ui.label_5.setText("Control cancelado")
                self.ui.label_6.setText("Control cancelado")
            # Restaurar estilo del botón
            self.ui.pushButton_5.setText("Iniciar Control de Calidad")
            self.ui.pushButton_5.setStyleSheet("")
            self.timer = None
        else:
            self.timer.start(2000)
            self.blink_timer.start(500)

    def interrumpir_control(self):
        """Detiene el proceso de control de calidad"""
        if self.timer and self.timer.isActive():
            self.timer.stop()
            print("Control de calidad interrumpido")
            
            # Detener parpadeo del botón y restaurar estilo original
            self.blink_timer.stop()
            self.ui.pushButton_5.setStyleSheet("")  # Restaurar estilo original
            
            # Mostrar mensaje de interrupción si no estaba completado
            if not self.analisis_completado and self.images:
                self.image_view1.showMessage("Control cancelado", "#F57C00")
                self.image_view2.showMessage("Control cancelado", "#F57C00")
                self.ui.label_5.setText("Control cancelado")
                self.ui.label_6.setText("Control cancelado")
                
            # Restaurar el texto del botón
            self.ui.pushButton_5.setText("Iniciar Control de Calidad")

    def mostrar_siguiente_imagen(self):
        if not self.images or self.index >= len(self.images):
            if not self.analisis_completado and self.images:
                self.mostrar_analisis_completado()
            return

        ruta_original, ruta_procesada = self.images[self.index]
        self.image_view1.setImage(ruta_original)     # Visor izquierdo: original
        self.image_view2.setImage(ruta_procesada)    # Visor derecho: procesada

        if not hasattr(self, 'imagenes_procesadas'):
            self.imagenes_procesadas = []
        self.imagenes_procesadas.append(ruta_procesada)

        nombre = os.path.basename(ruta_original)

        minimo, maximo, _ = self.leer_defectos_txt(ruta_procesada)
        if minimo is not None and maximo is not None:
            self.ui.label_5.setText(f"Rango de defectos: {minimo:.2f} - {maximo:.2f} mm")
        else:
            self.ui.label_5.setText("Rango de defectos: -- mm")

        self.ui.label_6.setText(f"Imagen: {nombre}")
        self.ui.progressBar.setValue(self.index + 1)
        self.ui.label_contador.setText(f"📊 {self.index + 1} / {len(self.images)}")
        self.agregar_registro_a_tabla(ruta_original, ruta_procesada)

        print(f"Mostrando imagen: {nombre} ({self.index + 1}/{len(self.images)})")
        self.index += 1


    def _agregar_imagenes_procesadas_a_pdf(self, c, width, height):
        y = height - 80
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "Imágenes Analizadas")
        y -= 20

        for img_path in getattr(self, 'imagenes_procesadas', [])[:6]:
            if y < 120:
                c.showPage()
                y = height - 50
            if os.path.exists(img_path):
                try:
                    c.drawImage(img_path, 40, y - 100, width=200, height=100)
                    c.drawString(250, y - 60, os.path.basename(img_path))
                    y -= 120
                except Exception as e:
                    print(f"Error al insertar imagen en PDF: {e}")


    def leer_defectos_txt(self, ruta_imagen_procesada):
        """
        Lee el archivo .txt correspondiente a una imagen procesada.
        Devuelve:
        - área mínima
        - área máxima
        - lista completa de áreas
        """
        try:
            txt_path = ruta_imagen_procesada + ".txt"
            if not os.path.exists(txt_path):
                return None, None, []

            areas = []
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    partes = line.strip().split()
                    if len(partes) == 2 and partes[1].endswith("mm2"):
                        valor = float(partes[1].replace("mm2", ""))
                        areas.append(valor)

            if not areas:
                return None, None, []

            return min(areas), max(areas), areas
        except Exception as e:
            print(f"Error al leer defectos desde TXT: {e}")
            return None, None, []
        
    def leer_tipos_defecto_json(self, ruta_imagen_procesada):
        """Lee el archivo .json generado por procesador_rollos.py y devuelve la lista de tipos de defecto"""
        json_path = ruta_imagen_procesada + ".json"
        if not os.path.exists(json_path):
            return []

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("tipos", [])
        except Exception as e:
            print(f"Error leyendo tipos de defecto desde JSON: {e}")
            return []


    def guardar_resultados(self):
        """
        Compila los resultados mostrados en la tabla y los envía al backend.

        Incluye:
        - metadatos del control
        - lista de imágenes y defectos
        - cálculo del resultado global (ok/nok)
        """
        if not self.analisis_completado:
            QMessageBox.warning(self, "Advertencia", "No se ha completado ningún análisis para guardar.")
            return

        try:
            # Extraer valores del formulario
            umbral = float(self.ui.doubleSpinBox.value())
            max_defectos = int(self.ui.spinBox.value())
            num_defectos_en_rollo = len(self.images)  # Número total de imágenes cargadas
            timestamp_actual = datetime.now().isoformat()
            ruta_rollo = self.folder  # Carpeta actual seleccionada
            nombre_rollo = os.path.basename(ruta_rollo).strip().lower()
            print(f"nombre_rollo enviado desde frontend: '{nombre_rollo}'")
            orden_analisis = 1
            print(f"Ruta enviada como rollo: {ruta_rollo}")
            try:
                resp_orden = requests.get("http://localhost:8000/controles/rollo/orden_analisis", params={"nombre_rollo": nombre_rollo})
                if resp_orden.status_code == 200:
                    orden_analisis = resp_orden.json().get("siguiente_orden", 1)
            except Exception as e:
                print(f"No se pudo obtener orden de análisis: {e}")

            # Compilar estructura del payload
            data = {
                "id_usuario": self.id_usuario,
                "umbral_tamano_defecto": umbral,
                "num_defectos_tolerables_por_tamano": max_defectos,
                "fecha_control": timestamp_actual,
                "rollo": {
                    "ruta_local_rollo": ruta_rollo,
                    "nombre_rollo": nombre_rollo,
                    "num_defectos_rollo": num_defectos_en_rollo,
                    "total_defectos_intolerables_rollo": 0,  # Se calcula más abajo
                    "resultado_rollo": "ok",  # Se modificará si se detectan defectos no tolerables
                    "orden_analisis": orden_analisis  # O el número correspondiente si haces múltiples controles por sesión
                },
                "imagenes": []
            }

            defectos_intolerables = 0

            for row in range(self.ui.tableWidget.rowCount()):
                if self.ui.tableWidget.item(row, 1).text() == "RESUMEN":
                    continue

                nombre_archivo = self.ui.tableWidget.item(row, 2).text()
                max_defecto = float(self.ui.tableWidget.item(row, 3).text())
                clasificacion = self.ui.tableWidget.item(row, 4).text().lower()
                tipo_defecto = self.ui.tableWidget.item(row, 1).text().strip()

                min_defecto = 0.0
                min_item = self.ui.tableWidget.item(row, 5)
                if min_item and min_item.text().replace('.', '', 1).isdigit():
                    try:
                        min_defecto = float(min_item.text())
                    except ValueError:
                        pass

                if clasificacion == "nok":
                    defectos_intolerables += 1

                data["imagenes"].append({
                    "nombre_archivo": nombre_archivo,
                    "fecha_captura": timestamp_actual,
                    "max_dim_defecto_medido": max_defecto,
                    "min_dim_defecto_medido": min_defecto,
                    "clasificacion": clasificacion,
                    "defectos": [
                        {"area": min_defecto, "tipo_valor": "min", "tipo_defecto": tipo_defecto},
                        {"area": max_defecto, "tipo_valor": "max", "tipo_defecto": tipo_defecto}
                    ]
                })

            # Ajustar total de defectos intolerables y resultado del rollo
            data["rollo"]["total_defectos_intolerables_rollo"] = defectos_intolerables
            data["rollo"]["resultado_rollo"] = "nok" if defectos_intolerables > 0 else "ok"

            response = requests.post("http://localhost:8000/controles/nuevo", json=data)

            if response.status_code == 200:
                QMessageBox.information(self, "Éxito", "Resultados guardados correctamente.")

                # Actualizar id_control en interfaz
                respuesta = response.json()
                nuevo_id = respuesta.get("id_control")
                if nuevo_id is not None:
                    self.id_control_confirmado = nuevo_id
                    self.ui.label_11.setText(f"{int(nuevo_id) + 1:05d}")
                else:
                    print("No se recibió un id_control válido desde el backend.")
                    self.ui.label_11.setText("-----")
            else:
                error_msg = response.json().get("detail", "Error desconocido")
                QMessageBox.critical(self, "Error", f"Error al guardar: {error_msg}")

        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))

    def generar_informe_pdf(self):
        """
        Genera un informe PDF con los resultados del análisis actual.

        El informe se guarda en la carpeta 'historico' del escritorio y
        se registra en la base de datos mediante una llamada al backend.
        """
        if not self.analisis_completado:
            QMessageBox.warning(self, "Advertencia", "Debe finalizar un análisis antes de generar el informe.")
            return

        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M")
        id_control = getattr(self, "id_control_confirmado", None)
        if not id_control:
            QMessageBox.warning(self, "Error", "Primero debes guardar los resultados antes de generar el informe.")
            return
        nombre_pdf = f"informe_control_{id_control}_{timestamp_str}.pdf"

        ruta_hist = obtener_ruta_informes()
        os.makedirs(ruta_hist, exist_ok=True)
        ruta_hist_pdf = os.path.join(ruta_hist, nombre_pdf)

        generar_pdf_completo(
            id_control=id_control,
            nombre_usuario=self.nombre_usuario,
            rol_usuario=self.rol_usuario,
            tablewidget=self.ui.tableWidget,
            imagenes_procesadas=self.imagenes_procesadas,
            tolerancia_tamano=self.ui.doubleSpinBox.value(),
            tolerancia_cantidad=self.ui.spinBox.value(),
            ruta_destino=ruta_hist_pdf,
            logo_path= "logo_isli.png",
            parent_widget=self
        )

        # Registrar el informe en la base de datos
        guardar_registro_informe(
            id_control=int(id_control),
            ruta_pdf=ruta_hist_pdf,
            generado_por=self.id_usuario
        )

    def setupUiConnections(self):
        self.ui.pushButton_report.clicked.connect(self.generar_informe_pdf)
        self.ui.pushButton_report.setEnabled(False)  # Deshabilitado por defecto

        # También deshabilitar al limpiar o interrumpir
        self.ui.pushButton_2.clicked.connect(lambda: self.ui.pushButton_report.setEnabled(False))  # limpiar_pantalla
        self.ui.pushButton_4.clicked.connect(lambda: self.ui.pushButton_report.setEnabled(False))  # interrumpir_control  # Deshabilitado por defecto


    def mostrar_analisis_completado(self, mensaje="Análisis completado", color="#2E7D32"):
        """
        Finaliza el flujo de análisis, muestra resumen global y activa la opción de generar informe.

        Añade una fila resumen con el resultado global basado en el mayor defecto detectado.
        """
        if self.analisis_completado:
            return

        print("Análisis de imágenes completado")

        if self.timer and self.timer.isActive():
            self.timer.stop()

        self.blink_timer.stop()
        self.ui.pushButton_5.setStyleSheet("")

        self.image_view1.showMessage(f"{mensaje}\n{len(self.images)} imágenes procesadas", color)
        self.image_view2.showMessage(f"Siga el flujo de botones\niluminados para\ncompletar proceso", color)

        self.ui.label_5.setText("Análisis finalizado")
        self.ui.label_6.setText("Análisis finalizado")
        self.ui.pushButton_5.setText("Iniciar Control de Calidad")

        if self.images:
            self.ui.progressBar.setValue(len(self.images))

            # Calcular mayor defecto robustamente desde la columna 3
            import re
            mayor_defecto = 0.0
            for i in range(self.ui.tableWidget.rowCount()):
                item = self.ui.tableWidget.item(i, 3)
                if item:
                    match = re.search(r"(\d+(\.\d+)?)", item.text())
                    if match:
                        try:
                            valor = float(match.group(1))
                            mayor_defecto = max(mayor_defecto, valor)
                        except ValueError:
                            print(f"No se pudo convertir '{item.text()}' a float.")

            umbral_usuario = float(self.ui.doubleSpinBox.value())
            resultado_global = "nok" if mayor_defecto > umbral_usuario else "ok"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fila_actual = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(fila_actual)

            # Obtener tipos de defecto desde los JSON procesados
            tipos_acumulados = []
            for ruta in self.imagenes_procesadas:
                tipos = self.leer_tipos_defecto_json(ruta)
                tipos_acumulados.extend(tipos)
            tipos_unicos = sorted(set(tipos_acumulados))
            tipos_str = ", ".join(tipos_unicos) if tipos_unicos else "—"

            # Crear items finales
            item_fecha = QTableWidgetItem(timestamp)
            item_tipos = QTableWidgetItem(tipos_str)
            item_total = QTableWidgetItem(f"Total: {len(self.images)} imágenes")
            item_limite = QTableWidgetItem(f"{mayor_defecto:.2f}")
            item_resultado = QTableWidgetItem(resultado_global)

            items = [item_fecha, item_tipos, item_total, item_limite, item_resultado]

            for item in items:
                item.setFont(QFont("Arial", 10, QFont.Bold))
                item.setBackground(QColor("#C8E6C9"))

            if resultado_global == "nok":
                item_limite.setBackground(QColor("#FFCDD2"))
                item_resultado.setBackground(QColor("#FFCDD2"))

            for col, item in enumerate(items):
                self.ui.tableWidget.setItem(fila_actual, col, item)

            self.ui.tableWidget.scrollToBottom()

        self.analisis_completado = True
        self.ui.pushButton_report.setEnabled(True)
        self.workflow_after_analysis()

    # --- Workflow postcontrol de botones iluminados ---
    def iluminar_btn(self, button, color, tooltip):
        button.setStyleSheet(f"background-color: {color}; color: black; font-weight: bold;")
        button.setToolTip(tooltip)
        button.setEnabled(True)

    def reset_button(self, button, original_style, tooltip=None):
        button.setStyleSheet(original_style)
        if tooltip is not None:
            button.setToolTip(tooltip)

    def workflow_after_analysis(self):
        # Paso 1: Iluminar 'Guardar Resultados'
        self.workflow_guardar_resultados()

    def workflow_guardar_resultados(self):
        btn = self.ui.pushButton_8  # Guardar Resultados
        btn2 = self.ui.pushButton_report  # Generar Informe
        btn3 = self.ui.pushButton_2  # Limpiar pantalla / Reiniciar
        # Deshabilitar también el botón de iniciar control
        self.ui.pushButton_5.setEnabled(False)
        orig_style = btn.styleSheet()
        orig_tooltip = btn.toolTip()
        # Solo habilitar el botón resaltado, deshabilitar los otros
        btn.setEnabled(True)
        btn2.setEnabled(False)
        btn3.setEnabled(False)
        self.iluminar_btn(btn, '#FBC02D', 'Haz clic para guardar los resultados del análisis')
        
        def on_click():
            btn.clicked.disconnect(on_click)
            self.reset_button(btn, orig_style, orig_tooltip)
            self.workflow_generar_informe()
        btn.clicked.connect(on_click)

    def workflow_generar_informe(self):
        btn = self.ui.pushButton_report  # Generar Informe
        btn2 = self.ui.pushButton_8  # Guardar Resultados
        btn3 = self.ui.pushButton_2  # Limpiar pantalla / Reiniciar
        # Deshabilitar también el botón de iniciar control
        self.ui.pushButton_5.setEnabled(False)
        orig_style = btn.styleSheet()
        orig_tooltip = btn.toolTip()
        # Solo habilitar el botón resaltado, deshabilitar los otros
        btn.setEnabled(True)
        btn2.setEnabled(False)
        btn3.setEnabled(False)
        self.iluminar_btn(btn, '#FBC02D', 'Genera el informe PDF del análisis')
        
        def on_click():
            btn.clicked.disconnect(on_click)
            self.reset_button(btn, orig_style, orig_tooltip)
            self.workflow_reiniciar()
        btn.clicked.connect(on_click)

    def workflow_reiniciar(self):
        btn = self.ui.pushButton_2  # Limpiar pantalla / Reiniciar
        btn2 = self.ui.pushButton_8  # Guardar Resultados
        btn3 = self.ui.pushButton_report  # Generar Informe
        # Deshabilitar también el botón de iniciar control
        self.ui.pushButton_5.setEnabled(False)
        orig_style = btn.styleSheet()
        orig_tooltip = btn.toolTip()
        # Solo habilitar el botón resaltado, deshabilitar los otros
        btn.setEnabled(True)
        btn2.setEnabled(False)
        btn3.setEnabled(False)
        self.iluminar_btn(btn, '#FBC02D', 'Reinicia el sistema para un nuevo análisis')
        
        def on_click():
            btn.clicked.disconnect(on_click)
            self.reset_button(btn, orig_style, orig_tooltip)
            self.ui.pushButton_5.setEnabled(True)  # Rehabilitar solo al final del workflow
        btn.clicked.connect(on_click)

    # --- Fin de Workflow ---

    def seleccionar_ruta_almacen(self):
        """Permite al usuario cambiar la carpeta raíz donde se almacenan los rollos."""
        nueva_ruta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta raíz de los rollos")
        if nueva_ruta:
            self.base_folder = nueva_ruta
            guardar_config_ruta(nueva_ruta)
            QMessageBox.information(self, "Ruta actualizada", f"Nueva carpeta raíz:\n{nueva_ruta}")
            self.configurar_combobox()

    def closeEvent(self, event):
        """
        Revoca el token al cerrar la ventana principal (X), para forzar expiración de sesión en el panel web.
        """
        token = getattr(self, 'token_jwt', None)
        if token:
            try:
                requests.post("http://localhost:8000/logout", json={"token": token}, timeout=3)
            except Exception as e:
                print(f"Error al revocar token en closeEvent: {e}")
        event.accept()  # Permite el cierre inmediato

    def prompt_reiniciar_on_start(self):
        btn = self.ui.pushButton_2  # Reiniciar
        orig_style = btn.styleSheet()
        orig_tooltip = btn.toolTip()
        self.iluminar_btn(btn, '#FBC02D', 'Haz clic aquí para reiniciar el sistema antes de iniciar un control de calidad')
        
        def on_click():
            btn.clicked.disconnect(on_click)
            self.reset_button(btn, orig_style, orig_tooltip)
            self.ui.pushButton_5.setEnabled(True)  # Enable 'Iniciar Control de Calidad' after reinicio
        btn.clicked.connect(on_click)


# Bloque para pruebas directas de MainWindow, pero ya no se usa
# porque el flujo completo comienza desde LoginWindow (main.py).
# Se conserva aquí solo como referencia:
#if __name__ == "__main__":
#    app = QApplication(sys.argv)
    
    # Directorio base donde se encuentran las subcarpetas con imágenes
#    base_folder = r"/Users/pacomunozgago/Downloads/arboles"
#    dummy_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # <- Sustituye con token real
#    ventana = MainWindow(base_folder, "admin2@isli.com", "administrador", dummy_token)
#    ventana.show()
    
#    sys.exit(app.exec())