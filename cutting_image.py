# this file is for cutting images in a consistent manner so that they look nice in the paper


from PIL import Image
import os

def crop_images_in_directory(input_directory:str, output_directory:str, crop_delimitters:tuple, signature:str):
    print(signature)
    for filename in os.listdir(input_directory):
        if filename.endswith(".png") and signature in filename:
            print(filename)
            with Image.open(os.path.join(input_directory, filename)) as img:
                cropped_img = img.crop(crop_delimitters)  # Crop the image
                cropped_img.save(os.path.join(output_directory, filename))  # Save the cropped image


# Specify the directory containing your images and where to save them
input_dir = 'C:\\Users\\bowie\\OneDrive\\Desktop\\cutting'
output_dir = 'C:\\Users\\bowie\\OneDrive\\Desktop\\cutting\\output'

# Specify the crop area (left, top, right, bottom)
crop_area1 = (95, 70, 1350, 1365) #A
crop_area2 = (80, 170, 470, 425) #E

crop_area3 = (80, 170, 470, 425) #I


crop_images_in_directory(input_dir, output_dir, crop_area1, 'E')
crop_images_in_directory(input_dir, output_dir, crop_area2, 'A')
crop_images_in_directory(input_dir, output_dir, crop_area3, 'I')