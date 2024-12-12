"""
Helper functions used throughout the project.
#Author: Bingrui Li"""

import logging
from io import BytesIO
import json
import os
import requests
from PIL import Image


logging.basicConfig(filename="logs/database_changes.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

def get_order_split(file_path="logs/order_constants.json"):

    """
    Returns saved order split agreed upon by the house
    :param file_path: location of the file relative to this file
    :return: string of a number indicating order split type
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the current script
    file_path = os.path.join(base_dir, file_path)
    with open(file_path, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    for constant in json_data:
        if constant["type"] == "order_split":
            return constant["value"]
    return None


def download_image(url, filepath):

    """
    Downloads the image given at url if it doesn't already exist in the directory.

    :param url: string location of the url on the internet
    :param filepath: string for filepath to save file to
    :return: string with whether function was successful or not
    """
    try:

        filepath = os.getcwd() + filepath
        # Check if the file already exists
        if os.path.isfile(filepath):
            logging.info("Attempted to download image for %s but already exists.", filepath)
            return "File already exists: %s", filepath

        # Download the image
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Open the image and convert it to PNG format
        image = Image.open(BytesIO(response.content))
        image.save(filepath, format="PNG")

        logging.info("Downloaded image to %s.", filepath)

        return "Image downloaded and saved as PNG: %s", filepath

    except requests.exceptions.RequestException as e:
        return "Error downloading image: %s", e
    except Exception as e:
        return "Error found of type: %s", e
