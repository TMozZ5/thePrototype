import pytest
from unittest.mock import Mock
from product import ProductInView, ProductInBasket, ProductInSearch

# test_product.py
# author: Saibo Guo

@pytest.fixture
def mock_database():
    return Mock()

@pytest.fixture
def mock_basket_view():
    basket_view = Mock()
    basket_view.basket_id = 1
    return basket_view

@pytest.fixture
def base_product_params(mock_database, mock_basket_view):
    return {
        'database': mock_database,
        'product_id': 1,
        'product_name': 'Test Product',
        'image_url': 'http://example.com/image.jpg',
        'quantity': 1,
        'price': 10.0,
        'promotion': None,
        'basket_view': mock_basket_view
    }

@pytest.fixture
def sample_product_in_view(base_product_params):
    return ProductInView(**base_product_params)

@pytest.fixture
def sample_product_in_basket(base_product_params):
    return ProductInBasket(**base_product_params)

@pytest.fixture
def sample_product_in_search(base_product_params):
    return ProductInSearch(**base_product_params)

#Test whether the initialization correctly sets all attributes.
class TestProductInView:
    def test_init(self, sample_product_in_view, base_product_params):
        assert sample_product_in_view.id == base_product_params['product_id']
        assert sample_product_in_view.name == base_product_params['product_name']
        assert sample_product_in_view.image_url == base_product_params['image_url']
        assert sample_product_in_view.quantity == base_product_params['quantity']
        assert sample_product_in_view.price == base_product_params['price']
        assert sample_product_in_view.promotion == base_product_params['promotion']
        assert sample_product_in_view.basket_id == base_product_params['basket_view'].basket_id

    #Test whether the initialization correctly sets all attributes.
    def test_update_quantity_label(self, sample_product_in_view):
        mock_label = Mock()
        sample_product_in_view.quantity = 5
        sample_product_in_view.update_quantity_label(mock_label)
        mock_label.config.assert_called_once_with(text='5')

    #Test the database quantity update.
    def test_update_quantity_database(self, sample_product_in_view):
        sample_product_in_view.update_quantity_database()
        sample_product_in_view.database.update_quantity.assert_called_once_with(
            sample_product_in_view.basket_id,
            sample_product_in_view.id,
            sample_product_in_view.quantity
        )

    def test_update_quantity_base(self, sample_product_in_view):
        mock_label = Mock()
        mock_container = Mock()
        result = sample_product_in_view.update_quantity(mock_label, 1, mock_container)
        assert result is None

    def test_get_cost(self, sample_product_in_view):
        sample_product_in_view.quantity = 3
        sample_product_in_view.price = 10.0
        assert sample_product_in_view.get_cost() == 30.0

class TestProductInBasket:
    def test_init(self, sample_product_in_basket, base_product_params):
        assert sample_product_in_basket.id == base_product_params['product_id']
        assert sample_product_in_basket.name == base_product_params['product_name']

    def test_update_quantity_increase(self, sample_product_in_basket):
        mock_label = Mock()
        mock_container = Mock()
        
        sample_product_in_basket.update_quantity(mock_label, 1, mock_container)
        
        assert sample_product_in_basket.quantity == 2
        sample_product_in_basket.database.update_quantity.assert_called_once()
        sample_product_in_basket.basket_view.update_total_price.assert_called_once()

    #Test removing a product (quantity is 0).
    def test_update_quantity_remove(self, sample_product_in_basket):
        mock_label = Mock()
        mock_container = Mock()
        
        sample_product_in_basket.update_quantity(mock_label, -1, mock_container)
        
        assert sample_product_in_basket.quantity == 0
        mock_container.destroy.assert_called_once()
        sample_product_in_basket.database.remove_product_from_basket.assert_called_once()

    #Test the remove product functionality
    def test_remove_product(self, sample_product_in_basket):
        sample_product_in_basket.remove_product()
        sample_product_in_basket.database.remove_product_from_basket.assert_called_once_with(
            sample_product_in_basket.basket_id,
            sample_product_in_basket.id
        )

class TestProductInSearch:
    def test_init(self, sample_product_in_search, base_product_params):
        assert sample_product_in_search.id == base_product_params['product_id']
        assert sample_product_in_search.name == base_product_params['product_name']

    def test_update_database_with_positive_quantity(self, sample_product_in_search):
        sample_product_in_search.quantity = 1
        sample_product_in_search.update_database()
        sample_product_in_search.database.add_product_to_basket.assert_called_once()

    def test_update_database_with_zero_quantity(self, sample_product_in_search):
        sample_product_in_search.quantity = 0
        sample_product_in_search.update_database()
        sample_product_in_search.database.add_product_to_basket.assert_not_called()

    def test_update_quantity_add(self, sample_product_in_search):
        mock_label = Mock()
        mock_container = Mock()
        
        sample_product_in_search.update_quantity(mock_label, 1, mock_container)
        
        assert sample_product_in_search.quantity == 2
        sample_product_in_search.database.add_product_to_basket.assert_called_once()
        sample_product_in_search.basket_view.update_search_price.assert_called_once()

    #Test decreasing quantity to 0.
    def test_update_quantity_remove(self, sample_product_in_search):
        mock_label = Mock()
        mock_container = Mock()
        
        sample_product_in_search.update_quantity(mock_label, -1, mock_container)
        
        assert sample_product_in_search.quantity == 0
        sample_product_in_search.database.remove_product_from_basket.assert_called_once()
        sample_product_in_search.basket_view.update_search_price.assert_called_once()
