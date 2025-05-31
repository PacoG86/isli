import requests
import json
from PySide6.QtGui import QIcon
import os
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QHeaderView, QTableWidgetItem, QFileDialog  
from PySide6.QtCore import QDate, QTimer, Qt, QRunnable, QThreadPool, Slot
from datetime import datetime, time
from UI.historico_controles import Ui_Form_historico
from utils_ui import mostrar_datos_usuario, configurar_botones_comunes, guardar_config_ruta


class HistoricoControlesWindow(QWidget):
    """
    Ventana del sistema ISLI para visualizar y filtrar el histórico de controles de calidad.

    Permite aplicar filtros por usuario, fecha, tolerancia y tamaño de defecto.
    También permite editar comentarios y visualizar informes asociados.
    """
    def cargar_datos_historico(self):
        """
        Obtiene el listado completo de controles desde la API y los muestra en la tabla.
        """
        try:
            response = requests.get("http://localhost:8000/controles/historico")
            if response.status_code == 200:
                data = response.json()
                self.mostrar_datos_en_tabla(data)
            else:
                QMessageBox.warning(self, "Error", f"No se pudo obtener el histórico.\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error de conexión", str(e))

    def aplicar_filtros(self):
        """
        Aplica los filtros seleccionados en la interfaz y actualiza la tabla con los resultados.
        """
        params = {}

        # Filtro por cantidad máxima de defectos en rollo
        max_defectos = self.ui.spinBox_numDefectos.value()
        if max_defectos > 0:
            params["max_defectos"] = max_defectos

        # Filtro por tamaño máximo de defecto individual analizado
        max_dim = self.ui.doubleSpinBox_dimDefectos.value()
        if max_dim > 0:
            params["max_dim"] = max_dim

        # Filtro por usuario
        usuario = self.ui.comboBox_listaUsuarios.currentText()
        if usuario and not usuario.startswith("--"):
            params["usuario"] = usuario

        # Filtro por fecha (si ambas fechas son válidas)
        fecha_desde = datetime.combine(self.ui.dateEdit_desde.date().toPython(), time.min)
        fecha_hasta = datetime.combine(self.ui.dateEdit_hasta.date().toPython(), time.max)

        params["desde"] = fecha_desde.isoformat()
        params["hasta"] = fecha_hasta.isoformat()

        try:
            response = requests.get("http://localhost:8000/controles/historico", params=params)
            if response.status_code == 200:
                datos_filtrados = response.json()
                self.mostrar_datos_en_tabla(datos_filtrados)
            else:
                print("Error al filtrar datos:", response.text)
        except Exception as e:
            print("Excepción al aplicar filtros:", str(e))

    def limpiar_filtros(self):
        """Reinicia los filtros a valores por defecto y recarga los datos."""
        # Restablecer spinBoxes
        self.ui.spinBox_numDefectos.setValue(0)
        self.ui.doubleSpinBox_dimDefectos.setValue(0.0)

        # Resetear ComboBox
        self.ui.comboBox_listaUsuarios.setCurrentIndex(0)

        # Resetear fechas al día actual (o al mínimo)
        hoy = QDate.currentDate()
        self.ui.dateEdit_desde.setDate(hoy)
        self.ui.dateEdit_hasta.setDate(hoy)

        # Volver a cargar todos los datos
        self.cargar_datos_historico()

    
    def mostrar_datos_en_tabla(self, controles):
        """
        Muestra en la tabla los datos de controles pasados como lista de diccionarios.
        
        Args:
            controles (list[dict]): Lista con la información de cada control.
        """
        self.ui.tableWidget_results.blockSignals(True)
        self.ui.tableWidget_results.setRowCount(0)
        self.ui.tableWidget_results.setColumnCount(8)
        self.ui.tableWidget_results.setHorizontalHeaderLabels([
            "ID Control", "Usuario", "Fecha/Hora", "Area max(mm2)", "#defectos",
            "Informe", "Result.", "Comentarios"
        ])
        for row_idx, item in enumerate(controles):
            self.ui.tableWidget_results.insertRow(row_idx)
            columnas = [
                str(item["id_control"]),
                item["nombre_usuario"],
                item["fecha_control"],
                str(item["umbral_tamano_defecto"]),
                str(item["num_defectos_tolerables_por_tamano"])
            ]
            for col_idx, valor in enumerate(columnas):
                celda = QTableWidgetItem(valor)
                celda.setFlags(celda.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidget_results.setItem(row_idx, col_idx, celda)

            icono_informe = "✅" if item.get("tiene_informe", False) else "❌"
            reporte_item = QTableWidgetItem(icono_informe)
            reporte_item.setFlags(reporte_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_results.setItem(row_idx, 5, reporte_item)

            resultado = item.get("resultado_rollo", "").lower()
            icono_resultado = "🟢" if resultado == "ok" else "🔴" if resultado == "nok" else "❔"
            resultado_item = QTableWidgetItem(icono_resultado)
            resultado_item.setFlags(resultado_item.flags() & ~Qt.ItemIsEditable)
            self.ui.tableWidget_results.setItem(row_idx, 6, resultado_item)

            notas = item.get("notas", "")
            notas_item = QTableWidgetItem(notas)
            self.ui.tableWidget_results.setItem(row_idx, 7, notas_item)
        self.ui.tableWidget_results.blockSignals(False)
    
    def cargar_usuarios(self):
        """Carga la lista de usuarios disponibles desde la API."""
        try:
            response = requests.get("http://localhost:8000/controles/usuarios")
            if response.status_code == 200:
                lista_usuarios = response.json()
                self.ui.comboBox_listaUsuarios.clear()
                self.ui.comboBox_listaUsuarios.addItem("-- Filtra por usuario --")  # placeholder
                self.ui.comboBox_listaUsuarios.addItems(lista_usuarios)
            else:
                print("No se pudieron cargar los usuarios:", response.text)
        except Exception as e:
            print("Error al cargar usuarios:", str(e))


    def volver_a_menu_principal(self):
        """Cierra la ventana actual y regresa al menú principal."""
        from frontend.control_calidad_menu_principal import MainWindow
        from main import BASE_FOLDER  # Disponible en config.json
        self.menu_window = MainWindow(BASE_FOLDER, self.nombre_usuario, self.rol_usuario, self.token_jwt, self.id_usuario)
        self.menu_window.show()
        self.hide()

    def configurar_tabla(self):
        header = self.ui.tableWidget_results.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # Ajusta ancho al contenido
        header.setStretchLastSection(True)  # Última columna ocupa espacio restante

    def mostrar_o_generar_informe(self):
        """
        Verifica si existe un informe PDF asociado al control seleccionado.
        Si existe, lo abre. Si no, muestra un mensaje.
        """
        fila = self.ui.tableWidget_results.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Sin selección", "Seleccione una fila para mostrar el informe.")
            return

        id_control = self.ui.tableWidget_results.item(fila, 0).text()

        try:
            response = requests.get(f"http://localhost:8000/controles/informe/existe?id_control={id_control}")
            if response.status_code == 200:
                data = response.json()
                if data.get("existe"):
                    ruta_pdf = data["ruta_pdf"]
                    from utils_informes import abrir_pdf
                    abrir_pdf(ruta_pdf)
                else:
                    QMessageBox.information(
                        self,
                        "Informe no disponible",
                        f"Este control (ID {id_control}) aún no tiene un informe generado."
                    )
            else:
                QMessageBox.warning(self, "Error", f"No se pudo verificar el informe:\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def guardar_comentarios(self):
        selection = self.ui.tableWidget_results.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Sin selección", "No hay notas que guardar. Seleccione fila de informe y escriba sus comentarios.")
            return
        fila = self.ui.tableWidget_results.currentRow()
        notas_item = self.ui.tableWidget_results.item(fila, 7)
        if notas_item is None or not notas_item.text().strip():
            QMessageBox.warning(self, "Sin comentarios", "No hay notas que guardar. Seleccione fila de informe y escriba sus comentarios.")
            return
        # Si hay selección y comentarios, mostrar mensaje de éxito
        QMessageBox.information(self, "Registro completado", "Notas guardadas correctamente.")

    def seleccionar_ruta_informes(self):
        """
        Permite al usuario seleccionar una nueva carpeta base para guardar informes.
        """
        nueva_ruta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta para informes")
        if nueva_ruta:
            # Convertir forward slashes a backward slashes para compatibilidad
            nueva_ruta = nueva_ruta.replace("\\", "/")
            try:
                # Abrimos y modificamos el config.json
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
            except FileNotFoundError:
                config = {}

            config["ruta_informes"] = nueva_ruta

            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

            QMessageBox.information(self, "Ruta actualizada", f"Nueva carpeta para informes:\n{nueva_ruta}")
    
    def actualizar_nota_en_background(self, id_control, nota):
        tarea = ActualizadorNotas(id_control, nota)
        QThreadPool.globalInstance().start(tarea)
    
    def on_cell_changed(self, row, column):
        if column != 7:  # Solo columna "Comentarios"
            return

        id_item = self.ui.tableWidget_results.item(row, 0)
        nota_item = self.ui.tableWidget_results.item(row, column)

        if not id_item or not nota_item:
            return

        id_control = int(id_item.text())
        nueva_nota = nota_item.text()

        self.ui.tableWidget_results.blockSignals(True)
        self.actualizar_nota_en_background(id_control, nueva_nota)
        self.ui.tableWidget_results.blockSignals(False)


    def __init__(self, nombre_usuario, rol_usuario, token_jwt, id_usuario):
        """
        Inicializa la interfaz, carga datos de usuario y conecta eventos.

        Args:
            nombre_usuario (str): Nombre del usuario actual.
            rol_usuario (str): Rol ('administrador' u 'operario').
            token_jwt (str): Token de autenticación.
            id_usuario (int): ID del usuario.
        """
        super().__init__()
        self.ui = Ui_Form_historico()
        self.ui.setupUi(self)
        self.showMaximized()
        ruta_icono = os.path.join(os.path.dirname(__file__), "..", "logo_isli_white.png")
        ruta_icono = os.path.abspath(ruta_icono)
        self.setWindowIcon(QIcon(ruta_icono))
        self.id_usuario = id_usuario
        self.configurar_tabla()
        self.cargar_usuarios()
        # Establecer fecha actual al iniciar
        hoy = QDate.currentDate()
        self.ui.dateEdit_desde.setDate(hoy)
        self.ui.dateEdit_hasta.setDate(hoy)
        self.setWindowTitle("Histórico de Controles")

        # Guardar atributos para usarlos al volver al menú princial (ventana control calidad)
        self.nombre_usuario = nombre_usuario
        self.rol_usuario = rol_usuario
        self.token_jwt = token_jwt

        # Mostrar el nombre de usuario y rol
        mostrar_datos_usuario(self.ui, nombre_usuario, rol_usuario)

        # Configurar botones comunes
        configurar_botones_comunes(self, self.ui, rol_usuario, token_jwt)

        # Retrasar carga de histórico para que UI abra rápido
        QTimer.singleShot(300, self.cargar_datos_historico)

        # Conectar botones
        self.ui.pushButton_menuPpal.clicked.connect(self.volver_a_menu_principal)
        self.ui.pushButton_filtrar.clicked.connect(self.aplicar_filtros)
        self.ui.pushButton_limpiarFiltros.clicked.connect(self.limpiar_filtros)
        self.ui.pushButton_report.clicked.connect(self.mostrar_o_generar_informe)
        self.ui.pushButton_saveObs.clicked.connect(self.guardar_comentarios)
        self.ui.pushButton_rutaInforme.clicked.connect(self.seleccionar_ruta_informes)
        self.ui.tableWidget_results.cellChanged.connect(self.on_cell_changed)

    def closeEvent(self, event):
        """
        Revoca el token al cerrar la ventana de histórico (X), para forzar expiración de sesión en el panel web.
        """
        token = getattr(self, 'token_jwt', None)
        if token:
            try:
                requests.post("http://localhost:8000/logout", json={"token": token}, timeout=3)
            except Exception as e:
                print(f"Error al revocar token en closeEvent: {e}")
        event.accept()  # Permite el cierre inmediato

class ActualizadorNotas(QRunnable):
    def __init__(self, id_control, nota):
        super().__init__()
        self.id_control = id_control
        self.nota = nota

    @Slot()
    def run(self):
        try:
            payload = {"id_control": self.id_control, "notas": self.nota}
            response = requests.post("http://localhost:8000/controles/informe/actualizar_notas", json=payload)
            if response.status_code != 200:
                print(f"Error actualizando nota de ID {self.id_control}: {response.text}")
        except Exception as e:
            print(f"Error conexión al guardar nota ID {self.id_control}: {str(e)}")


#if __name__ == "__main__":
#    app = QApplication(sys.argv)

    # Test manual con datos ficticios
#    dummy_user = "Pepa Gutiérrez"
#    dummy_rol = "administrador"
#    dummy_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

#    ventana = HistoricoControlesWindow(dummy_user, dummy_rol, dummy_token)
#    ventana.show()
#    sys.exit(app.exec())
