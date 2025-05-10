import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QWidget
from frontend.UI.tests.login_window import Ui_Form  # Using the correct import path based on your files

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Add functionality to the login button
        self.ui.pushButton_login.clicked.connect(self.login)
        
        # Load the logo
        self.set_logo()
        
    def set_logo(self):
        # Make sure the logo file exists in the correct location
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_isli.png")
        if os.path.exists(logo_path):
            from PySide6.QtGui import QIcon
            self.ui.pushButton.setIcon(QIcon(logo_path))
    
    def login(self):
        # Get username and password
        username = self.ui.lineEdit.text()
        password = self.ui.lineEdit_3.text()
        
        # Here you would implement your login logic
        print(f"Login attempt with username: {username}")
        # For now, just print a message


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())