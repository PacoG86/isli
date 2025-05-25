"""Funciones utilitarias para la interfaz gráfica del sistema ISLI.

Incluye lógica compartida entre ventanas PySide6 como:
- Mostrar datos de usuario.
- Configurar botones comunes según el rol.
- Logout con mensaje de despedida.
- Acceso al panel de control, manual de usuario o ID de control.
"""
from PySide6.QtWidgets import QMessageBox
import webbrowser
import json
from PySide6.QtCore import QTimer
import urllib.request
import sys
import os

CONFIG_FILE = "config.json"

def guardar_config_ruta(ruta):
    """
    Guarda en disco la ruta base de los rollos en un archivo JSON de configuración.
    """
    try:
        CONFIG_FILE = "config.json"

        # Leer configuración actual si existe
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {}

        # Modificar solo la clave deseada
        config["base_folder"] = ruta

        # Guardar la nueva configuración
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error al guardar config: {e}")


def cargar_config_ruta():
        """Carga la ruta base de los rollos desde el archivo config.json (si existe)."""
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("base_folder", "")
        except FileNotFoundError:
            return ""

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
                print("ID inválido recibido.")
                getattr(ui, label_name).setText("-----")
                return False
        else:
            print(f"Error HTTP {response.status_code}")
            getattr(ui, label_name).setText("Error")
            return False
    except Exception as e:
        print(f"Error obteniendo ID de control: {e}")
        getattr(ui, label_name).setText("N/A")
        return False


def configurar_botones_comunes(parent, ui, rol_usuario, token_jwt):
    """
    Conecta los botones de panel de control, manual de usuario y logout.
    Desactiva el botón de panel si el rol no es administrador.
    """
    ui.pushButton_3.clicked.connect(lambda: logout(parent))
    ui.pushButton_manual.clicked.connect(abrir_manual_usuario)


    if rol_usuario != "administrador":
        ui.pushButton_pcontrol.setEnabled(False)
        ui.pushButton_gAlmacen.setEnabled(False)
    else:
        print(f"🌐 Abriendo panel admin con token: {token_jwt}")
        ui.pushButton_pcontrol.clicked.connect(lambda: webbrowser.open(f"http://localhost:8000/admin?token={token_jwt}"))


def logout(parent):
    """
    Muestra un diálogo de cierre de sesión con opciones de confirmación, 
    incluyendo cierre, cancelación o inicio de nueva sesión.
    """
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

        # Guardar como atributo persistente para que no se destruya
        parent.login_window = LoginWindow()
        parent.login_window.show()


def hay_conexion_internet(url="http://www.google.com", timeout=3):
    """Verifica si hay conexión a internet intentando abrir una URL."""
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception:
        return False

def abrir_manual_usuario():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            ruta_pdf_local = config.get("ruta_manual_usuario", "")
    except Exception as e:
        print(f"Error leyendo configuración del manual: {e}")
        ruta_pdf_local = ""

    url_online = "https://github.com/PacoG86/isli/blob/dev/README.md"

    if hay_conexion_internet():
        print("Conexión detectada. Abriendo manual online...")
        webbrowser.open(url_online)
    elif ruta_pdf_local:
        print("Sin conexión. Abriendo manual local en PDF...")
        try:
            if sys.platform.startswith('darwin'):
                os.system(f"open '{ruta_pdf_local}'")
            elif os.name == 'nt':
                os.startfile(ruta_pdf_local)
            elif os.name == 'posix':
                os.system(f"xdg-open '{ruta_pdf_local}'")
        except Exception as e:
            print(f"Error al abrir el manual local: {e}")
    else:
        print("No se encontró ruta del manual local.")


def obtener_ruta_informes():
    """
    Devuelve la ruta donde se deben guardar los informes PDF.
    Si no se encuentra en config.json, devuelve una ruta por defecto en el escritorio.
    """
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                ruta = config.get("ruta_informes")
                if ruta and os.path.exists(ruta):
                    return ruta
    except Exception as e:
        print(f"Error al cargar config.json: {e}")

    # Ruta por defecto: Escritorio/historico
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    ruta_por_defecto = os.path.join(escritorio, "historico")
    os.makedirs(ruta_por_defecto, exist_ok=True)
    return ruta_por_defecto
