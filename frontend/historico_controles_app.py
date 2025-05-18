# archivo: frontend/historico_controles_app.py

import sys
import requests
from PySide6.QtWidgets import QApplication, QWidget, QTableWidgetItem, QMessageBox, QHeaderView, QTableWidgetItem, QPushButton
from PySide6.QtCore import QDate, QTimer
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
        self.menu_window = MainWindow(BASE_FOLDER, self.nombre_usuario, self.rol_usuario, self.token_jwt, self.id_usuario)
        self.menu_window.show()
        self.hide()

    def configurar_tabla(self):
        header = self.ui.tableWidget_results.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # Ajusta ancho al contenido
        header.setStretchLastSection(True)  # Última columna ocupa espacio restante

    def mostrar_o_generar_informe(self):
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
                    # No existe, generar uno
                    ruta_destino = f"C:/Users/pgago/Desktop/historico/informe_{id_control}.pdf"

                    # Extraer datos necesarios de la tabla
                    nombre_usuario = self.ui.tableWidget_results.item(fila, 1).text()
                    fecha = self.ui.tableWidget_results.item(fila, 2).text()
                    tolerancia_tamano = float(self.ui.tableWidget_results.item(fila, 3).text())
                    tolerancia_cantidad = int(self.ui.tableWidget_results.item(fila, 4).text())

                    # Imágenes de ejemplo para el visor
                    imagenes_procesadas = []  # Opcionalmente, podrías recuperar imágenes asociadas al control

                    from utils_informes import generar_pdf_completo, guardar_registro_informe
                    generar_pdf_completo(
                        id_control=id_control,
                        nombre_usuario=nombre_usuario,
                        rol_usuario=self.rol_usuario,
                        tablewidget=self.ui.tableWidget_results,
                        imagenes_procesadas=imagenes_procesadas,
                        tolerancia_tamano=tolerancia_tamano,
                        tolerancia_cantidad=tolerancia_cantidad,
                        ruta_destino=ruta_destino,
                        parent_widget=self
                    )
                    guardar_registro_informe(id_control, ruta_destino, self.id_usuario)

            else:
                QMessageBox.warning(self, "Error", f"No se pudo verificar el informe: {response.text}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    
    def __init__(self, nombre_usuario, rol_usuario, token_jwt, id_usuario):
        super().__init__()
        self.ui = Ui_Form_historico()
        self.ui.setupUi(self)
        self.id_usuario = id_usuario
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

        # Retrasar carga de histórico para que UI abra rápido
        QTimer.singleShot(300, self.cargar_datos_historico)

        # Conectar botones
        self.ui.pushButton_menuPpal.clicked.connect(self.volver_a_menu_principal)
        self.ui.pushButton_filtrar.clicked.connect(self.aplicar_filtros)
        self.ui.pushButton_limpiarFiltros.clicked.connect(self.limpiar_filtros)
        self.ui.pushButton_report.clicked.connect(self.mostrar_o_generar_informe)




#if __name__ == "__main__":
#    app = QApplication(sys.argv)

    # Test manual con datos ficticios
#    dummy_user = "Pepa Gutiérrez"
#    dummy_rol = "administrador"
#    dummy_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

#    ventana = HistoricoControlesWindow(dummy_user, dummy_rol, dummy_token)
#    ventana.show()
#    sys.exit(app.exec())
