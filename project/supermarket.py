"""Contains parent and child objects to interact with supermakets."""

import json
import os
import logging
from datetime import datetime, timedelta
from helpers import download_image

logging.basicConfig(filename="logs/database_changes.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")


class Supermarket:

    """Parent supermarket function. Inherited from individual supermarkets.
    Author: Saibo Guo"""

    def __init__(self, database):

        self.database = database
        # checks json log file to see last time json file updated and parsed
        # if it has been longer than two days, reprocess and record having done so in json log file
        if self.get_recent_database_update() < (datetime.now() - timedelta(days=2)):
            self.process_book()
            self.record_database_update()
        else:
            logging.info("No need to process supermarket JSON as it"
                         "has already been done within the past two days.")


    def make_directory(self):

        """
        Makes a directory if it does not already exist for images.
        :return: None
        """

        os.makedirs(f"{os.getcwd()}/data/images/{self.supermarket_name}/", exist_ok=True)

    def download_image(self, url, product_id):
        """
        Downloads images using helper method.
        :param url: string location of image on internet
        :param product_id: string product_id to add to extension to save
        :return: string extension of cwd to record in db
        """
        print("opened download image once")
        extension = f"/data/images/{self.supermarket_name}/{product_id}.png"
        download_image(url, extension)
        return extension

    def process_book(self):

        """Overwritten in child functions."""

        return None

    def get_recent_database_update(self):

        """
        Gets last timestamp for processing supermarket data.
        :return: string for a timestamp
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "logs/data_updates.json")

        # gets the timestamp held in json log file for
        # last database_update for child supermarket object
        with open(file_path, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
        for record in json_data:
            if record["event_type"] == "database_update" and \
                    record["supermarket"] == self.supermarket_name:
                return datetime.strptime(record['timestamp'], "%Y-%m-%d %H:%M:%S")
        return None

    def record_database_update(self):

        """Sets current timestamp for processing supermarket data.
        :return: None"""

        base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the current script
        file_path = os.path.join(base_dir, "logs/data_updates.json")

        # puts the current timestamp in json log file
        # for database_update for child supermarket object
        with open(file_path, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
        for record in json_data:
            if record["event_type"] == "database_update" and \
                    record["supermarket"] == self.supermarket_name:
                record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "w") as json_file:
            json.dump(json_data, json_file)


class SupermarketA(Supermarket):

    """
    Object to interact with pretend supermarketA. Inherits Supermarket.
    Author: SaiboGuo
    """

    def __init__(self, database):
        self.supermarket_name = "supermarketa"
        self.supermarket_id = 1
        super().__init__(database)

        self.make_directory()

    def get_data_book(self):

        """
        Since prototype, created example datasource to use. Would anticipate a
        source file to be provided by partnering supermarket. This function in
        that case would return directory of downloaded data sheet from
        supermarket API.
        :return: string for filepath
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "data/supermarketa_stocklist_04122024.json")
        return file_path

    def read_book(self):

        """
        Reads JSON file into local variable.
        :return: Dict of JSON data
        """

        with open(self.get_data_book(), "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
        return json_data

    def process_book(self):

        """
        Iterates through JSON file extracting relevant product information, adding
        products to the database with relevant data.
        :return: None
        """

        for product in self.read_book():
            product_id = product["product_id"]
            image_url = product["image_url"]
            # check if already in dir
            image_location = self.download_image(image_url, product_id)
            self.database.add_new_product(
                (product["product_id"], product["name"], image_location,
                 product["promotion"], product["price"]))
        logging.info("Processing JSON file, saving changes to Database.")

    def place_order(self, query):

        """
        Reformat data into JSON format as received, but with only product_id and quantity.
        Simulates what would be posted to API
        :param query: list of tuples (product_id, quantity)
        :return: string verdict of whether order was placed successfully
        """

        if sum(item[1] for item in query) >= 5:
            # jsn variable would be posted to api
            jsn = json.dumps([{"product_id": item[0],
                               "quantity": item[1]} for item in query], indent=4)
            logging.info("Simulating placing order with API. JSN post query: \n %s", jsn)
            return "Order placed successfully."
        return "Add at least five items to the order."
