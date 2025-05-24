import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import unittest
from tests.auth_testable import crear_token, verificar_contrasena, hashear_contrasena
from jose import jwt
import os

class TestAuthUtils(unittest.TestCase):

    def test_hash_y_verificacion_ok(self):
        contrasena = "prueba123"
        hash_generado = hashear_contrasena(contrasena)
        self.assertTrue(verificar_contrasena(contrasena, hash_generado))

    def test_hash_y_verificacion_fallo(self):
        contrasena = "prueba123"
        hash_generado = hashear_contrasena(contrasena)
        self.assertFalse(verificar_contrasena("otrovalor", hash_generado))

    def test_creacion_token_jwt(self):
        data = {"sub": "12", "rol": "admin", "nombre": "Paco"}
        token = crear_token(data)
        decoded = jwt.decode(token, os.getenv("SECRET_KEY", "dam202324!"), algorithms=["HS256"])
        self.assertEqual(decoded["sub"], "12")
        self.assertEqual(decoded["rol"], "admin")
        self.assertEqual(decoded["nombre"], "Paco")

if __name__ == '__main__':
    unittest.main()
