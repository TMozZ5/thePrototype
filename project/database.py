"""Contains database object to provide link with SQL db."""

import sqlite3
from datetime import datetime
import logging

from supermarket import SupermarketA
from sql_queries import USER_TABLE, PRODUCT_TABLE, ORDER_TABLE, BASKET_TABLE, BASKET_CONTAINS_TABLE
from sql_queries import GET_USER_NAME
from sql_queries import ADD_PRODUCT_QUERY, GET_SEARCHED_PRODUCTS_QUERY
from sql_queries import CREATE_ORDER_QUERY, GET_CURRENT_ORDER_QUERY, COMPLETE_ORDER_QUERY
from sql_queries import CREATE_BASKET_QUERY, GET_BASKET_ID_QUERY
from sql_queries import ADD_PRODUCT_TO_BASKET_QUERY, DELETE_PRODUCT_CONTENTS_QUERY,\
    UPDATE_QUANTITY_QUERY, GET_BASKET_CONTENTS_QUERY, GET_ORDER_QUERY
from helpers import get_order_split

logging.basicConfig(filename="logs/database_changes.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

class Database:

    """
    Database object for communicating with database file.
    When application closes, close_database function is called to commit changes.
    Author: Thomas Morris
    """

    def __init__(self, db_path="SSHsystem.db"):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        self.supermarketa = SupermarketA(self)
        self.create_tables()

    def log(self, action):

        """
        Logs a specific action to the log file.
        :param action: string description of the action to log
        """

        logging.info(action)

    def create_tables(self):

        """
        Method to create tables on loading application. Nothing is
        creating if tables already exist
        :return: None
        """

        for table in [USER_TABLE, PRODUCT_TABLE, ORDER_TABLE, BASKET_TABLE, BASKET_CONTAINS_TABLE]:
            self.cursor.execute(table)

    def get_name(self, user_id):

        """
        Method used to gey username from id, only method on user table.
        :param user_id: string of userid
        :return: string of name fetched from database
        """
        self.cursor.execute(GET_USER_NAME, (user_id, ))
        return self.cursor.fetchone()[0]

    def add_new_product(self, data):

        """
        Creates a new product on product table, called by Supermarket child object.
        :param data: tuple (id, name, image_url, promotion, price)
        :return: None
        """
        self.cursor.execute(ADD_PRODUCT_QUERY, data)
        self.log(f"Added new product to Product table: {data[1]} with ID {data[0]}.")

    def get_searched_products(self, keyword):

        """
        Gets and returns a list of data tuples where the name contains the
        keyword passed.
        :param keyword: string fetched froms search box
        :return: list of tuples (id, name, image_url, promotion, price)
        """

        self.cursor.execute(GET_SEARCHED_PRODUCTS_QUERY, (keyword,))
        return self.cursor.fetchall()

    def create_order(self):

        """
        Creates new order on order table when there is no active order.
        :return: string of order_id
        """
        self.cursor.execute(CREATE_ORDER_QUERY, (datetime.now().strftime('%Y%m%d'),
                                                 get_order_split()))
        order_id = self.cursor.lastrowid
        self.log(f"New order record created with ID: {order_id}.")
        return order_id

    def get_current_order(self):

        """
        Gets active order (date_created is past, no date_placed). If one is not found,
        new order is created.
        :return: string of order_id
        """

        self.cursor.execute(GET_CURRENT_ORDER_QUERY, (int(datetime.now().strftime('%Y%m%d')),))
        order_id = self.cursor.fetchone()
        if order_id is None:
            return self.create_order()
        return str(order_id[0])

    def complete_order(self, current_order):

        """
        Completes order by setting date_placed as current timestamp.
        :param current_order: string of current order_id
        :return: None
        """

        self.cursor.execute(COMPLETE_ORDER_QUERY, (datetime.now().strftime('%Y%m%d'),
                                                   current_order))
        self.log(f"Order committed on ID:{current_order}.")

    def create_basket(self, order_id, user_id):

        """
        Creates new basket on basket table.
        :param order_id: string of order_id
        :param user_id: string of user_id
        :return: string of new basket_id
        """

        self.cursor.execute(CREATE_BASKET_QUERY, (user_id, order_id,
                                                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        basket_id = self.cursor.lastrowid
        self.log(f"New basket ID: {basket_id} created on order ID: {order_id} for user  ID: {user_id}.")
        return basket_id

    def get_basket_id(self, user_id):

        """
        Gets current basket_id, calculated from current active order. If one is not found,
        a new basket is created and its id returned.
        :param user_id: string of user_id
        :return: string of calculated basket_id
        """

        order_id = self.get_current_order()
        self.cursor.execute(GET_BASKET_ID_QUERY, (order_id, user_id,))
        basket_id = self.cursor.fetchone()
        if basket_id is None:
            return self.create_basket(order_id, user_id)
        return str(basket_id[0])

    def add_product_to_basket(self, basket_id, product_id, quantity):

        """
        Created new record on basket_contains table. If record already exists, quantity
        is updated instead.
        :param basket_id: string of basket_id, makes up composite key
        :param product_id: string of product_id, makes up composite key
        :param quantity: int of quantity
        :return: None
        """

        self.cursor.execute(ADD_PRODUCT_TO_BASKET_QUERY,
                            (basket_id, product_id, quantity,))
        self.log(f"Added product ID: {product_id} to basket ID :{basket_id} with quantity: {quantity}.")

    def remove_product_from_basket(self, basket_id, product_id):

        """
        Removed record from the basket_contents table when the quantity reaches zero.
        :param basket_id: string of basket_id
        :param product_id: string of product_id
        :return:
        """
        self.cursor.execute(DELETE_PRODUCT_CONTENTS_QUERY, (basket_id, product_id))
        self.log(f"Removed product ID: {product_id} from basket ID :{basket_id}.")

    def update_quantity(self, basket_id, product_id, quantity):

        """
        Updates quanity of record, calls remove_product is quantity is zero.
        :param basket_id: string of basket_id
        :param product_id: string of product_id
        :param quantity: int of quantity
        :return:
        """
        if quantity == 0:
            self.remove_product_from_basket(basket_id, product_id)
        else:
            self.cursor.execute(UPDATE_QUANTITY_QUERY, (quantity, basket_id, product_id))
            self.log(f"Updated quantity: {quantity} for product ID: {product_id} from basket ID :{basket_id}.")

    def get_basket_contents(self, basket_id):

        """
        Gets current products in active basket, indexed by basket_id.
        :param basket_id: string of basket_id
        :return: list of tuples (product_id, name, image_url, quantity, price, promotion)
        """

        self.cursor.execute(GET_BASKET_CONTENTS_QUERY, (basket_id,))
        return self.cursor.fetchall()

    def place_order(self):

        """
        Gets prepared order. Quantity of all individual baskets is aggregated into singular value.
        If order placed successfully, database is updated to record order being closed. New
        order then created.
        :return: string verdict of success
        """

        current_order = self.get_current_order()
        print(current_order)
        self.cursor.execute(GET_ORDER_QUERY, (current_order,))
        result = self.supermarketa.place_order(self.cursor.fetchall())
        if result == "Order placed successfully.":
            self.complete_order(current_order)
            self.create_order()
        return result

    def close_database(self):

        """
        Runs on termination of program to save changes and close connection.
        :return: None
        """
        self.connection.commit()
        self.connection.close()
