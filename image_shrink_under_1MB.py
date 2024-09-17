import os
from PIL import Image
import pillow_heif

def convert_heic_to_jpeg(heic_path, jpeg_path):
    try:
        heif_file = pillow_heif.read_heif(heic_path)
        image = Image.frombytes(
            heif_file.mode, 
            heif_file.size, 
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        image.save(jpeg_path, "JPEG", quality=85)
        return True
    except Exception as e:
        print(f"Error converting {heic_path}: {str(e)}")
        return False

def resize_image(image_path, output_path, max_size_mb=1, quality=85):
    try:
        # Get the current file size in MB
        file_size = os.path.getsize(image_path) / (1024 * 1024)
        
        if file_size <= max_size_mb:
            print(f"{image_path} is already under {max_size_mb}MB. Skipping.")
            return True

        with Image.open(image_path) as img:
            # Start with original size
            width, height = img.size
            
            while file_size > max_size_mb:
                # Reduce dimensions by 10%
                width = int(width * 0.9)
                height = int(height * 0.9)
                
                # Create a temporary file to check size
                img.thumbnail((width, height), Image.LANCZOS)
                img.save(output_path, optimize=True, quality=quality)
                
                # Check new file size
                file_size = os.path.getsize(output_path) / (1024 * 1024)
            
            print(f"Resized {image_path} to {width}x{height}, new size: {file_size:.2f}MB")
            return True
    except Exception as e:
        print(f"Error resizing {image_path}: {str(e)}")
        return False

def process_directory(input_dir, output_dir, max_size_mb=1):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.heic')):
            input_path = os.path.join(input_dir, filename)
            
            if filename.lower().endswith('.heic'):
                # Convert HEIC to JPEG first
                jpeg_filename = os.path.splitext(filename)[0] + '.jpg'
                output_path = os.path.join(output_dir, jpeg_filename)
                if convert_heic_to_jpeg(input_path, output_path):
                    if resize_image(output_path, output_path, max_size_mb):
                        # Remove the original HEIC file
                        try:
                            os.remove(input_path)
                            print(f"Removed original HEIC file: {input_path}")
                        except Exception as e:
                            print(f"Error removing original HEIC file {input_path}: {str(e)}")
                    else:
                        print(f"Failed to resize converted JPEG. Keeping original HEIC file: {input_path}")
                else:
                    print(f"Failed to convert HEIC. Keeping original file: {input_path}")
            else:
                output_path = os.path.join(output_dir, filename)
                resize_image(input_path, output_path, max_size_mb)

if __name__ == "__main__":
    input_directory = "/home/dcostello/Downloads/kids_images_projector/images"
    output_directory = "/home/dcostello/Downloads/kids_images_projector/resized_images"
    max_file_size_mb = 1  # Maximum file size in MB
    
    process_directory(input_directory, output_directory, max_file_size_mb)