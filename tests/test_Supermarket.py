import pytest
import json
import os
from datetime import datetime, timedelta
from Supermarket import supermarketA
from Database import database

    # Test Supermarket.py
    # author: Saibo Guo

@pytest.fixture
def db():
    db = database(":memory:")
    db.create_tables()
    return db


def test_get_recent_database_update():
    supermarket = supermarketA(database(":memory:"))
    last_update = supermarket.get_recent_database_update()

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the current test file
    project_dir = os.path.abspath(os.path.join(base_dir, "../project"))
    file_path = os.path.join(project_dir, "logs/data_updates.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    expected_timestamp = datetime.strptime(data[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
    assert last_update == expected_timestamp, "Timestamp from JSON file is incorrect."


def test_record_database_update():
    supermarket = supermarketA(database(":memory:"))
    supermarket.record_database_update()

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the current test file
    project_dir = os.path.abspath(os.path.join(base_dir, "../project"))
    file_path = os.path.join(project_dir, "logs/data_updates.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    updated_timestamp = datetime.strptime(data[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
    
    assert updated_timestamp > datetime.now() - timedelta(minutes=1), "Timestamp was not updated correctly."


def test_get_data_book():
    supermarket = supermarketA(database(":memory:"))
    data_book = supermarket.get_data_book()

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the current test file
    project_dir = os.path.abspath(os.path.join(base_dir, "../project"))
    file_path = os.path.join(project_dir, "data/supermarketA_stocklist_04122024.json")

    assert data_book == file_path, "Data book path is incorrect."


def test_read_book():
    supermarket = supermarketA(database(":memory:"))
    products = supermarket.read_book()

    assert len(products) > 0, "No products were read from the JSON file."
    assert products[0]["name"] == "Heinz Baked Beans", "Product is incorrect."


def test_process_book(db):
    supermarket = supermarketA(db)
    supermarket.process_book()

    db.cursor.execute("SELECT * FROM product WHERE product_id = ?", ("001",))
    product = db.cursor.fetchone()

    assert product is not None, "Product was not inserted."
    assert product[1] == "Heinz Baked Beans", "Product is incorrect."


def test_place_order():
    supermarket = supermarketA(database(":memory:"))

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
