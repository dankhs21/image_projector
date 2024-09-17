import os
import sys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image
import pillow_heif

def debug_info():
    print("Python version:", sys.version)
    print("Operating System:", os.name, "-", sys.platform)
    print("Firefox path:", subprocess.getoutput("which firefox"))
    print("Firefox version:", subprocess.getoutput("firefox --version"))
    print("Geckodriver path:", subprocess.getoutput("which geckodriver"))
    print("Geckodriver version:", subprocess.getoutput("geckodriver --version"))

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
        image.save(jpeg_path, "JPEG")
        return True
    except Exception as e:
        print(f"Error converting {heic_path}: {str(e)}")
        return False

def find_firefox_binary():
    firefox_path = subprocess.getoutput("which firefox")
    if os.path.isfile(firefox_path):
        with open(firefox_path, 'r') as f:
            content = f.read()
            if 'exec' in content:
                exec_line = [line for line in content.split('\n') if 'exec' in line][0]
                binary_path = exec_line.split()[-1].strip('"')
                if os.path.isfile(binary_path):
                    return binary_path
    
    possible_paths = [
        '/usr/lib/firefox/firefox',
        '/opt/firefox/firefox',
        '/snap/firefox/current/usr/lib/firefox/firefox'
    ]
    for path in possible_paths:
        if os.path.isfile(path):
            return path
    return None

def get_image_orientation(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return 'landscape' if width > height else 'portrait'

def create_html(image_path, fullscreen):
    orientation = get_image_orientation(image_path)
    style = """
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: black;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
        }
        .image-container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 98vw;
            height: 98vh;
            background-color: black;
        }
        img {
            object-fit: contain;
            max-width: 100%;
            max-height: 100%;
        }
    """
    if orientation == 'landscape':
        style += """
        img {
            width: 100%;
            height: auto;
        }
        """
    else:  # portrait
        style += """
        img {
            width: auto;
            height: 100%;
        }
        """
    if not fullscreen:
        style += """
        body {
            background-color: #333;
        }
        .image-container {
            width: 78vw;
            height: 78vh;
            margin: 11vh auto;
        }
        """
    return f"""
    <html>
    <head>
        <style>{style}</style>
    </head>
    <body>
        <div class="image-container">
            <img src="file://{image_path}" alt="Slideshow Image">
        </div>
    </body>
    </html>
    """

def run_slideshow(image_directory, duration=5, firefox_path=None, geckodriver_path=None, fullscreen=True):
    debug_info()
    
    firefox_options = Options()
    if fullscreen:
        firefox_options.add_argument("-kiosk")
    else:
        firefox_options.add_argument("--width=1024")
        firefox_options.add_argument("--height=768")

    if not firefox_path:
        firefox_path = find_firefox_binary()
    
    if not firefox_path or not os.path.isfile(firefox_path):
        print(f"Firefox executable not found. Attempted path: {firefox_path}")
        return

    print(f"Using Firefox binary at: {firefox_path}")
    firefox_options.binary_location = firefox_path

    service = Service(geckodriver_path, log_path='geckodriver.log')

    try:
        print(f"Initializing WebDriver with Firefox path: {firefox_path}")
        driver = webdriver.Firefox(options=firefox_options, service=service)
    except WebDriverException as e:
        print(f"Error initializing WebDriver: {e}")
        print("Firefox path:", firefox_path)
        print("Geckodriver path:", geckodriver_path)
        print("Please check geckodriver.log for more details.")
        return

    image_files = [f for f in os.listdir(image_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.heic'))]

    if not image_files:
        print(f"No image files found in {image_directory}")
        driver.quit()
        return

    try:
        while True:
            for image in image_files:
                image_path = os.path.abspath(os.path.join(image_directory, image))
                
                if image.lower().endswith('.heic'):
                    jpeg_path = os.path.splitext(image_path)[0] + '.jpg'
                    if not convert_heic_to_jpeg(image_path, jpeg_path):
                        print(f"Skipping {image} due to conversion error.")
                        continue
                    image_path = jpeg_path

                try:
                    html_content = create_html(image_path, fullscreen)
                    
                    with open('temp.html', 'w') as f:
                        f.write(html_content)

                    driver.get('file://' + os.path.abspath('temp.html'))
                    time.sleep(duration)

                except Exception as e:
                    print(f"Error displaying {image}: {str(e)}")
                    continue

                finally:
                    if image.lower().endswith('.heic') and os.path.exists(jpeg_path):
                        os.remove(jpeg_path)

    except KeyboardInterrupt:
        print("Slideshow stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        if os.path.exists('temp.html'):
            os.remove('temp.html')

if __name__ == "__main__":
    image_directory = "/home/dcostello/Downloads/kids_images_projector/images"
    geckodriver_path = "/snap/bin/geckodriver"
    fullscreen = True  # Set this to False for windowed mode
    run_slideshow(image_directory, geckodriver_path=geckodriver_path, fullscreen=fullscreen)