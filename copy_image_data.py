import os
import shutil
import paths

# for copying all image folder with a certain name structure into one folder 

def copy_and_rename_folders(copy_type, runtype, dest_dir):
    # Create the destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Iterate over each item in the source directory
    for item in os.listdir(paths.to_personal_data()):
        source_item_path = os.path.join(paths.to_personal_data(), item)

        # Check if the item is a directory
        if os.path.isdir(source_item_path) and runtype in source_item_path:
            print(source_item_path)
            Intensity_value = "_".join(source_item_path.split('_')[-2:])
            images_folder = source_item_path+'/images/electron_temperature_tev_Heatmap.png'


            # Generate a new name for the directory
            new_folder_name = f"(n,l)={Intensity_value}"

            # Create the path for the new directory in the destination directory
            dest_item_path = os.path.join(dest_dir, new_folder_name)

            # Copy the directory from the source to the destination, renaming it
            
            if copy_type == 'dir':
                shutil.copytree(images_folder, dest_item_path)
            elif copy_type == 'img':
                shutil.copy(images_folder, dest_item_path)

            print(f"Folder '{item}' copied and renamed to '{new_folder_name}'")

# Example usage:

destination_directory = "/home/brewster/Desktop/temp_images"

copy_and_rename_folders('img','Howard_scott36', destination_directory)