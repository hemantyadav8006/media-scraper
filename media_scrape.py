import os
import requests
from urllib.parse import urljoin
import cv2
from bs4 import BeautifulSoup
import pytesseract


COOKIES = {...} # cookie here

HEADERS = {...} # headers here


def get_cards(base_url):
    response = requests.get(base_url, headers=HEADERS, cookies=COOKIES)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    cards = soup.select("div._8165")
    card_urls = []
    for card in cards:
        link = card.select_one('div.c8ff a')
        if link:
            card_urls.append({
                'name': link.get_text(strip=True),
                'url': urljoin(base_url, link['href']),
            })
    return card_urls

def scrape_media(url):
    response = requests.get(url, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.text, 'html.parser')

    images = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
    videos = [
        video['src'].replace("blob:", "") 
        for video in soup.find_all('video') 
        if 'src' in video.attrs
    ]
    return images, videos


def download_file(url, file_name):
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

def download_media(media_list, folder_name):
    os.makedirs(folder_name, exist_ok=True)
    for idx, media_url in enumerate(media_list):
        try:
            file_name = f"{folder_name}/{idx}_{os.path.basename(media_url)}"
            if any(ext in file_name.lower() for ext in [".jpg", ".png", ".jpeg", ".mp4", ".webm", ".avi"]):
                download_file(media_url, file_name)
            else:
                print(f"Skipping unsupported file: {file_name}")
        except Exception as e:
            print(f"Error downloading {media_url}: {e}")


def detect_watermarks(image_folder, watermark_folder):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    os.makedirs(watermark_folder, exist_ok=True)

    for image_file in os.listdir(image_folder):
        img_path = os.path.join(image_folder, image_file)
        if not image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            continue

        img = cv2.imread(img_path)
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)

        if text.strip():
            os.rename(img_path, os.path.join(watermark_folder, image_file))
            print(f"Moved watermarked file: {image_file}")


def main():
    base_url = "https://www.shiksha.com/engineering/colleges/b-tech-colleges-india"
    cards = get_cards(base_url)

    for card in cards:
        print(f"Processing: {card['name']} - {card['url']}")
        images, videos = scrape_media(card['url'])

        
        if images:
            download_media(images, f"images/{card['name']}")
        if videos:
            download_media(videos, f"videos/{card['name']}")

        detect_watermarks(f"images/{card['name']}", f"watermarked_images/{card['name']}")

if __name__ == "__main__":
    main()
