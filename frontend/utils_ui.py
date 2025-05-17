from PySide6.QtWidgets import QMessageBox
import webbrowser
from PySide6.QtCore import QTimer


def mostrar_datos_usuario(ui, nombre_usuario, rol_usuario):
    """
    Muestra el nombre de usuario y rol en la etiqueta correspondiente de la barra lateral.
    """
    ui.label_3.setText(f"{nombre_usuario} ({rol_usuario})")

import requests

def mostrar_siguiente_id_control(ui, label_name="label_11"):
    """
    Obtiene el siguiente ID de control desde el backend y lo muestra en el QLabel indicado.
    """
    try:
        response = requests.get("http://localhost:8000/controles/ultimo_id_control")
        if response.status_code == 200:
            data = response.json()
            siguiente_id = data.get("siguiente_id")
            if isinstance(siguiente_id, int):
                getattr(ui, label_name).setText(f"{siguiente_id:05d}")
                return True
            else:
                print("⚠️ ID inválido recibido.")
                getattr(ui, label_name).setText("-----")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            getattr(ui, label_name).setText("Error")
            return False
    except Exception as e:
        print(f"❌ Error obteniendo ID de control: {e}")
        getattr(ui, label_name).setText("N/A")
        return False


def configurar_botones_comunes(parent, ui, rol_usuario, token_jwt):
    """
    Conecta los botones de panel de control, manual de usuario y logout.
    Desactiva el botón de panel si el rol no es administrador.
    """
    ui.pushButton_manual.clicked.connect(lambda: webbrowser.open("manual_usuario.pdf"))
    ui.pushButton_3.clicked.connect(lambda: logout(parent))

    if rol_usuario != "administrador":
        ui.pushButton_pcontrol.setEnabled(False)
    else:
        ui.pushButton_pcontrol.clicked.connect(lambda: webbrowser.open(f"http://localhost:8000/admin?token={token_jwt}"))


def logout(parent):
    from main import LoginWindow

    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Cerrar sesión")
    msg_box.setText("¿Está seguro que desea cerrar sesión?")
    msg_box.setIcon(QMessageBox.Question)

    btn_yes = msg_box.addButton("Sí", QMessageBox.YesRole)
    btn_no = msg_box.addButton("No", QMessageBox.NoRole)
    btn_new_session = msg_box.addButton("Abrir nueva sesión", QMessageBox.AcceptRole)

    msg_box.exec()
    clicked_button = msg_box.clickedButton()

    if clicked_button == btn_yes:
        despedida = QMessageBox(parent)
        despedida.setWindowTitle("Gracias")
        despedida.setText("Muchas gracias por confiar en ISLI.\n¡Hasta pronto!")
        despedida.setIcon(QMessageBox.Information)
        despedida.setStandardButtons(QMessageBox.NoButton)

        def cerrar_y_salir():
            despedida.done(0)
            parent.close()

        QTimer.singleShot(2000, cerrar_y_salir)
        despedida.exec()

    elif clicked_button == btn_no:
        return

    elif clicked_button == btn_new_session:
        parent.hide()

        # ⬇️ Guardar como atributo persistente para que no se destruya
        parent.login_window = LoginWindow()
        parent.login_window.show()
