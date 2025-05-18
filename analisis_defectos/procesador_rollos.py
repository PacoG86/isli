# archivo: analisis_defectos/procesador_rollos.py

import os
import shutil
import json
import cv2
import numpy as np
from blackspots_segmentation import BlackSpotsSegmentation

def analizar_rollo(base_path: str, rollo: str, json_filename: str = "formaspack_test_black_dots.json", area_umbral: float = 1.0, pixel_to_mm: float = 0.13379797308):
    """
    Procesa un rollo de imágenes, generando dos carpetas:
    - 'originales': imágenes originales movidas desde el rollo.
    - 'procesado': imágenes con medidas e inspección visual.

    Args:
        base_path (str): Ruta raíz donde se encuentra el JSON y las carpetas de rollos.
        rollo (str): Nombre de la carpeta del rollo a procesar.
        json_filename (str): Nombre del archivo JSON de etiquetas.
        area_umbral (float): Área máxima tolerable para un defecto (mm2).
        pixel_to_mm (float): Conversión de píxeles a milímetros (no cambiar).
    """
    ruta_json = os.path.join(base_path, json_filename)
    ruta_rollo = os.path.join(base_path, rollo)
    carpeta_procesado = os.path.join(ruta_rollo, "procesado")
    carpeta_originales = os.path.join(ruta_rollo, "originales")

    os.makedirs(carpeta_procesado, exist_ok=True)
    os.makedirs(carpeta_originales, exist_ok=True)

    print("🔍 Analizando imágenes en:", ruta_rollo)

    with open(ruta_json, "r", encoding="utf-8") as f:
        etiquetas = json.load(f)

    nombres_imagenes = [f for f in os.listdir(ruta_rollo) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
    procesador = BlackSpotsSegmentation(True)

    for entrada in etiquetas:
        if entrada["labelSource"] not in ["manual", "ground-truth"]:
            continue

        nombre_img = entrada["originalFileName"]
        if nombre_img not in nombres_imagenes:
            continue

        ruta_img = os.path.join(ruta_rollo, nombre_img)
        imagen = cv2.imread(ruta_img, cv2.IMREAD_GRAYSCALE)
        imagen_vis = cv2.cvtColor(imagen.copy(), cv2.COLOR_GRAY2RGB)

        # Inicializar máscara para acumulación de defectos
        mascara_total = np.zeros_like(imagen, dtype=np.uint8)

        for crop in entrada.get("crops", []):
            if crop["imageObjectId"] not in ["punto-negro", "pegote-cascarilla"]:
                continue

            x1 = max(0, crop["rect"]["x"])
            y1 = max(0, crop["rect"]["y"])
            x2 = min(imagen.shape[1], x1 + crop["rect"]["w"])
            y2 = min(imagen.shape[0], y1 + crop["rect"]["h"])

            subimg = imagen[y1:y2, x1:x2].copy()
            blackspots, _ = procesador.blackspot_segmentation_and_classification_by_size(
                subimg, area_umbral, pixel_to_mm, return_visualization=False)

            # Insertar el crop segmentado en su posición original
            mascara_total[y1:y2, x1:x2] = np.logical_or(mascara_total[y1:y2, x1:x2], blackspots).astype(np.uint8)

            ok, nok = procesador.blackspot_filter_by_size(blackspots, area_umbral, pixel_to_mm)
            imagen_vis = procesador.create_visualization(imagen_vis, ok, nok, pixel_to_mm, crop_area=[x1, y1, x2, y2])

        # Dibujar bounding boxes
        for crop in entrada.get("crops", []):
            if crop["imageObjectId"] in ["punto-negro", "pegote-cascarilla"]:
                imagen_vis = procesador.draw_bounding_box(imagen_vis, crop["rect"], crop["imageObjectId"])

        # Guardar imagen visual
        cv2.imwrite(os.path.join(carpeta_procesado, nombre_img), imagen_vis)

        # Guardar archivo de mediciones
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mascara_total)
        with open(os.path.join(carpeta_procesado, nombre_img + ".txt"), "w", encoding="utf-8") as f_medidas:
            for idx, (area, centroid) in enumerate(zip(stats[:, cv2.CC_STAT_AREA], centroids[:])):
                if idx == 0:
                    continue
                area_mm = area * pixel_to_mm * pixel_to_mm
                f_medidas.write(f"{idx} {area_mm:.2f}mm2\n")

        # Mover imagen original
        shutil.move(ruta_img, os.path.join(carpeta_originales, nombre_img))

    print("✅ Análisis finalizado para:", rollo)
