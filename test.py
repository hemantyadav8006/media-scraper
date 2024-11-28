import requests

url = 'https://images.shiksha.com/mediadata/images/1507098550phptQ33Ej_205x160.jpg'


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

download_file(url, "Image.jpg")