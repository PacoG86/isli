import sys
import requests
from PySide6.QtWidgets import QDialog, QMessageBox
from UI.solicitud_password_dialog import Ui_Dialog  # Asegúrate de que el archivo generado se llama así
from datetime import datetime


class SolicitudPasswordWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Solicitud de cambio de contraseña")

        # Conectar botones
        self.ui.pushButton_enviar.clicked.connect(self.enviar_solicitud)
        self.ui.pushButton_cancelar.clicked.connect(self.close)

    
    def enviar_solicitud(self):
        email = self.ui.lineEdit_email.text().strip()
        nueva_password = self.ui.lineEdit_password.text().strip()
        motivo = self.ui.textEdit_motivo.toPlainText().strip()

        if not email:
            QMessageBox.warning(self, "Campos requeridos", "Por favor, introduce tu email.")
            return

        if not nueva_password:
            QMessageBox.warning(self, "Campos requeridos", "Por favor, introduce una nueva contraseña.")
            return

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
