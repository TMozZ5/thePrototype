import pytest
from Database import database
from Database import USER_TABLE, PRODUCT_TABLE, ORDER_TABLE, BASKET_TABLE, BASKET_CONTAINS_TABLE
#Test Database.py
#author：bingrui li
@pytest.fixture
def db():
    db = database(":memory:")
    db.cursor.execute(USER_TABLE)
    db.cursor.execute(PRODUCT_TABLE)
    db.cursor.execute(ORDER_TABLE)
    db.cursor.execute(BASKET_TABLE)
    db.cursor.execute(BASKET_CONTAINS_TABLE)
    db.connection.commit()
    return db


def test_create_tables(db):
    db.create_tables()
    tables = ["user", "product", "order", "basket", "basket_contents"]
    for table in tables:
        db.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        result = db.cursor.fetchone()
        assert result is not None, f"Table {table} was not created."


def test_get_name(db):
    db.cursor.execute("INSERT INTO user (user_id, name, email) VALUES (100, 'Bingrui', 'Bingrui@gmail.com')")
    db.connection.commit()
    name = db.get_name(100)
    assert name == "Bingrui", "The name is incorrect."


def test_add_new_product(db):
    product_data = (100, "Apple", "http://yigewangzhan.com/apple.jpg", "Promotion", 2.53)
    db.add_new_product(product_data)
    db.cursor.execute("SELECT * FROM product WHERE product_id = ?", (100,))
    result = db.cursor.fetchone()
    assert result is not None, "Product was not added."
    assert result[1] == "Apple", "Product is incorrect."


def test_get_searched_products(db):
    product_data = (100, "Apple", "http://yigewangzhan.com/apple.jpg", "Promotion", 2.53)
    db.add_new_product(product_data)
    results = db.get_searched_products("Apple")
    assert len(results) == 1, "Incorrect number of results."
    assert results[0][1] == "Apple", "Search result is incorrect."


def test_create_order(db):
    order_id = db.create_order()
    db.cursor.execute("SELECT * FROM `order` WHERE order_id = ?", (order_id,))
    db.connection.commit()
    result = db.cursor.fetchone()
    assert result is not None, "Order was not created."
    assert result[1] is not None, "Order date was not set."
    db.connection.close()


def test_get_current_order(db):
    order_id = db.create_order()
    current_order_id = db.get_current_order()
    assert current_order_id == str(order_id), "Current order ID does not match the created order ID."


def test_complete_order(db):
    order_id = db.create_order()
    db.complete_order(order_id)
    db.cursor.execute("SELECT date_placed FROM `order` WHERE order_id = ?", (order_id,))
    result = db.cursor.fetchone()
    assert result[0] is not None, "Order was not completed."


def test_create_basket(db):
    order_id = db.create_order()
    basket_id = db.create_basket(order_id, 100)
    db.cursor.execute("SELECT * FROM basket WHERE basket_id = ?", (basket_id,))
    result = db.cursor.fetchone()
    assert result is not None, "Basket was not created."


def test_get_basket_id(db):
    order_id = db.create_order()
    db.create_basket(order_id, 100)
    basket_id = db.get_basket_id(100)
    assert basket_id is not None, "Basket ID is incorrect."


def test_add_product_to_basket(db):
    order_id = db.create_order()
    basket_id = db.create_basket(order_id, 100)
    product_data = (100, "Apple", "http://example.com/apple.jpg", "Promotion", 2.53)
    db.add_new_product(product_data)
    db.add_product_to_basket(basket_id, 100, 101)
    db.cursor.execute("SELECT * FROM basket_contents WHERE basket_id = ? AND product_id = ?", (basket_id, 100))
    result = db.cursor.fetchone()
    assert result is not None, "Product was not added to the basket."
    assert result[2] == 101, "Product quantity in the basket is incorrect."


def test_remove_product_from_basket(db):
    order_id = db.create_order()
    basket_id = db.create_basket(order_id, 100)
    product_data = (100, "Apple", "http://example.com/apple.jpg", "Promotion", 2.53)
    db.add_new_product(product_data)
    db.add_product_to_basket(basket_id, 100, 101)
    db.remove_product_from_basket(basket_id, 100)
    db.cursor.execute("SELECT * FROM basket_contents WHERE basket_id = ? AND product_id = ?", (basket_id, 100))
    result = db.cursor.fetchone()
    assert result is None, "Product was not removed from the basket."


def test_get_basket_contents(db):
    order_id = db.create_order()
    basket_id = db.create_basket(order_id, 100)
    product_data = (100, "Apple", "http://example.com/apple.jpg", "Promotion", 2.53)
    db.add_new_product(product_data)
    db.add_product_to_basket(basket_id, 100, 3)
    contents = db.get_basket_contents(basket_id)
    assert len(contents) == 1, "Basket contents are incorrect."
    assert contents[0][1] == "Apple", "Product is incorrect."
    assert contents[0][3] == 3, "Product quantity in basket is incorrect."


def test_place_order(db):
    order_id = db.create_order()
    basket_id = db.create_basket(order_id, 100)
    product_data = (100, "Apple", "http://example.com/apple.jpg", "Promotion", 2.53)
    db.add_new_product(product_data)
    db.add_product_to_basket(basket_id, 100, 11)
    result = db.place_order()
    assert result == "Order placed successfully.", "Order placed unsuccessfully."
