import unittest
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

class TestGuardarResultados(unittest.TestCase):

    def test_guardar_control_calidad(self):
        """
        Verifica que el endpoint /controles/nuevo guarda correctamente un control
        de calidad cuando se le envía un payload válido.
        """
        payload = {
            "id_usuario": 1,
            "umbral_tamano_defecto": "0.50",
            "num_defectos_tolerables_por_tamano": 3,
            "fecha_control": datetime.now().isoformat(),
            "rollo": {
                "ruta_local_rollo": "C:/imagenes/rollo_prueba",
                "nombre_rollo": "rollo_prueba",
                "num_defectos_rollo": 2,
                "total_defectos_intolerables_rollo": 1,
                "resultado_rollo": "nok",
                "orden_analisis": 1
            },
            "imagenes": [
                {
                    "nombre_archivo": "img_001.png",
                    "fecha_captura": datetime.now().isoformat(),
                    "max_dim_defecto_medido": "0.70",
                    "min_dim_defecto_medido": "0.45",
                    "clasificacion": "nok",
                    "defectos": [
                        {
                            "area": "0.72",
                            "tipo_valor": "max",
                            "tipo_defecto": "punto-negro"
                        }
                    ]
                }
            ]
        }

        response = requests.post(f"{BASE_URL}/controles/nuevo", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id_control", response.json())

if __name__ == "__main__":
    unittest.main()
