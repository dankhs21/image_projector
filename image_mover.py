import os
import shutil

def move_images(source_dir, destination_dir):
    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Walk through the source directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # Check if the file has an image extension
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
                # Construct the full file paths
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_dir, file)

                # Move the file
                shutil.move(source_path, destination_path)
                print(f"Moved: {source_path} -> {destination_path}")

# Example usage
source_directory = "/home/dcostello/Downloads/all_kids_images"
destination_directory = "/home/dcostello/Downloads/daniel_images_projector/images"

move_images(source_directory, destination_directory)