# archivo: frontend/historico_controles_app.py

import sys
from PySide6.QtWidgets import QApplication, QWidget
from UI.historico_controles import Ui_Form_historico
from utils_ui import mostrar_datos_usuario, configurar_botones_comunes

class HistoricoControlesWindow(QWidget):
    def __init__(self, nombre_usuario, rol_usuario, token_jwt):
        super().__init__()
        self.ui = Ui_Form_historico()
        self.ui.setupUi(self)
        self.setWindowTitle("Histórico de Controles")

        # Mostrar el nombre de usuario y rol
        mostrar_datos_usuario(self.ui, nombre_usuario, rol_usuario)
        # Configurar botones comunes
        configurar_botones_comunes(self, self.ui, rol_usuario, token_jwt)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 🔁 Test manual con datos ficticios
    dummy_user = "Pepa Gutiérrez"
    dummy_rol = "administrador"
    dummy_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    ventana = HistoricoControlesWindow(dummy_user, dummy_rol, dummy_token)
    ventana.show()
    sys.exit(app.exec())
