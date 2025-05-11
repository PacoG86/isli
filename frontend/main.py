import sys
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from UI.login_window import Ui_Form
from parpadeo import MainWindow  # <-- importa la ventana de menú principal

API_URL = "http://localhost:8000"
BASE_FOLDER = r"C:\Users\pgago\Desktop\arboles"

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.pushButton_login.clicked.connect(self.login)

    def login(self):
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
                QMessageBox.information(self, "Login exitoso", f"¡Bienvenido!\nRol: {rol}")
                
                self.abrir_menu_principal(result)
            else:
                detail = response.json().get("detail", "Error de autenticación")
                QMessageBox.critical(self, "Error", detail)
        except Exception as e:
            QMessageBox.critical(self, "Error de conexión", str(e))

    def abrir_menu_principal(self, result):
        self.hide()
        nombre = result.get("nombre_usuario", "Desconocido")
        rol = result.get("rol", "N/A")
        token = result.get("access_token", "")
        self.menu_window = MainWindow(BASE_FOLDER, nombre, rol, token)
        self.menu_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = LoginWindow()
    ventana.show()
    sys.exit(app.exec())
