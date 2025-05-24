import unittest
import sys
import os

# Asegura que la raíz del proyecto esté en el path
sys.path.insert(0, os.path.abspath("."))

# Descubre y ejecuta los tests de la carpeta 'tests'
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover("tests")
    runner = unittest.TextTestRunner()
    runner.run(suite)
