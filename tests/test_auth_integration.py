import unittest
import requests

BASE_URL = "http://localhost:8000"

class TestLoginEndpoint(unittest.TestCase):

    def test_login_valido(self):
        """Verifica que un usuario válido obtiene un token y rol correctos."""
        payload = {
            "correo": "admin1@isli.com",
            "contrasenia": "Admin!123"
        }
        response = requests.post(f"{BASE_URL}/login", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["rol"], "administrador")

    def test_login_invalido_password(self):
        """Verifica que una contraseña incorrecta devuelve error 401."""
        payload = {
            "correo": "operario1@isli.com",
            "contrasenia": "incorrecta"
        }
        response = requests.post(f"{BASE_URL}/login", json=payload)
        self.assertEqual(response.status_code, 401)

    def test_login_usuario_inexistente(self):
        """Verifica que un usuario no registrado no puede iniciar sesión."""
        payload = {
            "correo": "usuario@noexiste.com",
            "contrasenia": "algo"
        }
        response = requests.post(f"{BASE_URL}/login", json=payload)
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
