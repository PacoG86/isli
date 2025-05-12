# archivo: frontend/historico_controles_app.py

import sys
from PySide6.QtWidgets import QApplication, QWidget
from UI.historico_controles import Ui_Form_historico

class HistoricoControlesWindow(QWidget):  # 👈 QWidget en lugar de QMainWindow
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form_historico()
        self.ui.setupUi(self)
        self.setWindowTitle("Histórico de Controles")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = HistoricoControlesWindow()
    ventana.show()
    sys.exit(app.exec())
