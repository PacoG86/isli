import cv2
import numpy as np
from typing import Dict, Tuple, Union
import  matplotlib.pyplot as plt
import os
import json

class BlackSpotsSegmentation:
    """
    Clase para la segmentación y visualización de defectos oscuros ("puntos negros") en imágenes industriales.

    Esta clase implementa distintos métodos para:
    - Preprocesar imágenes con transformaciones de histograma.
    - Segmentar defectos usando umbrales adaptativos o globales.
    - Clasificar los defectos por tamaño en "aceptables" y "no aceptables".
    - Generar visualizaciones con superposición de máscaras y anotaciones.

    También proporciona herramientas auxiliares para recortar imágenes, dibujar cuadros delimitadores (bounding boxes),
    y obtener mediciones asociadas a los defectos detectados.
    """

    def __init__(self, visualization: bool = False):
        """
        Inicializa la clase con una opción para activar o desactivar la visualización.

        Args:
            visualization (bool): Si se establece en True, los métodos que lo soporten
                devolverán imágenes con superposición visual de los defectos segmentados.
                Si se aplica filtrado por tamaño, las visualizaciones también diferenciarán
                entre defectos aceptables y no aceptables, incluyendo su área en mm².
        """
        self.visualization = visualization

    @staticmethod
    def draw_bounding_box(image: np.ndarray, bbox: Dict[str, int], category: str) -> np.ndarray:
        """
        Dibuja un recuadro delimitador (bounding box) con una etiqueta de categoría sobre una imagen.

        Este método se utiliza para resaltar visualmente regiones de interés (defectos detectados)
        sobre una imagen, agregando además una etiqueta con el nombre de la categoría.

        Args:
            image (np.ndarray): Imagen original sobre la que se dibujará el recuadro.
            bbox (Dict[str, int]): Diccionario con las coordenadas del recuadro. Debe contener:
                - "x": coordenada horizontal del vértice superior izquierdo.
                - "y": coordenada vertical del vértice superior izquierdo.
                - "w": ancho del recuadro.
                - "h": alto del recuadro.
            category (str): Etiqueta de texto que se mostrará encima del recuadro (ej. "punto-negro").

        Returns:
            np.ndarray: Imagen con el recuadro y la etiqueta superpuestos.
        """
        x, y, w, h = bbox["x"], bbox["y"], bbox["w"], bbox["h"]

        # Make a copy to avoid modifying the original
        image_with_box = image.copy()

        # Bounding box coordinates
        start_point = (x, y)
        end_point = (x + w, y + h)

        # Box settings
        box_color = (255, 255, 255)  # Green
        thickness = 2

        # Draw the bounding box
        cv2.rectangle(image_with_box, start_point, end_point, box_color, thickness)

        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        text_thickness = 1
        text_color = (0, 255, 0)

        # Get text size to draw a background rectangle if needed
        (text_width, text_height), baseline = cv2.getTextSize(category, font, font_scale, text_thickness)
        text_origin = (x, y - 0 if y - 0 > text_height else y + text_height + 0)

        # Optional: Draw background rectangle for better visibility
        cv2.rectangle(image_with_box, (text_origin[0], text_origin[1] - text_height),
                    (text_origin[0] + text_width, text_origin[1] + baseline), box_color, -1)

        # Draw the category text
        cv2.putText(image_with_box, category, text_origin, font, font_scale, (0, 0, 0), text_thickness, cv2.LINE_AA)

        return image_with_box

    @staticmethod
    def get_image_crop(image: np.ndarray[np.uint8], bbox: Dict[str, int]) -> np.ndarray[np.uint8]:
        """
        Extrae y devuelve una región recortada de la imagen original según un bounding box.

        Este método permite aislar una sección rectangular de la imagen especificada
        por las coordenadas y dimensiones indicadas en el diccionario `bbox`.

        Args:
            image (np.ndarray): Imagen de entrada (en escala de grises o RGB).
            bbox (Dict[str, int]): Diccionario con las coordenadas del recorte. Debe incluir:
                - "x": coordenada horizontal del vértice superior izquierdo.
                - "y": coordenada vertical del vértice superior izquierdo.
                - "w": ancho del recorte.
                - "h": alto del recorte.

        Returns:
            np.ndarray: Imagen recortada según las coordenadas especificadas.
        """
        x_init = max(0, bbox["x"])
        y_init = max(0, bbox["y"])
        x_fin = min(image.shape[1], bbox["x"]+bbox["w"])
        y_fin = min(image.shape[0], bbox["y"]+bbox["h"])

        return image[y_init:y_fin, x_init:x_fin]

    @staticmethod
    def create_bimodal_histogram(image: np.ndarray[np.uint8], peak1: int = 20, peak2: int = 240, weight1: float = 0.99, weight2: float = 0.01) -> np.ndarray[np.uint8]:
        """
        Transforma una imagen en escala de grises para generar una distribución bimodal de intensidades.

        Esta transformación sirve para aumentar el contraste de la imagen antes de aplicar técnicas
        de segmentación. Utiliza dos curvas gaussianas con pesos diferentes para modificar la 
        distribución de histograma.

        Args:
            image (np.ndarray): Imagen de entrada en escala de grises.
            peak1 (int): Pico de intensidad principal de la primera gaussiana (más oscura). Por defecto 20.
            peak2 (int): Pico de intensidad de la segunda gaussiana (más clara). Por defecto 240.
            weight1 (float): Peso relativo de la primera gaussiana. Por defecto 0.99.
            weight2 (float): Peso relativo de la segunda gaussiana. Por defecto 0.01.

        Raises:
            ValueError: Si la imagen no está en escala de grises.

        Returns:
            np.ndarray: Imagen resultante con distribución de intensidades bimodal.
        """
        if len(image.shape) > 2:
            raise ValueError("Input image must be a grayscale image.")

        normalized_image = image / 255.0

        transformation = np.zeros(256, dtype=np.float32)
        for i in range(256):
            t1 = weight1 * np.exp(-((i - peak1) ** 2) / (2 * (30 ** 2))) 
            t2 = weight2 * np.exp(-((i - peak2) ** 2) / (2 * (60 ** 2))) 
            transformation[i] = t1 + t2

        transformation /= np.sum(transformation)

        cdf = np.cumsum(transformation)
        cdf_normalized = cdf / cdf[-1]

        output_image = np.interp(normalized_image.ravel(), np.linspace(0, 1, 256), cdf_normalized)
        output_image = (output_image * 255).astype('uint8').reshape(image.shape)

        return output_image

    @staticmethod
    def create_visualization(image: np.ndarray[np.uint8], blackspot_binary_image_ok: np.ndarray[np.bool_], blackspot_binary_image_nok: np.ndarray[np.bool_], pixel_to_mm: float = None, crop_area = None) -> np.ndarray[np.uint8]:
        """
        Crea una visualización superponiendo máscaras de defectos sobre la imagen original.

        Este método genera una imagen RGB a partir de una imagen de entrada (en escala de grises o RGB),
        donde se resaltan los defectos clasificados como:
        - OK (dentro del umbral de tamaño): en verde.
        - NOK (fuera del umbral de tamaño): en rojo.

        Si se proporciona el factor `pixel_to_mm`, se anotan también las áreas de cada defecto en mm².
        Además, se puede limitar la visualización a un área concreta mediante `crop_area`.

        Args:
            image (np.ndarray): Imagen original en escala de grises o RGB.
            blackspot_binary_image_ok (np.ndarray): Máscara binaria de defectos aceptables ("OK").
            blackspot_binary_image_nok (np.ndarray): Máscara binaria de defectos no aceptables ("NOK").
            pixel_to_mm (float, opcional): Factor de conversión de píxeles a milímetros. Si se proporciona,
                se muestran etiquetas con el área de cada defecto detectado.
            crop_area (list[int], opcional): Área de recorte sobre la que aplicar las máscaras, en formato [x1, y1, x2, y2].
                Si no se proporciona, se aplica a toda la imagen.

        Returns:
            np.ndarray: Imagen visual resultante con superposición de defectos y anotaciones (si aplica).
        """

        if crop_area == None:
            x_init = 0
            y_init = 0
        else:
            x_init = crop_area[0]
            y_init = crop_area[1]
            x_fin = crop_area[2]
            y_fin = crop_area[3]

        if len(image.shape) == 2:
            visualization_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            visualization_img = image.copy()

        if blackspot_binary_image_nok is not None:

            if crop_area == None:
                visualization_img[blackspot_binary_image_nok] = [0, 0, 255]
            else:
                visualization_img[y_init:y_fin, x_init:x_fin][blackspot_binary_image_nok] = [0, 0, 255]

            if pixel_to_mm is not None:
                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackspot_binary_image_nok.astype(np.uint8))
                for idx, (area, centroid) in enumerate(zip(stats[:, cv2.CC_STAT_AREA], centroids[:])):
                    if idx == 0:
                        continue

                    cv2.putText(visualization_img, "{:.2f}mm2".format(area*pixel_to_mm*pixel_to_mm), (int(centroid[0])+x_init, int(centroid[1])+y_init), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)

        if blackspot_binary_image_ok is not None:

            if crop_area == None:
                visualization_img[blackspot_binary_image_nok] = [0, 255, 0]
            else:
                visualization_img[y_init:y_fin, x_init:x_fin][blackspot_binary_image_ok] = [0, 255, 0]

            if pixel_to_mm is not None:
                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackspot_binary_image_ok.astype(np.uint8))
                for idx, (area, centroid) in enumerate(zip(stats[:, cv2.CC_STAT_AREA], centroids[:])):
                    if idx == 0:
                        continue

                    cv2.putText(visualization_img, "{:.2f}mm2".format(area*pixel_to_mm*pixel_to_mm), (int(centroid[0])+x_init, int(centroid[1])+y_init), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)


        return visualization_img

    @staticmethod
    def adaptive_blackspot_segmentation(image: np.ndarray[np.uint8]) -> np.ndarray[np.bool_]:
        """
        Aplica umbralización adaptativa para segmentar defectos oscuros (blackspots) en una imagen en escala de grises.

        Esta técnica ajusta el umbral dinámicamente en función de las regiones locales de la imagen,
        lo que permite una detección más precisa en condiciones de iluminación no uniforme.

        Args:
            image (np.ndarray[np.uint8]): Imagen de entrada en escala de grises.

        Returns:
            np.ndarray[np.bool_]: Máscara binaria donde los píxeles `True` indican regiones con posibles defectos.
        
        Notas:
            - El tamaño del bloque para la umbralización se calcula como la mitad del menor lado de la imagen,
            y se ajusta para que siempre sea impar.
            - Se aplica un desenfoque Gaussiano previo para reducir ruido.
        """

        blur = cv2.GaussianBlur(image, (5,5), 0)
        
        block_size = min(image.shape[0], image.shape[1]) // 2
        #block_size = min(image.shape[0], image.shape[1])
        if block_size % 2 == 0:
            block_size -= 1

        blackspot_mask = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY_INV,block_size,2)

        return blackspot_mask.astype(np.bool)

    @staticmethod
    def global_blackspot_segmentation(image: np.ndarray[np.uint8]) -> np.ndarray[np.bool_]:
        """
        Segmenta defectos oscuros en una imagen en escala de grises utilizando umbralización global con el método de Otsu.

        Este método determina automáticamente un umbral óptimo de binarización analizando el histograma
        de la imagen. Es útil en condiciones de iluminación homogénea donde una separación clara entre
        fondo y defecto es posible.

        Args:
            image (np.ndarray[np.uint8]): Imagen de entrada en escala de grises.

        Returns:
            np.ndarray[np.bool_]: Máscara binaria donde los píxeles `True` representan regiones detectadas como defectos.

        Notas:
            - Se aplica un filtro Gaussiano previo para suavizar la imagen y reducir el ruido.
            - Otsu determina el umbral que minimiza la varianza intra-clase de intensidades.
        """

        blur = cv2.GaussianBlur(image, (5,5), 0)

        _, blackspot_mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

        return blackspot_mask.astype(np.bool)
    
    @staticmethod
    def blackspot_filter_by_size(blackspot_binary_image: np.ndarray[np.bool_], max_acceptable_blackspot_area: float, pixel_to_mm: float) -> Tuple[np.ndarray[np.bool_], np.ndarray[np.bool_]]:
        """
        Clasifica los defectos detectados en una imagen binaria según su tamaño.

        Esta función recorre los componentes conectados de la imagen binaria (`blackspot_binary_image`)
        y los separa en dos máscaras:
        - Una con los defectos aceptables (OK) cuyo área está por debajo del umbral.
        - Otra con los defectos no aceptables (NOK) que superan el área máxima permitida.

        Args:
            blackspot_binary_image (np.ndarray[np.bool_]): Imagen binaria donde los píxeles `True` representan defectos detectados.
            max_acceptable_blackspot_area (float): Área máxima tolerable para un defecto, en milímetros cuadrados.
            pixel_to_mm (float): Factor de conversión de píxeles a milímetros.

        Returns:
            Tuple[np.ndarray[np.bool_], np.ndarray[np.bool_]]:
                - Primera máscara binaria con los defectos aceptables ("OK").
                - Segunda máscara binaria con los defectos no aceptables ("NOK").

        Notas:
            - La segmentación se basa en el área de cada componente conectado.
            - El área en mm² se calcula como: `área en píxeles * pixel_to_mm²`.
        """

        blackspot_binary_image_ok = np.zeros(blackspot_binary_image.shape).astype(np.bool)
        blackspot_binary_image_nok = np.zeros(blackspot_binary_image.shape).astype(np.bool)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackspot_binary_image.astype(np.uint8))

        for idx, (area, centroid) in enumerate(zip(stats[:, cv2.CC_STAT_AREA], centroids[:])):
            if idx == 0:
                continue

            #x_init = stats[idx, cv2.CC_STAT_LEFT]
            #y_init = stats[idx, cv2.CC_STAT_TOP]
            #x_fin = x_init + stats[idx, cv2.CC_STAT_WIDTH]
            #y_fin = y_init + stats[idx, cv2.CC_STAT_HEIGHT]
            #cv2.rectangle(original_image, (x_init, y_init), (x_fin, y_fin), (0, 255, 0), 2)
            #print(gray_cropped_black_dots[y_init:y_fin, x_init:x_fin,].mean(), gray_cropped_black_dots[y_init:y_fin, x_init:x_fin,].std())
            #if gray_cropped_black_dots[y_init:y_fin, x_init:x_fin,].std() < 4.0 and gray_cropped_black_dots[y_init:y_fin, x_init:x_fin,].mean() > 120:
            #    continue
            
            if area*pixel_to_mm*pixel_to_mm >= max_acceptable_blackspot_area:

                blackspot_binary_image_nok[labels == idx] = True
            
            else:

                blackspot_binary_image_ok[labels == idx] = True

                #cv2.putText(annotated_image, str(area*pixel_area_in_mm), (int(centroid[0]), int(centroid[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)


        return blackspot_binary_image_ok, blackspot_binary_image_nok

    def preprocess_image(self, image: np.ndarray[np.uint8]) -> np.ndarray[np.uint8]:
        """
        Preprocesa una imagen en escala de grises para mejorar la segmentación de defectos.

        Este método reduce la intensidad de las regiones muy brillantes, que podrían generar
        un tercer pico no deseado en el histograma, y aplica una transformación para forzar
        una distribución bimodal de intensidades.

        Args:
            image (np.ndarray[np.uint8]): Imagen original en escala de grises.

        Returns:
            np.ndarray[np.uint8]: Imagen preprocesada lista para segmentación.
        
        Notas:
            - Se limita la intensidad máxima al valor de la mediana para eliminar saturaciones.
            - Luego se aplica `create_bimodal_histogram()` para aumentar el contraste local.
        """
        
        # Low-pass filter to avoid low-intensity areas that creates a third peak in the image histogram
        median_gray = np.median(image)
        image[image > median_gray] = median_gray

        preprocessed_image = self.create_bimodal_histogram(image)
        
        return preprocessed_image

    def blackspot_segmentation(self, crop_img: np.ndarray[np.uint8], return_visualization: bool = False) -> Union[np.ndarray[np.uint8], None]:
        """
        Segmenta defectos en una imagen recortada utilizando umbralización adaptativa.

        Esta función aplica preprocesado sobre una subimagen (crop) y segmenta posibles defectos.
        Si se indica `return_visualization=True`, devuelve también una imagen anotada visualmente.

        Args:
            crop_img (np.ndarray[np.uint8]): Imagen recortada en escala de grises sobre la que se aplicará la segmentación.
            return_visualization (bool): Si es True, devuelve también una visualización de los defectos segmentados.

        Returns:
            Union[np.ndarray[np.uint8], Tuple[np.ndarray, np.ndarray]]:
                - Si `return_visualization` es False: máscara binaria con los defectos segmentados.
                - Si es True: tupla con (máscara segmentada, visualización con superposición).

        Notas:
            - Utiliza el método `preprocess_image` para mejorar el contraste antes de segmentar.
            - La segmentación se realiza con umbralización adaptativa.
        """

        enhanced_crop_img = self.preprocess_image(crop_img)

        blackspots_ok = self.adaptive_blackspot_segmentation(enhanced_crop_img)        

        if return_visualization:

            return blackspots_ok, self.create_visualization(crop_img, blackspots_ok, None)

        return blackspots_ok, None
    
    def blackspot_segmentation_and_classification_by_size(self, crop_img: np.ndarray[np.uint8], size_th_in_mm: float, pixel_to_mm: float, return_visualization: bool = False) -> Union[np.ndarray[np.uint8], None]:
        """
        Segmenta y clasifica defectos por tamaño en una imagen recortada.

        Esta función realiza segmentación de defectos oscuros (puntos negros), los clasifica
        como aceptables (OK) o no aceptables (NOK) en función de un umbral de área, y
        opcionalmente genera una visualización anotada.

        Args:
            crop_img (np.ndarray[np.uint8]): Imagen recortada (crop) en escala de grises.
            size_th_in_mm (float): Umbral de área (en mm²) para considerar un defecto como no aceptable.
            pixel_to_mm (float): Factor de conversión de píxeles a milímetros.
            return_visualization (bool): Si es True, se devuelve también una imagen con la visualización de los defectos clasificados.

        Returns:
            Union[np.ndarray[np.uint8], Tuple[np.ndarray, np.ndarray]]:
                - Máscara binaria con todos los defectos segmentados.
                - Si `return_visualization` es True, también se devuelve una visualización RGB con la clasificación OK/NOK superpuesta.

        Notas:
            - Este método combina `preprocess_image`, `adaptive_blackspot_segmentation`,
            `blackspot_filter_by_size` y `create_visualization`.
            - Es adecuado cuando se desea inspección automática con criterio de tamaño.
        """
        
        enhanced_crop_img = self.preprocess_image(crop_img)

        blackspots = self.adaptive_blackspot_segmentation(enhanced_crop_img)
        
        blackspots_ok, blackspots_nok = self.blackspot_filter_by_size(blackspots, size_th_in_mm, pixel_to_mm)

        if return_visualization:

            return blackspots, self.create_visualization(crop_img, blackspots_ok, blackspots_nok, pixel_to_mm, offset = None)
        
        return blackspots, None
    
    
    def get_detections_and_measurements_for_roll(self, base_path, roll_name, defect_area_threshold, pixel_to_mm_factor = 0.13379797308):

        """
        Aplica segmentación y medición de defectos sobre todas las imágenes de un rollo.

        Este método recorre todas las imágenes en la carpeta de un rollo determinado,
        identifica las regiones etiquetadas como defectos en el archivo JSON de anotaciones,
        y genera dos salidas por cada imagen:
        - Una imagen con los defectos marcados mediante bounding boxes.
        - Una imagen con la segmentación y medición de cada defecto detectado.

        Args:
            base_path (str): Ruta raíz donde se encuentran el archivo JSON y la carpeta del rollo.
            roll_name (str): Nombre de la carpeta del rollo a procesar.
            defect_area_threshold (float): Área máxima aceptable para un defecto, en mm².
            pixel_to_mm_factor (float): Factor de conversión de píxeles a milímetros cuadrados. Por defecto 0.13379797308.

        Efectos:
            - Crea dos carpetas dentro del rollo: `detecciones` y `mediciones`.
            - Guarda imágenes con resultados visuales del análisis para cada muestra.
        """
        JSON_PATH = os.path.join(base_path, "formaspack_test_black_dots.json")
        IMAGES_ROLL_PATH = os.path.join(base_path, roll_name)

        # Create mediciones and detecciones folders
        detecciones_path = os.path.join(IMAGES_ROLL_PATH, "detecciones")
        mediciones_path = os.path.join(IMAGES_ROLL_PATH, "mediciones")

        filenames = os.listdir(IMAGES_ROLL_PATH)

        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        image_files = [f for f in filenames if f.lower().endswith(image_extensions)]

        with open(JSON_PATH, "r") as json_file:
            mongo_database = json.load(json_file)

        for element in mongo_database:

            if element["labelSource"] not in ["manual", "ground-truth"]:
                continue

            if element["originalFileName"] in image_files:
                
                img_path = IMAGES_ROLL_PATH + element["originalFileName"]

                if os.path.exists(img_path):
                    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

                    bs_seg = BlackSpotsSegmentation(True)

                    image_with_bbox = image.copy()
                    image_with_measurements = image.copy()

                    for crop in element["crops"]:

                        if crop["imageObjectId"] in ["punto-negro", "pegote-cascarilla"]:

                            image_with_bbox = self.draw_bounding_box(image_with_bbox, crop["rect"], crop["imageObjectId"])

                            x_init = max(0, crop["rect"]["x"])
                            y_init = max(0, crop["rect"]["y"])
                            x_fin = min(image.shape[1], crop["rect"]["x"]+crop["rect"]["w"])
                            y_fin = min(image.shape[0], crop["rect"]["y"]+crop["rect"]["h"])

                            _, vis_img = bs_seg.blackspot_segmentation_and_classification_by_size(image_with_measurements[y_init:y_fin, x_init:x_fin].copy(), defect_area_threshold, pixel_to_mm_factor, True)
                            image_with_measurements[y_init:y_fin, x_init:x_fin] = vis_img

                    cv2.imwrite(os.path.join(detecciones_path, element["originalFileName"]), image_with_bbox)
                    cv2.imwrite(os.path.join(mediciones_path, element["originalFileName"]), image_with_measurements)
                            