import json
from datetime import datetime, timedelta


    # parent supermarket function, inherited by individual supermarket objects
    # author: Saibo Guo
class Supermarket:

    # parent supermarket function, inherited by individual supermarket objects
    # author:

    def __init__(self, database):

        self.database = database
        # checks json log file to see last time json file updated and parsed
        # if it has been longer than two days, reprocess and record having done so in json log file
        if self.get_recent_database_update() < (datetime.now() - timedelta(days=2)):
            self.process_book()
            self.record_database_update()

    def process_book(self):
        # overwritten in child functions
        return None

    def get_recent_database_update(self):
        # gets the timestamp held in json log file for last database_update for child supermarket object
        with open("logs/data_updates.json", "r") as json_file:
            json_data = json.load(json_file)
        for record in json_data:
            if record["event_type"] == "database_update" and record["supermarket"] == self.supermarket_name:
                return datetime.strptime(record['timestamp'], "%Y-%m-%d %H:%M:%S")

    def record_database_update(self):
        # puts the current timestamp in json log file for database_update for child supermarket object
        with open("logs/data_updates.json", "r") as json_file:
            json_data = json.load(json_file)
        for record in json_data:
            if record["event_type"] == "database_update" and record["supermarket"] == self.supermarket_name:
                record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("logs/data_updates.json", "w") as json_file:
            json.dump(json_data, json_file)


class SupermarketA(Supermarket):

    def __init__(self, database):
        self.supermarket_name = "supermarketa"
        self.supermarket_id = 1
        super().__init__(database)

    def get_data_book(self):
        # since prototype, created example data source to use
        # would expect a source file to be provided by partnering supermarket
        # this function in that case would return the downloaded file from supermarket api
        return "data/supermarketa_stocklist_04122024.json"

    def read_book(self):
        # reads json file into local variable
        with open(self.get_data_book()) as json_file:
            json_data = json.load(json_file)
        return json_data

    def process_book(self):
        # iterates through json file extracting relevant product information, adding to list as tuples
        for product in self.read_book():
            self.database.add_new_product(
                (product["product_id"], product["name"], product["image_url"], product["promotion"], product["price"]))
        self.database.close_database()

    def place_order(self, query):
        # reformat data into json format as received, but only with product id and quantity
        # simulates what would be posted to api
        # returns verdict of whether order was placed successfully or not
        if sum(item[1] for item in query) >= 5:
            # jsn variable would be posted to api
            jsn = json.dumps([{"product_id": item[0], "quantity": item[1]} for item in query], indent=4)
            return "Order placed successfully."
        return "Add at least five items to the order."


