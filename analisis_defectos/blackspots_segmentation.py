import cv2
import numpy as np
from typing import Dict, Tuple, Union
import  matplotlib.pyplot as plt
import os
import json

class BlackSpotsSegmentation:
    """ Class for black spot segmentation using dynamic binarization.
    """

    def __init__(self, visualization: bool = False):
        """

        Args:
            visualization (bool, optional): Set to true to return a visualization images which highlights the segmented defects. If filter by size is applied, it also will differentiate between acceptable and non-acceptable black spots, as well as their size in mm2. Defaults to False.
        """
        self.visualization = visualization

    @staticmethod
    def draw_bounding_box(image: np.ndarray, bbox: Dict[str, int], category: str) -> np.ndarray:
        """
        Draws a bounding box with a category label on the image.

        Args:
            image (np.ndarray): The original image.
            bbox (Dict[str, int]): Bounding box with keys "x", "y", "w", and "h".
            category (str): Category label to draw above the bounding box.

        Returns:
            np.ndarray: Image with the bounding box and label drawn.
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
        Extracts and returns a cropped portion of the input image based on the specified bounding box.

        Args:
            image (np.ndarray): The original image represented as a NumPy array.
            bbox (Dict[str, int]): A dictionary containing the bounding box coordinates with keys:
                - "x": The x-coordinate of the top-left corner.
                - "y": The y-coordinate of the top-left corner.
                - "w": The width of the bounding box.
                - "h": The height of the bounding box.

        Returns:
            np.ndarray: The cropped image as a NumPy array.
        """
        x_init = max(0, bbox["x"])
        y_init = max(0, bbox["y"])
        x_fin = min(image.shape[1], bbox["x"]+bbox["w"])
        y_fin = min(image.shape[0], bbox["y"]+bbox["h"])

        return image[y_init:y_fin, x_init:x_fin]

    @staticmethod
    def create_bimodal_histogram(image: np.ndarray[np.uint8], peak1: int = 20, peak2: int = 240, weight1: float = 0.99, weight2: float = 0.01) -> np.ndarray[np.uint8]:
        """
        Transforms a grayscale image to create a bimodal intensity distribution based on two Gaussian peaks. The goal is to enhance the contrast of the image.

        Args:
            image (np.ndarray): The input grayscale image represented as a NumPy array.
            peak1 (int, optional): The intensity value for the first Gaussian peak. Defaults to 20.
            peak2 (int, optional): The intensity value for the second Gaussian peak. Defaults to 240.
            weight1 (float, optional): The weight (contribution) of the first Gaussian peak. Defaults to 0.99.
            weight2 (float, optional): The weight (contribution) of the second Gaussian peak. Defaults to 0.01.

        Raises:
            ValueError: If the input image is not a grayscale image.

        Returns:
            np.ndarray: The transformed image with the bimodal intensity distribution applied.
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
        Creates a visualization image by overlaying binary blackspot masks on the input image. 
        The visualization highlights "OK" areas in green and "NOK" areas in red. Optionally,
        it annotates areas with size information if a pixel-to-millimeter ratio is provided.

        Args:
            image (np.ndarray[np.uint8]): The input grayscale image to be visualized.
            blackspot_binary_image_ok (np.ndarray[np.bool_]): Binary mask for "OK" blackspots. 
                Non-zero pixels represent the "OK" regions.
            blackspot_binary_image_nok (np.ndarray[np.bool_]): Binary mask for "NOK" blackspots. 
                Non-zero pixels represent the "NOK" regions.
            pixel_to_mm (float, optional): Conversion factor from pixels to millimeters. If provided, 
                the areas of the regions are annotated in the visualization.

        Returns:
            np.ndarray[np.uint8]: The visualization image with overlaid masks and optional annotations.
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
        Performs adaptive thresholding to segment blackspots in a grayscale image.

        Args:
            image (np.ndarray[np.uint8]): The input grayscale image represented as a NumPy array.

        Returns:
            np.ndarray[np.bool_]: A binary mask (boolean array) where `True` indicates blackspot regions.

        Notes:
            - The block size for adaptive thresholding is dynamically calculated as half the smaller dimension of the image,
            adjusted to ensure it is odd.
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
        Segments blackspots in a grayscale image using global thresholding with Otsu's method.

        Args:
            image (np.ndarray[np.uint8]): The input grayscale image represented as a NumPy array.

        Returns:
            np.ndarray[np.bool_]: A binary mask (boolean array) where `True` indicates blackspot regions.

        Notes:
            - Otsu's method automatically determines an optimal threshold value for the image based on its histogram.
            - The binary mask uses `True` for pixels corresponding to blackspot regions.
        """

        blur = cv2.GaussianBlur(image, (5,5), 0)

        _, blackspot_mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

        return blackspot_mask.astype(np.bool)
    
    @staticmethod
    def blackspot_filter_by_size(blackspot_binary_image: np.ndarray[np.bool_], max_acceptable_blackspot_area: float, pixel_to_mm: float) -> Tuple[np.ndarray[np.bool_], np.ndarray[np.bool_]]:
        """
        Filters blackspots in a binary image based on their area. Segments blackspots into two categories:
        one for acceptable blackspot sizes and another for oversized blackspots.

        Args:
            blackspot_binary_image (np.ndarray[np.bool_]): Binary image where `True` represents blackspot regions.
            max_acceptable_blackspot_area (float): The maximum acceptable area for blackspots, in square millimeters.
            pixel_to_mm (float): Conversion factor to map pixel area to millimeters squared.

        Returns:
            Tuple[np.ndarray[np.bool_], np.ndarray[np.bool_]]:
                - A binary mask (np.ndarray[np.bool_]) where `True` represents blackspots within the acceptable area (`blackspot_binary_image_ok`).
                - A binary mask (np.ndarray[np.bool_]) where `True` represents blackspots exceeding the maximum acceptable area (`blackspot_binary_image_nok`).
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
        Preprocesses the input image to reduce high-intensity regions and enhance its histogram for better segmentation.

        Args:
            image (np.ndarray[np.uint8]): The input grayscale image represented as a NumPy array.

        Returns:
            np.ndarray[np.uint8]: The preprocessed grayscale image after applying a low-pass filter and a bimodal histogram transformation.
        """
        
        # Low-pass filter to avoid low-intensity areas that creates a third peak in the image histogram
        median_gray = np.median(image)
        image[image > median_gray] = median_gray

        preprocessed_image = self.create_bimodal_histogram(image)
        
        return preprocessed_image

    def blackspot_segmentation(self, crop_img: np.ndarray[np.uint8], return_visualization: bool = False) -> Union[np.ndarray[np.uint8], None]:
        """
        Segments blackspots from the input cropped image. Optionally returns a visualization of the blackspot detection.

        Args:
            crop_img (np.ndarray[np.uint8]): The cropped grayscale image from which blackspots will be segmented.
            return_visualization (bool, optional): If True, returns a visualization image with the segmented blackspots marked. Defaults to False.

        Returns:
            Union[np.ndarray[np.uint8], None]: 
                - A grayscale image with the segmented blackspots (if `return_visualization` is True).
                - None if `return_visualization` is False.
        
        Notes:
            - If `return_visualization` is set to True, the function uses the `create_visualization` method to generate an annotated image
            showing the segmented blackspots.
        """

        enhanced_crop_img = self.preprocess_image(crop_img)

        blackspots_ok = self.adaptive_blackspot_segmentation(enhanced_crop_img)        

        if return_visualization:

            return blackspots_ok, self.create_visualization(crop_img, blackspots_ok, None)

        return blackspots_ok, None
    
    def blackspot_segmentation_and_classification_by_size(self, crop_img: np.ndarray[np.uint8], size_th_in_mm: float, pixel_to_mm: float, return_visualization: bool = False) -> Union[np.ndarray[np.uint8], None]:
        """
        Segments blackspots in the input cropped image, classifies them by size, and optionally returns a visualization.

        Args:
            crop_img (np.ndarray[np.uint8]): The cropped grayscale image from which blackspots will be segmented and classified.
            size_th_in_mm (float): The size threshold in millimeters to classify blackspots as acceptable or oversized.
            pixel_to_mm (float): Conversion factor from pixels to millimeters for size calculations.
            return_visualization (bool, optional): If True, returns a visualization image with the segmented blackspots and their classifications. Defaults to False.

        Returns:
            Union[np.ndarray[np.uint8], None]: 
                - A grayscale image with the segmented and classified blackspots if `return_visualization` is True.
                - None if `return_visualization` is False.

        Notes:
            - If `return_visualization` is True, the `create_visualization` method is used to display the blackspots categorized as "OK" (within size threshold) and "NOK" (exceeding size threshold).
            - The classification is based on the area of each blackspot, calculated using the `pixel_to_mm` conversion factor.
        """
        
        enhanced_crop_img = self.preprocess_image(crop_img)

        blackspots = self.adaptive_blackspot_segmentation(enhanced_crop_img)
        """
        # Find connected components
        num_labels, labels = cv2.connectedComponents(blackspots.astype(np.uint8))

        # Create an output image (with colors for each region)
        output = np.zeros((*blackspots.shape, 3), dtype=np.uint8)

        # Generate random colors for each component (excluding background)
        colors = np.random.randint(0, 255, size=(num_labels, 3), dtype=np.uint8)

        # Assign colors to each connected component
        for label in range(1, num_labels):  # Skip 0 (background)
            output[labels == label] = colors[label]

        # Show the result
        plt.figure(figsize=(8, 6))
        plt.imshow(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.title('Connected Components')
        plt.show()
        """
        blackspots_ok, blackspots_nok = self.blackspot_filter_by_size(blackspots, size_th_in_mm, pixel_to_mm)

        if return_visualization:

            return blackspots, self.create_visualization(crop_img, blackspots_ok, blackspots_nok, pixel_to_mm, offset = None)
        
        return blackspots, None
    
    
    def get_detections_and_measurements_for_roll(self, base_path, roll_name, defect_area_threshold, pixel_to_mm_factor = 0.13379797308):

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
                            