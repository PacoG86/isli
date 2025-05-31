"""Punto de entrada de la interfaz gráfica ISLI (frontend).

Lanza la ventana de login que autentica al usuario y da acceso al sistema.
"""
import sys
import requests
from PySide6.QtGui import QIcon
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QProgressDialog
from PySide6.QtCore import QTimer, Qt
from frontend.UI.login_window import Ui_Form
from frontend.control_calidad_menu_principal import MainWindow
from frontend.solicitud_password_window import SolicitudPasswordWindow
import json

API_URL = "http://localhost:8000"

# Cargar BASE_FOLDER desde config.json
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
with open(CONFIG_PATH, encoding='utf-8') as f:
    config = json.load(f)
BASE_FOLDER = config.get('base_folder', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'arboles')))

class LoginWindow(QMainWindow):
    """
    Ventana de inicio de sesión del sistema ISLI.

    Permite al usuario ingresar su email y contraseña para autenticarse contra el backend.
    En caso de éxito, abre el menú principal.
    """
    def __init__(self):
        """
        Inicializa la ventana de login y conecta los botones de acción.
        """
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("Login ISLI")
        ruta_icono = os.path.join(os.path.dirname(__file__), "..", "assets", "logo_isli.ico")
        ruta_icono = os.path.abspath(ruta_icono)
        self.setWindowIcon(QIcon(ruta_icono))
        
        self.ui.pushButton_login.clicked.connect(self.login)
        self.ui.pushButton_login_2.clicked.connect(self.abrir_ventana_password)

    def login(self):
        """
        Envía los datos de login al backend y procesa la respuesta.

        Si el login es correcto, se abre el menú principal.
        Si falla, se muestra un mensaje de error.
        """
        email = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_3.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Campos vacíos", "Por favor completa ambos campos.")
            return

        data = {"correo": email, "contrasenia": password}
        try:
            response = requests.post(f"{API_URL}/login", json=data)
            if response.status_code == 200:
                result = response.json()
                rol = result.get("rol", "desconocido")
                
                progress = QProgressDialog(f"¡Bienvenido!\nRol: {rol}", None, 0, 0, self)
                progress.setWindowTitle("Login exitoso")
                progress.setCancelButton(None)
                progress.setWindowModality(Qt.ApplicationModal)
                progress.setMinimumDuration(0)
                progress.show()
                QTimer.singleShot(3000, progress.close)  # Close after 1.5 seconds
                
                self.abrir_menu_principal(result)
            else:
                detail = response.json().get("detail", "Error de autenticación")
                QMessageBox.critical(self, "Error", detail)
        except Exception as e:
            QMessageBox.critical(self, "Error de conexión", str(e))

    def abrir_menu_principal(self, result):
        """
        Crea e inicia la ventana de menú principal tras un login exitoso.

        Args:
            result (dict): Diccionario con los datos del usuario autenticado.
        """
        self.hide()
        id_usuario = result.get("id_usuario", 1)
        nombre = result.get("nombre_usuario", "Desconocido")
        rol = result.get("rol", "N/A")
        token = result.get("access_token", "")
        self.menu_window = MainWindow(BASE_FOLDER, nombre, rol, token, id_usuario)
        self.menu_window.show()

    def abrir_ventana_password(self):
        """Abre la ventana para solicitar un cambio de contraseña."""
        self.solicitud_window = SolicitudPasswordWindow(self)
        self.solicitud_window.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ruta_icono = os.path.join(os.path.dirname(__file__), "..", "assets", "logo_isli.ico")
    ruta_icono = os.path.abspath(ruta_icono)
    app.setWindowIcon(QIcon(ruta_icono))
    ventana = LoginWindow()
    ventana.show()
    sys.exit(app.exec())
