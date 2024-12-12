"""File contains all the SQL queries used in this application."""

# Author: Thomas Morris

# queries for creating initial tables for database
USER_TABLE = """CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
)"""

PRODUCT_TABLE = """CREATE TABLE IF NOT EXISTS product (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_url TEXT,
    promotion TEXT,
    price REAL NOT NULL
)"""

ORDER_TABLE = """CREATE TABLE IF NOT EXISTS `order` (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_created INTEGER NOT NULL,
    date_placed INTEGER,
    fee_split TEXT
)"""

BASKET_TABLE = """CREATE TABLE IF NOT EXISTS basket (
    basket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    last_updated TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES `order` (order_id)
)"""

BASKET_CONTAINS_TABLE = """CREATE TABLE IF NOT EXISTS basket_contents (
    basket_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (basket_id, product_id),
    FOREIGN KEY (basket_id) REFERENCES basket (basket_id),
    FOREIGN KEY (product_id) REFERENCES product (product_id)
)"""

# queries for order table
GET_USER_NAME = """SELECT name FROM user WHERE user_id = ?"""

# queries for product table
ADD_PRODUCT_QUERY = """INSERT INTO product (product_id, name, image_url, promotion, price)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(product_id) DO UPDATE SET 
    name = excluded.name,
    image_url = excluded.image_url,
    promotion = excluded.promotion,
    price = excluded.price;
"""
GET_SEARCHED_PRODUCTS_QUERY = """SELECT product_id, name, image_url, price, promotion 
FROM product WHERE LOWER(name) LIKE '%' || LOWER(?) || '%';"""

# queries for order table
CREATE_ORDER_QUERY = """INSERT INTO `order`(date_created, date_placed, fee_split)  VALUES (?, 0, ?)"""
COMPLETE_ORDER_QUERY = """UPDATE `order` SET date_placed = ? WHERE order_id = ?"""
GET_CURRENT_ORDER_QUERY = """SELECT order_id from `order` WHERE date_created <= ? AND date_placed = 0"""

# queries for basket table
CREATE_BASKET_QUERY = """INSERT INTO basket (user_id, order_id, last_updated) VALUES (?, ?, ?)"""
GET_BASKET_ID_QUERY = """SELECT basket_id FROM basket WHERE order_id = ? AND user_id = ?"""

# queries for basket_contents table
ADD_PRODUCT_TO_BASKET_QUERY = """INSERT INTO basket_contents VALUES (?, ?, ?)
    ON CONFLICT(basket_id, product_id) DO UPDATE SET
        quantity = excluded.quantity"""
UPDATE_QUANTITY_QUERY = """UPDATE basket_contents SET quantity = ? WHERE basket_id = ? AND product_id = ?"""
DELETE_PRODUCT_CONTENTS_QUERY = """DELETE FROM basket_contents WHERE basket_id = ? AND product_id = ?"""
GET_BASKET_CONTENTS_QUERY = """SELECT product.product_id, product.name, 
product.image_url, basket_contents.quantity, product.price,product.promotion
    FROM basket_contents
    JOIN product ON basket_contents.product_id = product.product_id
    WHERE basket_contents.basket_id = ?;"""
GET_ORDER_QUERY = """SELECT product.product_id, sum(quantity)
    FROM basket_contents, product, basket
    WHERE product.product_id = basket_contents.product_id
    AND basket.basket_id = basket_contents.basket_id
    AND basket.order_id = ?
    GROUP BY product.product_id"""
