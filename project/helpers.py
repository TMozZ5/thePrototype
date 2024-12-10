import json

#author：bingrui li
# returns saved order split agreed upon by the house
def get_order_split():
    with open("logs/order_constants.json") as json_file:
        json_data = json.load(json_file)
    for constant in json_data:
        if constant["type"] == "order_split":
            return constant["value"]

