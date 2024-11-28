import os
import requests
import cv2
from bs4 import BeautifulSoup
import pytesseract


cookies = {...}


url = "https://www.shiksha.com/university/iit-bombay-indian-institute-of-technology-mumbai-54212"

print("start")

# Step 1: Scrape images and videos
def scrape_media(url):
    headers = {...}
    print("Scrape_media")
    response = requests.get(url, headers=headers, cookies=cookies)
    print("response")
    soup = BeautifulSoup(response.text, 'html.parser')

    images = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
    # videos = [video['src'] for video in soup.find_all('source') if 'src' in video.attrs]
    videos = [
        video['src'].replace("blob:", "") 
        for video in soup.find_all('video') 
        if 'src' in video.attrs
    ]

    return images, videos


def download_file(url, file_name):
    header= {...}
    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=header, stream=True)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Write the file in chunks to avoid using too much memory
        with open(file_name, 'wb+') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File downloaded successfully: {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


# Step 2: Download media
def download_media(media_list, folder_name):
    print("download_media")

    try: 
        os.mkdir(os.path.join(os.getcwd(), folder_name))
        
    except:
        pass
    # os.chdir(os.path.join(os.getcwd(), folder_name))

    for idx, media_url in enumerate(media_list):
        try:
            file_name = f"{folder_name}/{idx}_{media_url.split('/')[-1]}"
            # print(file_name)
            if any(ext in file_name.lower() for ext in [".jpg", ".png", ".jpeg", ".mp4", ".webm", ".avi"]):
                download_file(media_url, file_name)
            else:
                print(f"Skipping non-image file: {file_name}")
        except Exception as e:
            print(f"Error downloading {media_url}: {e}")

# Step 3: Detect watermarks in images

def detect_watermarks(image_folder, watermark_folder):
    print("detect_watermarks")
    if not os.path.exists(watermark_folder):
        os.makedirs(watermark_folder)

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    for image_file in os.listdir(image_folder):
        img_path = os.path.join(image_folder, image_file)
        
        # Ensure file is an image
        if not image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            print(f"Skipping non-image file: {image_file}")
            continue
        
        img = cv2.imread(img_path)

        # Check if image is loaded successfully
        if img is None:
            print(f"Failed to load image: {img_path}")
            continue

        # Convert to grayscale and extract text
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)

        if text.strip():  # Check if text exists
            os.rename(img_path, os.path.join(watermark_folder, image_file))
            print(f"Watermark detected in: {image_file}, moved to watermark folder.")

# Execute the steps
images, videos = scrape_media(url)


def download_images_and_videos(images, videos):
    # Download images
    download_media(images, "images")

    # Download videos
    download_media(videos, "videos")

download_images_and_videos(images, videos)

detect_watermarks("images", "watermarked_images")



