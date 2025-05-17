# archivo: frontend/historico_controles_app.py

import sys
import requests
from PySide6.QtWidgets import QApplication, QWidget, QTableWidgetItem, QMessageBox, QHeaderView, QTableWidgetItem, QPushButton
from PySide6.QtCore import QDate
from datetime import datetime, time
from UI.historico_controles import Ui_Form_historico
from utils_ui import mostrar_datos_usuario, configurar_botones_comunes


class HistoricoControlesWindow(QWidget):

    def cargar_datos_historico(self):
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
        params = {}

        # Filtro por cantidad máxima de defectos
        max_defectos = self.ui.spinBox_numDefectos.value()
        if max_defectos > 0:
            params["max_defectos"] = max_defectos

        # Filtro por tamaño máximo de defecto
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
        # Restablecer spinBoxes
        self.ui.spinBox_numDefectos.setValue(0)
        self.ui.doubleSpinBox_dimDefectos.setValue(0.0)

        # Reset ComboBox
        self.ui.comboBox_listaUsuarios.setCurrentIndex(0)

        # Resetear fechas al día actual (o al mínimo)
        hoy = QDate.currentDate()
        self.ui.dateEdit_desde.setDate(hoy)
        self.ui.dateEdit_hasta.setDate(hoy)

        # Volver a cargar todos los datos
        self.cargar_datos_historico()


    def mostrar_datos_en_tabla(self, controles):
        self.ui.tableWidget_results.setRowCount(0)
        self.ui.tableWidget_results.setColumnCount(6)
        self.ui.tableWidget_results.setHorizontalHeaderLabels([
            "ID Control", "Usuario", "Fecha", "Tamaño máx (mm)", "Cant. defectos", "Comentarios"
        ])

        for row_idx, item in enumerate(controles):
            self.ui.tableWidget_results.insertRow(row_idx)
            self.ui.tableWidget_results.setItem(row_idx, 0, QTableWidgetItem(str(item["id_control"])))
            self.ui.tableWidget_results.setItem(row_idx, 1, QTableWidgetItem(item["nombre_usuario"]))
            self.ui.tableWidget_results.setItem(row_idx, 2, QTableWidgetItem(item["fecha_control"]))
            self.ui.tableWidget_results.setItem(row_idx, 3, QTableWidgetItem(str(item["umbral_tamano_defecto"])))
            self.ui.tableWidget_results.setItem(row_idx, 4, QTableWidgetItem(str(item["num_defectos_tolerables_por_tamano"])))
            self.ui.tableWidget_results.setItem(row_idx, 5, QTableWidgetItem(item["observacs"] or ""))


    def cargar_usuarios(self):
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
        from parpadeo import MainWindow
        from main import BASE_FOLDER  # Asegúrate de tener esta variable disponible o pásala por parámetro
        self.close()
        self.menu_window = MainWindow(BASE_FOLDER, self.nombre_usuario, self.rol_usuario, self.token_jwt)
        self.menu_window.show()

    def configurar_tabla(self):
        header = self.ui.tableWidget_results.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # Ajusta ancho al contenido
        header.setStretchLastSection(True)  # Última columna ocupa espacio restante

    
    def __init__(self, nombre_usuario, rol_usuario, token_jwt):
        super().__init__()
        self.ui = Ui_Form_historico()
        self.ui.setupUi(self)
        self.configurar_tabla()
        self.cargar_usuarios()
        # Establecer fecha actual al iniciar
        hoy = QDate.currentDate()
        self.ui.dateEdit_desde.setDate(hoy)
        self.ui.dateEdit_hasta.setDate(hoy)
        self.setWindowTitle("Histórico de Controles")

        # Guardar atributos para usarlos al volver
        self.nombre_usuario = nombre_usuario
        self.rol_usuario = rol_usuario
        self.token_jwt = token_jwt

        # Mostrar el nombre de usuario y rol
        mostrar_datos_usuario(self.ui, nombre_usuario, rol_usuario)

        # Configurar botones comunes
        configurar_botones_comunes(self, self.ui, rol_usuario, token_jwt)

        self.cargar_datos_historico()

        # Conectar botón para volver
        self.ui.pushButton_menuPpal.clicked.connect(self.volver_a_menu_principal)
        self.ui.pushButton_filtrar.clicked.connect(self.aplicar_filtros)
        self.ui.pushButton_limpiarFiltros.clicked.connect(self.limpiar_filtros)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Test manual con datos ficticios
    dummy_user = "Pepa Gutiérrez"
    dummy_rol = "administrador"
    dummy_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    ventana = HistoricoControlesWindow(dummy_user, dummy_rol, dummy_token)
    ventana.show()
    sys.exit(app.exec())
