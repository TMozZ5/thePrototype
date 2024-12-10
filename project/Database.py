import sqlite3
from datetime import datetime

import Supermarket
from SQLQeueries import USER_TABLE, PRODUCT_TABLE, ORDER_TABLE, BASKET_TABLE, BASKET_CONTAINS_TABLE
from SQLQeueries import GET_USER_NAME
from SQLQeueries import ADD_PRODUCT_QUERY, GET_SEARCHED_PRODUCTS_QUERY
from SQLQeueries import CREATE_ORDER_QUERY, GET_CURRENT_ORDER_QUERY, COMPLETE_ORDER_QUERY
from SQLQeueries import CREATE_BASKET_QUERY, GET_BASKET_ID_QUERY
from SQLQeueries import ADD_PRODUCT_TO_BASKET_QUERY, DELETE_PRODUCT_CONTENTS_QUERY, UPDATE_QUANTITY_QUERY,\
    GET_BASKET_CONTENTS_QUERY, GET_ORDER_QUERY
from helpers import get_order_split


class Database:

    # database object for communicating with database file
    # when application closes, close_database function is called to commit changes
    # author: Tom Morris

    def __init__(self):
        self.connection = sqlite3.connect("SSHsystem.db")
        self.cursor = self.connection.cursor()

        self.supermarketa = Supermarket.SupermarketA(self)

        self.create_tables()

    # method to create the tables on loading application
    # nothing is created if tables already exist
    def create_tables(self):
        for table in [USER_TABLE, PRODUCT_TABLE, ORDER_TABLE, BASKET_TABLE, BASKET_CONTAINS_TABLE]:
            self.cursor.execute(table)
        self.connection.commit()

    # method used to get username from id, only method on user table
    def get_name(self, user_id):
        self.cursor.execute(GET_USER_NAME, (user_id, ))
        return self.cursor.fetchone()[0]

    # methods used on product table
    # creates a new product, called by supermarket children
    def add_new_product(self, data):
        # data parameter is formatted as a tuple (id, name, image_url, promotion, price)
        self.cursor.execute(ADD_PRODUCT_QUERY, data)

    # returns a list of tuples with data, name contains keyword parameter passed
    def get_searched_products(self, keyword):
        self.cursor.execute(GET_SEARCHED_PRODUCTS_QUERY, (keyword,))
        return self.cursor.fetchall()

    # methods used on order table
    # creates new order when there is no active order
    # returns new order_id
    def create_order(self):
        self.cursor.execute(CREATE_ORDER_QUERY, (datetime.now().strftime('%Y%m%d'), get_order_split()))
        return self.cursor.lastrowid

    # gets active order (date_created is past, no date_placed), returns order_id
    # if one is not found, a new order is created
    def get_current_order(self):
        self.cursor.execute(GET_CURRENT_ORDER_QUERY, (int(datetime.now().strftime('%Y%m%d')),))
        order_id = self.cursor.fetchone()
        if order_id is None:
            return self.create_order()
        return str(order_id[0])

    # completes order by setting current day to order placed, time not neccesary
    def complete_order(self, current_order):
        self.cursor.execute(COMPLETE_ORDER_QUERY, (datetime.now().strftime('%Y%m%d'), current_order))

    # methods used on basket table
    # creates new basket, returning id
    def create_basket(self, order_id, user_id):
        self.cursor.execute(CREATE_BASKET_QUERY, (user_id, order_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return self.cursor.lastrowid

    # gets current basket_id, calculated from current active order and user_id
    # if one is not found, a new basket is created and its id is returned
    def get_basket_id(self, user_id):
        order_id = self.get_current_order()
        self.cursor.execute(GET_BASKET_ID_QUERY, (order_id, user_id,))
        basket_id = self.cursor.fetchone()
        if basket_id is None:
            return self.create_basket(order_id, user_id)
        return str(basket_id[0])

    # methods used on basket_contains table
    # creates new record in basket_contains or basket_id, product_id and quantity
    # if a record already exists with the same basket_id and product_id_, the quantity is updated instead
    def add_product_to_basket(self, basket_id, product_id, quantity):
        self.cursor.execute(ADD_PRODUCT_TO_BASKET_QUERY, (basket_id, product_id, quantity,))

    # removes record from table, used when quantity of product reaches zero
    def remove_product_from_basket(self, basket_id, product_id):
        self.cursor.execute(DELETE_PRODUCT_CONTENTS_QUERY, (basket_id, product_id))

    # updates quantity of record
    # calls remove_product_from_basket is quantity is zero
    def update_quantity(self, basket_id, product_id, quantity):
        if quantity == 0:
            self.remove_product_from_basket(basket_id, product_id)
        else:
            self.cursor.execute(UPDATE_QUANTITY_QUERY, (quantity, basket_id, product_id))

    # returns a list of tuples (product_id, name, image_url, quantity, price, promotion)
    # only contains items held in the current active basket, indexed by parameter basket_id
    def get_basket_contents(self, basket_id):
        self.cursor.execute(GET_BASKET_CONTENTS_QUERY, (basket_id,))
        return self.cursor.fetchall()

    # returns a list of tuples (product_id, quantity)
    # quantity is of all baskets of a given order number
    # if order placed successfully, database is updated to record order being closed, new order is created
    # returns verdict of success in placing order
    def place_order(self):
        current_order = self.get_current_order()
        print(current_order)
        self.cursor.execute(GET_ORDER_QUERY, (current_order,))
        result = self.supermarketa.place_order(self.cursor.fetchall())
        if result == "Order placed successfully.":
            self.complete_order(current_order)
            self.create_order()
        return result

    # runs on termination of program, commits and saves changes
    def close_database(self):
        self.connection.commit()
        self.connection.close()
