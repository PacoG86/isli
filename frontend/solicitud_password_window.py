import requests
from PySide6.QtGui import QIcon
import os
from PySide6.QtWidgets import QDialog, QMessageBox
from frontend.UI.solicitud_password_dialog import Ui_Dialog
from datetime import datetime

class SolicitudPasswordWindow(QDialog):
    """
    Ventana de diálogo para solicitar un cambio de contraseña.

    Permite al usuario ingresar su email, nueva contraseña y un motivo opcional.
    Envía la solicitud al backend para su posterior validación por un administrador.
    """
    def __init__(self, parent=None):
        """
        Inicializa la interfaz y conecta los botones de enviar y cancelar.

        Args:
            parent (QWidget, optional): Widget padre. Por defecto es None.
        """
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Solicitud de cambio de contraseña")
        ruta_icono = os.path.abspath("logo_isli.ico")  # Ajusta según tu estructura
        self.setWindowIcon(QIcon(ruta_icono))

        # Conectamos botones
        self.ui.pushButton_enviar.clicked.connect(self.enviar_solicitud)
        self.ui.pushButton_cancelar.clicked.connect(self.close)
    
    def enviar_solicitud(self):
        """
        Envía la solicitud de cambio de contraseña al backend.

        Valida los campos requeridos, construye el payload y muestra mensajes
        de confirmación o error según la respuesta del servidor.
        """
        email = self.ui.lineEdit_email.text().strip()
        nueva_password = self.ui.lineEdit_password.text().strip()
        motivo = self.ui.textEdit_motivo.toPlainText().strip()

        if not email:
            QMessageBox.warning(self, "Campos requeridos", "Por favor, introduce tu email.")
            return

        if not nueva_password:
            QMessageBox.warning(self, "Campos requeridos", "Por favor, introduce una nueva contraseña.")
            return

        # Validación de contraseña
        mensaje_restricciones = (
            "La contraseña debe tener al menos 8 caracteres, incluyendo "
            "letras, mayúsculas, números y caracteres especiales."
        )
        if len(nueva_password) < 8 \
            or nueva_password.isdigit() or nueva_password.isalpha() \
            or not any(c.isupper() for c in nueva_password) \
            or not any(c in '!@#$%^&*()-_=+[]{}|;:,.<>?/\\' for c in nueva_password) \
            or not any(c.isdigit() for c in nueva_password):
            QMessageBox.warning(self, "Contraseña insegura", mensaje_restricciones)
            return
        # Fin validación

        payload = {
            "email_usuario": email,
            "motivo": motivo,
            "password_nueva": nueva_password,
            "timestamp": datetime.now().isoformat()
        }

        try:
            response = requests.post("http://localhost:8000/controles/solicitud_password", json=payload)
            if response.status_code == 200:
                QMessageBox.information(self, "Enviado", "La solicitud fue registrada correctamente.")
                self.close()
            else:
                detalle = response.json().get("detail", "Error desconocido")
                QMessageBox.critical(self, "Error", f"No se pudo registrar la solicitud:\n{detalle}")
        except Exception as e:
            QMessageBox.critical(self, "Error de conexión", f"No se pudo conectar al servidor:\n{str(e)}")
