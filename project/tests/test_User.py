import pytest
from project.Database import Database
from project.SQLQeueries import USER_TABLE
#Test User.py
#author：bingrui li

@pytest.fixture
def db(): 
    database = Database(":memory:")  
    database.cursor.execute(USER_TABLE)   
    database.connection.commit()
    return database


def test_user_get_name(db):
    db.cursor.execute("INSERT INTO user (user_id, name, email) VALUES (100, 'Bingrui', 'Bingrui@gmail.com')")
    db.connection.commit()
    name = db.get_name(100)
    assert name == "Bingrui", "The name is incorrect."
