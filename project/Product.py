import os
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import requests


class ProductInView:

    # parent class for products both in search window and basket window
    # author: Ben Thompson

    def __init__(self, database, product_id, product_name, image_url, quantity, price, promotion, basket_view):

        self.database = database
        self.basket_view, self.basket_id = basket_view, basket_view.basket_id

        self.id, self.name, self.image_url = product_id, product_name, image_url
        self.quantity, self.promotion, self.price = quantity, promotion, price

    # updates quantity label, called on button press from up and down button
    def update_quantity_label(self, label):
        label.config(text=str(self.quantity))

    # updates the change in quantity in database
    def update_quantity_database(self):
        self.database.update_quantity(self.basket_id, self.id, self.quantity)

    # overwritten in child functions, used to declare parameters
    def update_quantity(self, label, quantity, container):
        return None

    # returns the total cost of all products of one type in basket
    def get_cost(self):
        return self.price * self.quantity

    # preprocesses image from url to tk image object
    # returns ImageTk object ready to be drawn to screen
    def display_image(self, image_location):

        image = Image.open(os.getcwd() + image_location)
        image = image.resize((100, 100))
        photo = ImageTk.PhotoImage(image)

        return photo

    # called from each individual product object to display details on screen
    def product_listing(self, frame):

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
                                 command=lambda: self.update_quantity(quantity_label, -1, product_container))
        minus_button.pack(side=tk.LEFT, padx=2)

        plus_button = tk.Button(quantity_frame, text="+",
                                command=lambda: self.update_quantity(quantity_label, 1, product_container))
        plus_button.pack(side=tk.LEFT, padx=2)

        price = tk.Label(product_container, text=self.price, font=("Arial", 12))
        price.pack(side=tk.RIGHT, padx=5)


class ProductInBasket(ProductInView):

    # object called when a product is to be displayed in basket view
    # inherits ProductInView
    # author:

    def __init__(self, database, product_id, product_name, image_url, quantity, price, promotion, basket_view):
        super().__init__(database, product_id, product_name, image_url, quantity, price, promotion, basket_view)

    # method to update quantity and deal with side effects when called from basket
    def update_quantity(self, label, change, container):
        self.quantity += change
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

    # calls database object to remove basket_contains record
    def remove_product(self):
        self.database.remove_product_from_basket(self.basket_id, self.id)


class ProductInSearch(ProductInView):

    # object called when a product is to be displayed in search view
    # inherits ProductInView
    # author:

    def __init__(self, database, product_id, product_name, image_url, quantity, price, promotion, basket_view):
        super().__init__(database, product_id, product_name, image_url, quantity, price, promotion, basket_view)

    # method to update quantity, adds to basket_contains table if quantity is greater than zero
    # updates record if it already exists in table
    def update_database(self):
        if self.quantity > 0:
            self.database.add_product_to_basket(self.basket_id, self.id, self.quantity)

    # overwrites inherited function, hence redundant container
    # calls add to basket function if quantity greater than zero, else remove product function
    def update_quantity(self, label, change, container):
        self.quantity += change
        if self.quantity > 0:
            self.database.add_product_to_basket(self.basket_id, self.id, self.quantity)
        elif self.quantity == 0:
            self.database.remove_product_from_basket(self.basket_id, self.id)

        # updates quantity label and total price
        self.update_quantity_label(label)
        self.basket_view.update_search_price(change * self.price)
