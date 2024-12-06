# Media Scraper and Watermark Detector

This repository contains a Python-based tool to scrape images and videos from college web pages, download them, and detect watermarked images. The script uses cookies and headers for authentication and supports modular functionality for scraping, downloading, and watermark detection.

## Features

- **Scrape URLs**: Extracts URLs of colleges from a base URL.
- **Scrape Media**: Extracts image and video links from individual college pages.
- **Download Media**: Saves images and videos to organized folders.
- **Detect Watermarks**: Identifies watermarked images using OCR (Tesseract).

## Requirements

- Python 3.8 or above
- Required Python libraries:
  - `requests`
  - `bs4` (BeautifulSoup)
  - `cv2` (OpenCV)
  - `pytesseract`
- Tesseract-OCR installed on your system. [Download here](https://github.com/tesseract-ocr/tesseract).

## Installation

### 1. Clone the repository:

```bash
git clone https://github.com/yourusername/media-scraper.git
cd media-scraper
```
