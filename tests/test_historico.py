import unittest
import requests

BASE_URL = "http://127.0.0.1:8000"

class TestHistoricoControles(unittest.TestCase):

    def test_get_historico(self):
        params = {
            "usuario": 1  # Puedes ajustar según el ID real
        }
        response = requests.get(f"{BASE_URL}/controles/historico", params=params)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_actualizar_notas(self):
        payload = {
            "id_control": 9,  # Ajusta si necesitas uno existente
            "notas": "Comentario de prueba actualizado automáticamente"
        }
        response = requests.post(f"{BASE_URL}/controles/informe/actualizar_notas", json=payload)
        self.assertIn(response.status_code, [200, 404])  # Puede ser 404 si el ID no existe
        if response.status_code == 200:
            self.assertIn("msg", response.json())

if __name__ == "__main__":
    unittest.main()
