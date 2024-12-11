import json, os, requests
from PIL import Image
from io import BytesIO
import logging

logging.basicConfig(filename="logs/database_changes.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")


# author：Bingrui Li
# returns saved order split agreed upon by the house
def get_order_split(file_path="logs/order_constants.json"):
    with open(file_path) as json_file:
        json_data = json.load(json_file)
    for constant in json_data:
        if constant["type"] == "order_split":
            return constant["value"]

def download_image(url, filepath):
    try:

        filepath = os.getcwd() + filepath
        # Check if the file already exists
        if os.path.isfile(filepath):
            logging.info(f"Attempted to download image for {filepath} but already exists.")
            return f"File already exists: {filepath}"

        # Download the image
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Open the image and convert it to PNG format
        image = Image.open(BytesIO(response.content))
        image.save(filepath, format="PNG")

        logging.info(f"Downloaded image to {filepath}.")

        return f"Image downloaded and saved as PNG: {filepath}"

    except requests.exceptions.RequestException as e:
        return f"Error downloading image: {e}"
    except Exception as e:
        return f"Error: {e}"
