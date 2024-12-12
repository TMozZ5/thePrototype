import pytest
import json
import os
from datetime import datetime, timedelta
from supermarket import SupermarketA
from database import Database

    # Test Supermarket.py
    # author: Saibo Guo

@pytest.fixture
def db():
    database = Database(":memory:")
    database.create_tables()
    return database


def test_get_recent_database_update():
    supermarket = SupermarketA(Database(":memory:"))
    last_update = supermarket.get_recent_database_update()

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the current test file
    project_dir = os.path.abspath(os.path.join(base_dir, "../project"))
    file_path = os.path.join(project_dir, "logs/data_updates.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    expected_timestamp = datetime.strptime(data[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
    assert last_update == expected_timestamp, "Timestamp from JSON file is incorrect."


def test_record_database_update():
    supermarket = SupermarketA(Database(":memory:"))
    supermarket.record_database_update()

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the current test file
    project_dir = os.path.abspath(os.path.join(base_dir, "../project"))
    file_path = os.path.join(project_dir, "logs/data_updates.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    updated_timestamp = datetime.strptime(data[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
    
    assert updated_timestamp > datetime.now() - timedelta(minutes=1), "Timestamp was not updated correctly."


def test_get_data_book():
    supermarket = SupermarketA(Database(":memory:"))
    data_book = supermarket.get_data_book()

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the current test file
    project_dir = os.path.abspath(os.path.join(base_dir, "../project"))
    file_path = os.path.join(project_dir, "data/supermarketa_stocklist_04122024.json")

    assert data_book == file_path, "Data book path is incorrect."


def test_read_book():
    supermarket = SupermarketA(Database(":memory:"))
    products = supermarket.read_book()

    assert len(products) > 0, "No products were read from the JSON file."
    assert products[0]["name"] == "Heinz Baked Beans", "Product is incorrect."


def test_process_book(db):
    supermarket = SupermarketA(db)
    supermarket.process_book()

    db.cursor.execute("SELECT * FROM product WHERE product_id = ?", ("001",))
    product = db.cursor.fetchone()

    assert product is not None, "Product was not inserted."
    assert product[1] == "Heinz Baked Beans", "Product is incorrect."


def test_place_order():
    supermarket = SupermarketA(Database(":memory:"))

    result = supermarket.place_order([
        ("001", 3),
        ("002", 2)
    ])
    assert result == "Order placed successfully.", "Expected order to be placed successfully."

    result = supermarket.place_order([
        ("001", 1),
        ("002", 1)
    ])
    assert result == "Add at least five items to the order.", "Insufficient quantity."
