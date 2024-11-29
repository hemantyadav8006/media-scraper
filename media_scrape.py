import os
import requests
from urllib.parse import urljoin
import cv2
from bs4 import BeautifulSoup
import pytesseract
import yt_dlp
import re
import glob

COOKIES = {...}

HEADERS = {...}

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
    try:
        response = requests.get(url, headers=HEADERS, cookies=COOKIES)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return [], []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract images
    print("getting img url")
    images = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
    print("got img url")

    # Extract videos (generalized for YouTube and Vimeo)
    print("going for video")
    videos = [
        urljoin(url, iframe['data-original'])
        for iframe in soup.find_all('iframe')
        if 'data-original' in iframe.attrs
    ]
    print("after video url")
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

def download_media(media_list, folder_name, is_video=False):
    os.makedirs(folder_name, exist_ok=True)
    for idx, media_url in enumerate(media_list):
        try:
            if is_video:
                ydl_opts = {
                    'outtmpl': f'{folder_name}/{idx}_%(title)s.%(ext)s',
                    'quiet': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([media_url])
                print(f"Downloaded streaming video: {media_url}")

                # Sanitize filenames after download
                for file_name in os.listdir(folder_name):
                    sanitized_name = re.sub(r'\s+', '_', file_name)
                    if file_name != sanitized_name:
                        os.rename(os.path.join(folder_name, file_name), os.path.join(folder_name, sanitized_name))
                        print(f"Renamed file: {file_name} -> {sanitized_name}")

            else:
                file_name = f"{folder_name}/{idx}_{os.path.basename(media_url)}"
                extension = os.path.splitext(media_url)[-1].lower()
                if extension in [".jpg", ".png", ".jpeg"]:
                    download_file(media_url, file_name)
                else:
                    print(f"Skipping unsupported file: {media_url}")
        except Exception as e:
            print(f"Error downloading {media_url}: {e}")


def detect_watermarks(image_folder, watermark_folder):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    os.makedirs(watermark_folder, exist_ok=True)

    for image_file in os.listdir(image_folder):
        img_path = os.path.join(image_folder, image_file)
        if not image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            print(f"Skipping non-image file: {image_file}")
            continue

        img = cv2.imread(img_path)
        if img is None:
            print(f"Failed to read image: {img_path}")
            continue
        
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            text = pytesseract.image_to_string(gray)

            if any(keyword in text.strip().lower() for keyword in ['watermark', 'sample', 'copyright', 'shiksha']):
                new_path = os.path.join(watermark_folder, image_file)
                os.rename(img_path, new_path)
                print(f"Moved watermarked file: {image_file} to {watermark_folder}")
            else:
                print(f"No watermark detected in: {image_file}")

        except Exception as e:
            print(f"Error processing {img_path}: {e}")


def detect_watermarks_in_video(video_folder, output_folder, watermark_keywords):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    os.makedirs(output_folder, exist_ok=True)

    video_files = glob.glob(os.path.join(video_folder, "*.*"))
    if not video_files:
        print(f"No video files found in folder: {video_folder}")
        return

    for video_path in video_files:
        sanitized_path = video_path.replace("\\", "/")
        if not os.path.exists(sanitized_path):
            print(f"File not found: {sanitized_path}")
            continue
        
        cap = cv2.VideoCapture(sanitized_path)
        print(f"Attempting to open video: {sanitized_path}")

        if not cap.isOpened():
            print(f"Failed to open video: {sanitized_path}")
            continue

        frame_count = 0
        watermarked_frames = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break  # End of video

            frame_count += 1
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            try:
                text = pytesseract.image_to_string(gray_frame)
                if any(keyword in text.lower() for keyword in watermark_keywords):
                    watermarked_frames += 1
                    frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    frame_output_path = os.path.join(output_folder, f"frame_{frame_count}.jpg")
                    cv2.imwrite(frame_output_path, frame)
                    print(f"Watermark detected in frame {frame_count} at {frame_time:.2f}s, saved to {frame_output_path}")
                    break

            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")

        cap.release()
        print(f"Processed {frame_count} frames. Detected watermarks in {watermarked_frames} frames.")

def main():
    base_url = "https://www.shiksha.com/engineering/colleges/b-tech-colleges-india"
    cards = get_cards(base_url)

    for card in cards:
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', card['name'])
        cleaned_name = sanitized_name.replace(" ", "_").replace("|", "_")
        print(f"Processing: {card['name']} - {card['url']}")
        images, videos = scrape_media(card['url'])

        
        if images:
            print("going inside image")
            download_media(images, f"images/{cleaned_name}", is_video=False)
            print("going outside image")
        if videos:
            print("going inside video")
            download_media(videos, f"videos/{cleaned_name}", is_video=True)
            print("going outside video")

        detect_watermarks(f"images/{cleaned_name}", f"watermarked_images/{cleaned_name}")
        watermark_keywords = ["watermark", "sample", "copyright", "shiksha"]
        detect_watermarks_in_video(f"videos/{cleaned_name}",f"watermarked_videos/{cleaned_name}", watermark_keywords)

if __name__ == "__main__":
    main()
