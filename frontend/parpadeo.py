import sys
import os
import json
from datetime import datetime
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSizePolicy, QGraphicsView,
    QGraphicsScene, QVBoxLayout, QFrame, QGraphicsTextItem,
    QTableWidgetItem, QMessageBox
)
from PySide6.QtGui import QPixmap, QImage, QPainter, QFont, QColor, QBrush
from PySide6.QtCore import Qt, QTimer, QRectF, QEvent
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
            print(f"\u274c Error: no se pudo cargar la imagen desde {image_path}")
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
        view_width = self.viewport().width()
        view_height = self.viewport().height()
        rect = QRectF(0, 0, view_width, view_height)
        self.scene.addRect(rect, brush=QBrush(QColor(bgColor)))
        self.text_item = QGraphicsTextItem(message)
        font = QFont("Arial", 14, QFont.Bold)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(textColor))
        text_width = self.text_item.boundingRect().width()
        text_height = self.text_item.boundingRect().height()
        self.text_item.setPos((rect.width() - text_width) / 2, (rect.height() - text_height) / 2)
        self.scene.addItem(self.text_item)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene and not self.scene.itemsBoundingRect().isNull():
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            if self.text_item and not self.image_item:
                message = self.text_item.toPlainText()
                bgColor = self.scene.items()[-1].brush().color().name()
                textColor = self.text_item.defaultTextColor().name()
                self.showMessage(message, bgColor, textColor)


class MainWindow(QMainWindow):
    def __init__(self, base_folder, nombre_usuario, rol_usuario):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("ISLI - Control de Calidad")

        self.ui.comboBox.installEventFilter(self)
        self.ui.spinBox.valueChanged.connect(self.configurar_combobox)
        
        self.nombre_usuario = nombre_usuario
        self.rol_usuario = rol_usuario
        self.ui.label_3.setText(f"{nombre_usuario} ({rol_usuario})")
        self.obtener_siguiente_id_control()

        # Directorio base donde se encuentran las subcarpetas
        self.base_folder = base_folder
        
        # Inicializar variables
        self.folder = None  # La carpeta actual seleccionada
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
        self.configurar_combobox()
        self.configurar_tabla()
        self.reemplazar_qlabels()
        self.ui.progressBar.setValue(0)
        
        # Conectar señales
        self.ui.pushButton_5.clicked.connect(self.iniciar_control_calidad)  # Botón "Iniciar Control de Calidad"
        self.ui.pushButton_2.clicked.connect(self.limpiar_pantalla)  # Botón "Limpiar pantalla"
        self.ui.pushButton_4.clicked.connect(self.confirmar_interrumpir)  # Botón "Interrumpir control"
        self.ui.pushButton_8.clicked.connect(self.guardar_resultados)
        self.ui.pushButton_3.clicked.connect(self.logout)

    def obtener_siguiente_id_control(self): 
        try:
            response = requests.get("http://localhost:8000/controles/ultimo_id_control")
            if response.status_code == 200:
                data = response.json()
                siguiente_id = data.get("siguiente_id")

                print(f"📥 ID recibido desde backend: {siguiente_id}")

                if isinstance(siguiente_id, int):  # comprobamos que sea un entero válido
                    self.ui.label_11.setText(f"{siguiente_id:05d}")
                    return True
                else:
                    print("⚠️ ID de control inválido o ausente en la respuesta.")
                    self.ui.label_11.setText("-----")
                    return False
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                self.ui.label_11.setText("Error")
                return False
        except Exception as e:
            print(f"❌ Excepción al obtener ID control: {e}")
            self.ui.label_11.setText("N/A")
            return False


    def configurar_combobox(self):
        """Configura el ComboBox con las subcarpetas del directorio base, filtrando por el número máximo de imágenes"""
        self.ui.comboBox.blockSignals(True)
        self.ui.comboBox.clear()
        

        try:
            max_imgs = self.ui.spinBox.value()
            if max_imgs <= 0:
                self.ui.comboBox.addItem("-- No hay rollos que cumplan con el umbral indicado --")
                print("🔢 El valor del spinBox es 0, no se cargarán carpetas.")
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
                print(f"📁 Cargadas {len(carpetas_validas)} carpetas con ≤ {max_imgs} imágenes")
            else:
                self.ui.comboBox.addItem("-- No hay rollos que cumplan con el umbral indicado --")
                print("⚠️ No se encontraron carpetas que cumplan con el criterio.")
        except Exception as e:
            print(f"❌ Error al cargar subcarpetas: {e}")
            QMessageBox.warning(self, "Error", f"No se pudo acceder al directorio: {self.base_folder}\n{str(e)}")

        self.ui.comboBox.blockSignals(False)

    def eventFilter(self, obj, event):
        if obj == self.ui.comboBox and event.type() == QEvent.MouseButtonPress:
            self.configurar_combobox()
        return super().eventFilter(obj, event)

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
        self.ui.tableWidget.setHorizontalHeaderLabels([
        "Fecha/ Hora", "REF Rollo", "REF Defecto Img", "Dim. Defecto mm", "Resultado"
        ])
    
        header = self.ui.tableWidget.horizontalHeader()
        for col in range(5):
            header.setSectionResizeMode(col, header.ResizeMode.Stretch)  # que todas se estiren por igual

        self.ui.tableWidget.setRowCount(0)

    def agregar_registro_a_tabla(self, ruta_imagen):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        carpeta = os.path.basename(os.path.dirname(ruta_imagen))  # ID Rollo
        archivo = os.path.basename(ruta_imagen)                   # Ref. Img Defecto
        dim_defecto = "4.23"  # 🧪 Sustituye por lógica real o variable
        umbral_usuario = float(self.ui.doubleSpinBox.value())
        result_analisis = "nok" if float(dim_defecto) > umbral_usuario else "ok"

        fila = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(fila)
        self.ui.tableWidget.setItem(fila, 0, QTableWidgetItem(timestamp))
        self.ui.tableWidget.setItem(fila, 1, QTableWidgetItem(carpeta))
        self.ui.tableWidget.setItem(fila, 2, QTableWidgetItem(archivo))
        self.ui.tableWidget.setItem(fila, 3, QTableWidgetItem(dim_defecto))
        self.ui.tableWidget.setItem(fila, 4, QTableWidgetItem(result_analisis))
        
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
        """Inicia el proceso de control de calidad con la carpeta seleccionada"""
        # Si ya hay un control en curso, detenerlo primero
        if self.timer and self.timer.isActive():
            self.interrumpir_control()
            return
            
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
        
        # Actualizar el texto del botón
        self.ui.pushButton_5.setText("Iniciar Control de Calidad")
        
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
        
        # Iniciar parpadeo del botón
        self.blink_timer.start(500)
        
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
                self.image_view1.showMessage("Control interrumpido", "#F57C00")
                self.image_view2.showMessage("Control interrumpido", "#F57C00")
                self.ui.label_5.setText("Control interrumpido")
                self.ui.label_6.setText("Control interrumpido")
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
            print("⏹️ Control de calidad interrumpido")
            
            # Detener parpadeo del botón y restaurar estilo original
            self.blink_timer.stop()
            self.ui.pushButton_5.setStyleSheet("")  # Restaurar estilo original
            
            # Mostrar mensaje de interrupción si no estaba completado
            if not self.analisis_completado and self.images:
                self.image_view1.showMessage("Control interrumpido", "#F57C00")
                self.image_view2.showMessage("Control interrumpido", "#F57C00")
                self.ui.label_5.setText("Control interrumpido")
                self.ui.label_6.setText("Control interrumpido")
                
            # Restaurar el texto del botón
            self.ui.pushButton_5.setText("Iniciar Control de Calidad")

    def mostrar_siguiente_imagen(self):
        if not self.images or self.index >= len(self.images):
            if not self.analisis_completado and self.images:
                self.mostrar_analisis_completado()
            return

        ruta_imagen = self.images[self.index]
        self.image_view1.setImage(ruta_imagen)
        self.image_view2.setImage(ruta_imagen)

        # Buscar la dimensión máxima desde el JSON si está disponible
        nombre = os.path.basename(ruta_imagen)
        json_path = os.path.join(self.folder, f"{os.path.splitext(nombre)[0]}.json")
        dim_max = self.obtener_dim_maxima_desde_json(json_path)

        if dim_max:
            self.ui.label_5.setText(f"MAYOR DEFECTO ENCONTRADO: {dim_max:.2f} mm")
        else:
            self.ui.label_5.setText("MAYOR DEFECTO ENCONTRADO: -- mm")
        
        self.ui.label_6.setText(f"Imagen: {nombre}")

        self.ui.progressBar.setValue(self.index + 1)
        self.agregar_registro_a_tabla(ruta_imagen)
        
        print(f"🔄 Mostrando imagen: {nombre} ({self.index + 1}/{len(self.images)})")
        self.index += 1

    def obtener_dim_maxima_desde_json(self, json_path): #REVISAR AL INCLUIR LAS IMÁGENES FINALES
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                contenido = json.load(f)
                defectos = contenido.get("defectos", [])
                if defectos:
                    return max(d["area"] for d in defectos)
        except Exception as e:
            print(f"❌ Error leyendo JSON para dimensión máxima: {e}")
        return None

    
    def mostrar_analisis_completado(self, mensaje="Análisis completado", color="#2E7D32"):
        if self.analisis_completado:
            return
        
        print("✅ Análisis de imágenes completado")
        
        if self.timer and self.timer.isActive():
            self.timer.stop()
            
        # Detener parpadeo del botón y restaurar estilo original
        self.blink_timer.stop()
        self.ui.pushButton_5.setStyleSheet("")  # Restaurar estilo original
            
        # Mostrar mensaje en ambos visores
        self.image_view1.showMessage(f"{mensaje}\n{len(self.images)} imágenes procesadas", color)
        self.image_view2.showMessage(f"{mensaje}\n{len(self.images)} imágenes procesadas", color)
        
        # Actualizar las etiquetas de detalles
        self.ui.label_5.setText("Análisis finalizado")
        self.ui.label_6.setText("Análisis finalizado")
        
        # Restaurar el texto del botón
        self.ui.pushButton_5.setText("Iniciar Control de Calidad")
        
        # Asegurar que la barra de progreso esté al 100%
        if self.images:
            self.ui.progressBar.setValue(len(self.images))
        
        # Agregar una fila de resumen a la tabla
        if self.images:
            # Calcular mayor defecto
            mayor_defecto = 0.0
            for i in range(self.ui.tableWidget.rowCount()):
                item = self.ui.tableWidget.item(i, 3)
                if item and item.text().replace('.', '', 1).isdigit():
                    try:
                        valor = float(item.text())
                        mayor_defecto = max(mayor_defecto, valor)
                    except ValueError:
                        pass

            umbral_usuario = float(self.ui.doubleSpinBox.value())
            resultado_global = "nok" if mayor_defecto > umbral_usuario else "ok"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fila_actual = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(fila_actual)
            
            self.ui.tableWidget.setItem(fila_actual, 0, QTableWidgetItem(timestamp))
            self.ui.tableWidget.setItem(fila_actual, 1, QTableWidgetItem("RESUMEN"))
            self.ui.tableWidget.setItem(fila_actual, 2, QTableWidgetItem(f"Total: {len(self.images)} imágenes"))
            self.ui.tableWidget.setItem(fila_actual, 3, QTableWidgetItem(f"LÍMITE: {mayor_defecto:.2f} mm"))
            self.ui.tableWidget.setItem(fila_actual, 4, QTableWidgetItem(resultado_global))

            # Hacer la fila de resumen destacada (fondo verde claro)
            for col in range(3):
                item = self.ui.tableWidget.item(fila_actual, col)
                item.setBackground(QBrush(QColor("#C8E6C9")))
                item.setFont(QFont("Arial", 10, QFont.Bold))
            
            self.ui.tableWidget.scrollToBottom()
        
        self.analisis_completado = True

    def guardar_resultados(self):
        if not self.analisis_completado:
            QMessageBox.warning(self, "Advertencia", "No se ha completado ningún análisis para guardar.")
            return

        try:
            # Extraer valores del formulario
            umbral = float(self.ui.doubleSpinBox.value())
            max_defectos = int(self.ui.spinBox.value())
            ruta_rollo = self.folder  # Carpeta actual seleccionada
            num_defectos_en_rollo = len(self.images)  # Número total de imágenes cargadas
            timestamp_actual = datetime.now().isoformat()

            # Compilar estructura del payload
            data = {
                "id_usuario": 1,  # Sustituye esto cuando tengas login real
                "umbral_tamano_defecto": umbral,
                "num_defectos_tolerables_por_tamano": max_defectos,
                "fecha_control": timestamp_actual,
                "rollo": {
                    "ruta_local_rollo": ruta_rollo,
                    "num_defectos_rollo": num_defectos_en_rollo,
                    "total_defectos_intolerables_rollo": 0,  # Se calculará más abajo
                    "resultado_rollo": "ok",  # Se modificará si se detectan defectos no tolerables
                    "orden_analisis": 1  # O el número correspondiente si haces múltiples controles por sesión
                },
                "imagenes": []
            }

            defectos_intolerables = 0

            for row in range(self.ui.tableWidget.rowCount()):
                if self.ui.tableWidget.item(row, 1).text() == "RESUMEN":
                    continue

                nombre_archivo = self.ui.tableWidget.item(row, 2).text()
                dim_defecto = float(self.ui.tableWidget.item(row, 3).text())
                clasificacion = self.ui.tableWidget.item(row, 4).text().lower()

                if clasificacion == "nok":
                    defectos_intolerables += 1

                # Ruta al JSON con datos adicionales (mismo nombre que la imagen)
                json_path = os.path.join(self.folder, f"{os.path.splitext(nombre_archivo)[0]}.json")
                print(json_path)

                defectos = []
                detecciones = []

                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            contenido = json.load(f)
                            defectos = contenido.get("defectos", [])
                            detecciones = contenido.get("detecciones", [])
                    except Exception as e:
                        print(f"❌ Error leyendo JSON {json_path}: {e}")

                data["imagenes"].append({
                    "nombre_archivo": nombre_archivo,
                    "fecha_captura": timestamp_actual,
                    "max_dim_defecto_medido": dim_defecto,
                    "clasificacion": clasificacion,
                    "defectos": defectos, #ojo sobre cómo se obtienen del json
                    "detecciones": detecciones
                })

            # Ajustar total de defectos intolerables y resultado del rollo
            data["rollo"]["total_defectos_intolerables_rollo"] = defectos_intolerables
            data["rollo"]["resultado_rollo"] = "nok" if defectos_intolerables > 0 else "ok"

            # Enviar al backend
            response = requests.post("http://localhost:8000/controles/nuevo", json=data)

            if response.status_code == 200:
                QMessageBox.information(self, "Éxito", "✅ Resultados guardados correctamente.")

                # Actualizar id_control en interfaz
                respuesta = response.json()
                nuevo_id = respuesta.get("id_control")
                if nuevo_id is not None:
                    self.ui.label_11.setText(f"{int(nuevo_id) + 1:05d}")
                else:
                    print("⚠️ No se recibió un id_control válido desde el backend.")
                    self.ui.label_11.setText("-----")
            else:
                error_msg = response.json().get("detail", "Error desconocido")
                QMessageBox.critical(self, "Error", f"❌ Error al guardar: {error_msg}")

        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))


    def logout(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cerrar sesión")
        msg_box.setText("¿Está seguro que desea cerrar sesión?")
        msg_box.setIcon(QMessageBox.Question)

        btn_yes = msg_box.addButton("Sí", QMessageBox.YesRole)
        btn_no = msg_box.addButton("No", QMessageBox.NoRole)
        btn_new_session = msg_box.addButton("Abrir nueva sesión", QMessageBox.AcceptRole)

        msg_box.exec()

        clicked_button = msg_box.clickedButton()

        if clicked_button == btn_yes:
            despedida = QMessageBox(self)
            despedida.setWindowTitle("Gracias")
            despedida.setText("Muchas gracias por confiar en ISLI.\n¡Hasta pronto!")
            despedida.setIcon(QMessageBox.Information)
            despedida.setStandardButtons(QMessageBox.NoButton)

            # Cerrar la app después de 2 segundos
            # Mostrar el diálogo y cerrarlo tras 2 segundos
            def cerrar_y_salir():
                despedida.done(0)  # Cierra el diálogo
                QApplication.instance().quit()

            QTimer.singleShot(2000, cerrar_y_salir)
            despedida.exec()  # Ejecutar como modal y esperar los 2 segundos

        elif clicked_button == btn_no:
            # No hacer nada, simplemente cerrar el diálogo
            return

        elif clicked_button == btn_new_session:
            # Cerrar ventana actual y volver a mostrar la de login
            self.close()
            from main import LoginWindow  # Importa aquí para evitar import circular
            self.login_window = LoginWindow()
            self.login_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Directorio base donde se encuentran las subcarpetas con imágenes
    base_folder = r"C:\Users\pgago\Desktop\arboles"
    
    ventana = MainWindow(base_folder)
    ventana.show()
    
    sys.exit(app.exec())