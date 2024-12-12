"""Contains child and parent methods to display products on screen."""

import os
import tkinter as tk
from PIL import Image, ImageTk

class ProductInView:

    """Parent class for products in both search and basket view.
    Author: Ben Thompson"""

    def __init__(self, database, product_id, product_name, image_url,
                 quantity, price, promotion, basket_view):

        self.database = database
        self.basket_view, self.basket_id = basket_view, basket_view.basket_id

        self.id, self.name, self.image_url = product_id, product_name, image_url
        self.quantity, self.promotion, self.price = quantity, promotion, price

    def update_quantity_label(self, label):

        """
        Updates quantity label, called on button press from up and down quantity
        :param label: label object to change txt
        :return: None
        """

        label.config(text=str(self.quantity))

    def update_quantity_database(self):

        """
        Updates the change in quantity within the database.
        :return: None
        """

        self.database.update_quantity(self.basket_id, self.id, self.quantity)

    def update_quantity(self, label, delta, container):

        """
        Overwritten in child functions, used to declare parameters.
        """
        return None

    def get_cost(self):
        """
        :return: int of the total cost of all products of this type in basket
        """
        return self.price * self.quantity


    def display_image(self, image_location):

        """
        Preprocesses image from url to Tk image object
        :param image_location: string for location in directory of image
        :return: ImageTk object for photo
        """

        image = Image.open(os.getcwd() + image_location)
        image = image.resize((100, 100))
        photo = ImageTk.PhotoImage(image)

        return photo

    def product_listing(self, frame):

        """
        Called from each individual product to display details on screen.
        :param frame: scrollable frame object
        :return: None
        """

        # individual container for products image, details, price etc...
        product_container = tk.Frame(frame, padx=5, pady=5, relief=tk.RIDGE, borderwidth=2)
        product_container.pack(fill=tk.X, pady=2)

        # displays image on left hand side of container
        photo = self.display_image(self.image_url)
        image_label = tk.Label(product_container, image=photo)
        image_label.image = photo
        image_label.pack(side="left", padx=10)

        # frame for adding product details and quantity
        details_frame = tk.Frame(product_container)
        details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        details = tk.Label(details_frame, text=self.name,justify="left")
        details.pack(anchor="w")

        # frame for quantity, contains buttons also, subframe of details_frame
        quantity_frame = tk.Frame(details_frame)
        quantity_frame.pack(anchor="w")

        quantity_label = tk.Label(quantity_frame, text=self.quantity, font=("Arial", 12))
        quantity_label.pack(side=tk.LEFT, padx=2)

        minus_button = tk.Button(quantity_frame, text="-",
                                 command=lambda: self.update_quantity(quantity_label,
                                                                      -1, product_container))
        minus_button.pack(side=tk.LEFT, padx=2)

        plus_button = tk.Button(quantity_frame, text="+",
                                command=lambda: self.update_quantity(quantity_label,
                                                                     1, product_container))
        plus_button.pack(side=tk.LEFT, padx=2)

        price = tk.Label(product_container, text=self.price, font=("Arial", 12))
        price.pack(side=tk.RIGHT, padx=5)


class ProductInBasket(ProductInView):

    """Object called when a product is to be dispalyed in BasketView.
    Inherits ProductsInView.
    Author: Ben Thompson"""

    def __init__(self, database, product_id, product_name, image_url,
                 quantity, price, promotion, basket_view):
        super().__init__(database, product_id, product_name, image_url,
                         quantity, price, promotion, basket_view)

    def update_quantity(self, label, delta, container):

        """
        Overwrites inherited function. Updates quantity and deals with side
        effects when called from Basket.
        :param label: label object containing number of products in basket, to change
        :param change: +/- number of change to quantity
        :param container: container object to remove product from if search reaches zero
        :return: None
        """

        self.quantity += delta
        if self.quantity <= 0:
            # removes product from frame if quantity reached zero
            container.destroy()
            self.remove_product()
        else:
            # updates label and database
            self.update_quantity_label(label)
            self.update_quantity_database()
        # updates new total price based on updated basket
        self.basket_view.update_total_price()

    def remove_product(self):

        """
        Calls database object to remove basket_contents method.
        :return: None
        """

        self.database.remove_product_from_basket(self.basket_id, self.id)


class ProductInSearch(ProductInView):

    """
    Object called when a product is to be displayed in SearchView.
    Inherits ProductInView.
    Author: Ben Thompson
    """

    def __init__(self, database, product_id, product_name, image_url,
                 quantity, price, promotion, basket_view):
        super().__init__(database, product_id, product_name, image_url,
                         quantity, price, promotion, basket_view)

    def update_database(self):

        """
        Method to update quantity in database. Adds new record, or updated quanity
        if it already exists.
        :return: None
        """

        if self.quantity > 0:
            self.database.add_product_to_basket(self.basket_id, self.id, self.quantity)

    # overwrites inherited function, hence redundant container
    # calls add to basket function if quantity greater than zero, else remove product function
    def update_quantity(self, label, delta, container):

        """
        Overwrites inherited function, hence redundant container. Calls add to basket
        function if quantity is greater than zero, else remove product function. Can
        only be updated to quantity of zero if it already existed, so no remove
        calls are made to records that don't exist.
        :param label: label object containing number of products in basket, to change
        :param change: +/- number of change to quantity
        :param container: redundant
        :return: None
        """
        self.quantity += delta
        if self.quantity > 0:
            self.database.add_product_to_basket(self.basket_id, self.id, self.quantity)
        elif self.quantity == 0:
            self.database.remove_product_from_basket(self.basket_id, self.id)

        # updates quantity label and total price
        self.update_quantity_label(label)
        self.basket_view.update_search_price(delta * self.price)
