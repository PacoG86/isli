import unittest
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend")))
from frontend.utils_ui import guardar_config_ruta

CONFIG_PATH = "config.json"

class TestConfiguracionRutaAlmacen(unittest.TestCase):

    def test_guardar_ruta_con_funcion_real(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config_original = json.load(f)

        ruta_original = config_original.get("base_folder", "")
        nueva_ruta = "C:/Users/pgago/Desktop/test_guardado_ruta"

        guardar_config_ruta(nueva_ruta)

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config_actualizado = json.load(f)

        self.assertEqual(config_actualizado.get("base_folder"), nueva_ruta)

        guardar_config_ruta(ruta_original)

if __name__ == "__main__":
    unittest.main()