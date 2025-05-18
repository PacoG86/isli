import os
import cv2
import json
import numpy as np
import time
import shutil

from blackspots_segmentation import BlackSpotsSegmentation

def get_detections_and_measurements_for_roll(base_path, roll_name, defect_area_threshold, pixel_to_mm_factor = 0.13379797308):

    JSON_PATH = os.path.join(base_path, "formaspack_test_black_dots.json")
    IMAGES_ROLL_PATH = os.path.join(base_path, roll_name)
    
    # Create mediciones and detecciones folders
    processed_path = os.path.join(IMAGES_ROLL_PATH, "procesado")
    originals_path = os.path.join(IMAGES_ROLL_PATH, "originales")
    os.makedirs(processed_path, exist_ok=True)
    os.makedirs(originals_path, exist_ok=True)

    print("carpetas creadas!")
    print(IMAGES_ROLL_PATH)

    filenames = os.listdir(IMAGES_ROLL_PATH)

    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    image_files = [f for f in filenames if f.lower().endswith(image_extensions)]

    with open(JSON_PATH, "r") as json_file:
        mongo_database = json.load(json_file)

    for element in mongo_database:

        if element["labelSource"] not in ["manual", "ground-truth"]:
            continue

        if element["originalFileName"] in image_files:
            
            img_path = os.path.join(IMAGES_ROLL_PATH, element["originalFileName"])
            print(img_path)
            if os.path.exists(img_path):

                image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

                bs_seg = BlackSpotsSegmentation(True)
                image_with_measurements = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)

                for crop in element["crops"]:

                    if crop["imageObjectId"] in ["punto-negro", "pegote-cascarilla"]:

                        x_init = max(0, crop["rect"]["x"])
                        y_init = max(0, crop["rect"]["y"])
                        x_fin = min(image.shape[1], crop["rect"]["x"]+crop["rect"]["w"])
                        y_fin = min(image.shape[0], crop["rect"]["y"]+crop["rect"]["h"])

                        image_crop = image[y_init:y_fin, x_init:x_fin].copy()
                        blackspots, _ = bs_seg.blackspot_segmentation_and_classification_by_size(image_crop.copy(), defect_area_threshold, pixel_to_mm_factor, False)

                        blackspots_ok, blackspots_nok = bs_seg.blackspot_filter_by_size(blackspots, defect_area_threshold, pixel_to_mm_factor)

                        image_with_measurements = bs_seg.create_visualization(image_with_measurements, blackspots_ok, blackspots_nok, pixel_to_mm_factor, crop_area = [x_init,y_init, x_fin, y_fin])

                        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackspots.astype(np.uint8))


                        with open(os.path.join(processed_path, element["originalFileName"] + '.txt'), "w") as file:

                            for idx, (area, centroid) in enumerate(zip(stats[:, cv2.CC_STAT_AREA], centroids[:])):
                                if idx == 0:
                                    continue

                                area_mm = area*pixel_to_mm_factor*pixel_to_mm_factor

                                file.write(f"{idx} {area_mm:.2f}mm2\n")

                        #image_with_measurements[y_init:y_fin, x_init:x_fin, :] = vis_img
                
                for crop in element["crops"]:

                    if crop["imageObjectId"] in ["punto-negro", "pegote-cascarilla"]:

                        image_with_measurements = bs_seg.draw_bounding_box(image_with_measurements, crop["rect"], crop["imageObjectId"])

                cv2.imwrite(os.path.join(processed_path, element["originalFileName"]), image_with_measurements)
                shutil.move(img_path, os.path.join(originals_path, element["originalFileName"]))
                        

def main(mongo_database, images_path):
    
    num_samples=0
    total_time = 0
    visualization = True
    for element in mongo_database:

        if element["labelSource"] not in ["manual", "ground-truth"]:
            continue

        
        for crop in element["crops"]:

            if crop["imageObjectId"] in ["punto-negro", "pegote-cascarilla"]:

                img_path = images_path + element["originalFileName"]

                if os.path.exists(img_path):

                    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    
                    bs_seg = BlackSpotsSegmentation(True)
                    crop_image = bs_seg.get_image_crop(image, crop["rect"])

                    #test_image = np.ones((50, 200), dtype=np.uint8) * 128
                    #test_image[10:40, 80:110] = 12                         # Adding a large defect that doesn't meet the maxAcceptableDefectArea
                    #test_image[10:15, 30:40] = 13   
                    #noise = np.random.normal(loc=0, scale=10, size=(50, 200)).astype(np.int8)
                    #noisy_image = np.clip(test_image + noise, 0, 255).astype(np.uint8)

                    #crop_image = test_image.copy()
                    start_t = time.time()
                    _, vis_img = bs_seg.blackspot_segmentation_and_classification_by_size(crop_image, 1.0, PIXEL_TO_MM, return_visualization = visualization)
                    total_time += time.time() - start_t

                    #_, vis_img = bs_seg.blackspot_segmentation(crop_image, return_visualization = True)

                    if visualization:
                        divider = np.zeros((crop_image.shape[0], 5, 3), dtype=np.uint8)
                        combined_image = cv2.hconcat([cv2.cvtColor(crop_image, cv2.COLOR_GRAY2RGB), divider, vis_img])
                        
                        cv2.imshow("Blackspot segmentation results", combined_image)
                        cv2.waitKey()
                        cv2.destroyAllWindows()
                    
                    num_samples+=1

    #print(c)
    print("Avg. time: {:2f} ms".format((total_time/num_samples)*1000.))


if __name__ == "__main__":

    IMAGES_PATH = "/Users/josematez/Downloads/ptosNegros_pegotes/all/"
    JSON_PATH = "/Users/josematez/Desktop/formaspack_test_black_dots.json"
    
    LINE = 1

    PIXEL_TO_MM_PER_LINE = {
        1: 0.13379797308,
        2: 0.11859801396,
        3: 0.09883469035,
        4: 0.11670907867,
        5: 0.1361281471
    }
    PIXEL_TO_MM = PIXEL_TO_MM_PER_LINE[LINE]

    with open(JSON_PATH, "r") as json_file:
        mongo_database = json.load(json_file)

    #PIXEL_TO_MM = PIXEL_TO_MM_PER_LINE[CURRENT_LINE]
    
    #main(mongo_database, IMAGES_PATH)

    get_detections_and_measurements_for_roll("/Users/josematez/Documents/PacoProjectFinal/ptosNegros_pegotes/", "rollo1", 1.0)
