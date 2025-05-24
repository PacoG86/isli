import unittest
import requests

BASE_URL = "http://localhost:8000"

class TestLoginEndpoint(unittest.TestCase):

    def test_login_valido(self):
        payload = {
            "correo": "operario1@isli.com",
            "contrasenia": "qwerty"
        }
        response = requests.post(f"{BASE_URL}/login", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["rol"], "operario")

    def test_login_invalido_password(self):
        payload = {
            "correo": "operario1@isli.com",
            "contrasenia": "incorrecta"
        }
        response = requests.post(f"{BASE_URL}/login", json=payload)
        self.assertEqual(response.status_code, 401)

    def test_login_usuario_inexistente(self):
        payload = {
            "correo": "usuario@noexiste.com",
            "contrasenia": "algo"
        }
        response = requests.post(f"{BASE_URL}/login", json=payload)
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
