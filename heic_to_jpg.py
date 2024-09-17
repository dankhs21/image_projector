from PIL import Image
import os
import pillow_heif

directory_start = '/home/dcostello/Downloads/heic_to_jpg/images_start/'
directory_end = '/home/dcostello/Downloads/heic_to_jpg/images_end_temp/'

for filename in os.listdir(directory_start):
    if filename.lower().endswith(".heic"): 
        print("filename:",filename)
        heif_file = pillow_heif.read_heif(str(directory_start)+str(filename))
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",

        )

        image_end=str(directory_end)+str(str(filename).replace(".HEIC",".png")).replace(".heic",".png")
        image.save(image_end, format("png"))

images_folder="/home/dcostello/Downloads/heic_to_jpg/images_end_temp/"
output_folder="/home/dcostello/Downloads/heic_to_jpg/images_end_final/"

for image_path in os.listdir(images_folder):
    print(image_path)
    image_origin=images_folder+image_path
    image_future=output_folder+image_path.replace(".png",".jpg")
    with open(image_origin, 'rb') as file:
        img = Image.open(file)
        img.thumbnail((2000, 1500))
        img.save(image_future, "JPEG", optimize = True, quality = 80)
