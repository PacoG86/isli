import unittest
import numpy as np
import cv2
import os
import json

# Para esta prueba unitaria, hemos simulado una pequeña función equivalente a parte del flujo 
# de procesador_rollos.py
def calcular_area_mm2(imagen_binaria, pixel_mm=0.13379797308):
    """
    Calcula el área en mm² de los píxeles blancos en una imagen binaria.
    """
    area_pixels = cv2.countNonZero(imagen_binaria)
    return area_pixels * (pixel_mm ** 2)

def crear_json_resultados_mock(bboxes):
    """
    Crea una lista simulada de resultados en formato JSON a partir de bounding boxes.
    """
    resultados = []
    for bbox in bboxes:
        resultado = {
            "tipo_defecto": bbox["tipo"],
            "area_mm2": bbox["area"],
            "coordenadas": bbox["coordenadas"]
        }
        resultados.append(resultado)
    return resultados

class TestAnalisisImagenes(unittest.TestCase):

    def test_calculo_area_defecto(self):
        """Verifica que el cálculo del área sobre una región blanca sea correcto."""
        imagen = np.zeros((100, 100), dtype=np.uint8)
        cv2.rectangle(imagen, (10, 10), (20, 20), 255, -1)
        area = calcular_area_mm2(imagen)
        self.assertGreater(area, 0.0)
        self.assertAlmostEqual(area, 0.13379797308 ** 2 * 121, places=4)

    def test_creacion_json_resultado(self):
        """Valida que el JSON generado desde bounding boxes tenga el formato correcto."""
        bboxes = [{
            "tipo": "punto-negro",
            "area": 1.25,
            "coordenadas": [10, 10, 20, 20]
        }]
        resultado = crear_json_resultados_mock(bboxes)
        self.assertEqual(len(resultado), 1)
        self.assertIn("tipo_defecto", resultado[0])
        self.assertEqual(resultado[0]["tipo_defecto"], "punto-negro")

    def test_segmentacion_binaria_simulada(self):
        """Simula una segmentación binaria simple y verifica que la máscara sea coherente."""
        imagen = np.zeros((50, 50), dtype=np.uint8)
        cv2.circle(imagen, (25, 25), 5, 255, -1)
        binaria = (imagen > 200).astype(np.uint8) * 255
        self.assertEqual(cv2.countNonZero(binaria), cv2.countNonZero(imagen))

if __name__ == '__main__':
    unittest.main()
