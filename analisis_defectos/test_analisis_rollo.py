# test_analisis_rollo.py

from procesador_rollos import analizar_rollo


if __name__ == "__main__":
    base_path = r"C:\Users\pgago\Desktop\arboles"  # carpeta donde está "rollo_03"
    rollo = "rollo_03"

    analizar_rollo(
        base_path=base_path,
        rollo=rollo,
        json_filename="formaspack_test_black_dots.json",
        area_umbral=1.0,
        pixel_to_mm=0.13379797308
    )
