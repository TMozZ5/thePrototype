"""Contains both the module import used to facilitate views
within the Tkinter window."""

import tkinter as tk
from tkinter import ttk
from Product import productInBasket, productInSearch
from User import user

class productsView:

    """
    Parent class for views containing products. Inherited by
    BasketView and SearchView.
    Author: Ben Thompson
    """

    def __init__(self, database, root):

        self.database = database
        self.root = root
        self.products = []

    def scroll_frame(self):

        """
        Creates a scrollable frame object that can be added to.
        :return: the scrollable frame object created
        """
        item_frame = tk.Frame(self.root, padx=10, pady=10)
        item_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(item_frame)

        scrollbar = ttk.Scrollbar(item_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>",
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return scrollable_frame

    # removes all products currently in frame
    def hide_products(self, frame):
        """
        Removes all products currently in frame.
        :param frame: current frame containing products
        :return: None
        """
        for widget in frame.winfo_children():
            widget.destroy()

class basketView (productsView):

    """
    Object used to create a view for a shopping basket.
    Inherits ProductView since it will be used to display a baskets products.
    Author: Ben Thompson
    """

    def __init__(self, database, root, user_id):
        super().__init__(database, root)

        us = user(user_id)
        self.user_id, self.user_name = user_id, us.get_name()
        # sets basket_id when program is first launched
        self.get_current_basket()

        # create search view object to switch to when a product is searched
        self.search_view = searchView(database, root, user_id, self)
        # scroll frame object, used to contain both products in basket and products in search
        self.scrollable_frame = self.scroll_frame()
        self.total_cost = 0

        # defined in later functions
        self.total_cost_label = None
        self.verdict_label = None

    # set self.basket id to basket_id of current open basket
    def get_current_basket(self):
        """
        Sets basket_id to the current open basket from database.
        :return: None
        """
        self.basket_id = self.database.get_basket_id(self.user_id)

    def calculate_total_cost(self):
        """
        Sets total cost to the sum of products in products list.
        :return: None
        """
        self.total_cost = sum(product.get_cost() for product in self.products)

    def update_total_price(self):
        """
        Updates the total cost value and label also to show to screen.
        :return: None
        """
        self.calculate_total_cost()
        self.total_cost_label.config(text=f"£{round(self.total_cost, 2)}")

    def update_search_price(self, delta):
        """
        Gets the current total price from label and adds the delta to it.
        :param delta: can be +/-, change in total value from basket before
        :return: None
        """
        current_total = float(self.total_cost_label.cget("text").replace("£", ""))
        new_total = current_total + delta
        self.total_cost_label.config(text=f"£{round(new_total, 2)}")

    def get_products(self):
        """
        :return: current contents of basket from basket_id
        """
        return self.database.get_basket_contents(self.basket_id)

    def show_basket(self, frame):
        """
        Displays current basket conents onto screen.
        Calculates first each time what items are in the basket.
        Updates total price to reflect.
        :param frame: scrollable frame to add product listings to
        :return: None
        """
        # gets current products from database
        products = self.get_products()
        # clears previous product objects from list
        self.products = []

        # loops for all products, creating new object, adding to frame and appending to list
        for product in products:
            prod = productInBasket(self.database, product[0], product[1],
                                   product[2], product[3], product[4], product[5], self)
            prod.product_listing(frame)
            self.products.append(prod)

        self.update_total_price()

    def add_search_bar(self):

        """
        Adds search bar to the BasketView object.
        :return: None
        """
        search_frame = tk.Frame(self.root, padx=10, pady=5)
        search_frame.pack(fill=tk.X)

        search_label = tk.Label(search_frame, text="Search:", anchor="w")
        search_label.pack(side=tk.LEFT, padx=5)

        search_entry = tk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # on change to search entry, trigger method to create search
        search_entry.bind("<KeyRelease>", lambda e: self.show_search(search_entry.get()))

    def place_order(self):

        """
        Method run on place order button being pressed.
        Places order with database method, which simulates api post also.
        Displays successful or unsuccessful verdict onto window.
        :return: None
        """
        verdict = self.database.place_order()
        self.verdict_label.config(text=verdict)
        if verdict == "Order placed successfully.":

            # sets new basket_id
            self.get_current_basket()
            # clears products from window and shows products from new basket (initially none)
            self.hide_products(self.scrollable_frame)
            self.show_basket(self.scrollable_frame)

    def show_search(self, keyword):

        """
        Shows searched products on frame, replacing basket products.
        :param keyword: string contents of search box
        :return: None
        """
        # searched only if word is greater than three characters
        # hides products in basket to show product searched
        if len(keyword) >= 3:
            self.hide_products(self.scrollable_frame)
            self.search_view.set_product_quantities(self.products)
            self.search_view.show_search(keyword, self.scrollable_frame)
        # clears current frame of searched products and replaces it with current basket
        else:
            self.search_view.hide_products(self.scrollable_frame)
            self.show_basket(self.scrollable_frame)

    def create_window(self):

        """
        Creates the basket_window and displays it to the main window.
        :return: None
        """

        self.add_search_bar()

        # bottom frame for username, total cost and button
        bottom_frame = tk.Frame(self.root, padx=10, pady=10)
        bottom_frame.pack(fill=tk.X)

        # equally space each column so button is centered
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)
        bottom_frame.columnconfigure(2, weight=1)

        username_label = tk.Label(bottom_frame, text=self.user_name, anchor="w")
        username_label.grid(row=0, column=0, sticky="w", padx=5)

        place_order_button = tk.Button(bottom_frame, text="Place Order", command=self.place_order)
        place_order_button.grid(row=0, column=1)

        # label updates when an order is successfully or unsuccessfully placed
        self.verdict_label = tk.Label(bottom_frame, text="")
        self.verdict_label.grid(row=1, column=1)

        self.calculate_total_cost()
        self.total_cost_label = tk.Label(bottom_frame, text=f"£{self.total_cost}", anchor="e")
        self.total_cost_label.grid(row=0, column=2, sticky="e", padx=5)

        # adds items contained in basket to view
        self.show_basket(self.scrollable_frame)


class searchView (productsView):

    """
    Object used to build search view.
    Inherits products view since it will be used to display basket products.
    Author: Ben Thompson
    """

    def __init__(self, database, root, user_id, basket_view):
        super().__init__(database, root)

        self.basket_view, self.basket_id = basket_view, basket_view.basket_id
        self.basket_quantities = {}

        self.user_id = user_id
        self.keyword = ''

    def set_product_quantities(self, basket):

        """
        Creates a dictionary of product_id as key, and quantity as record in basket.
        Used to determine whether searched product is already in basket
        and updated quantity accordingly.
        :param basket: list of ProductInBasket objects
        :return: None
        """
        product_quantities = {}
        for product in basket:
            product_quantities[product.id] = product.quantity
        self.basket_quantities = product_quantities

    def show_search(self, keyword, frame):

        """
        Method called when item is searched and products are to be changed.
        :param keyword: string contained by the search box
        :param frame: scrollable frame to add products to
        :return: None
        """
        # removes current basket products from frame
        self.hide_products(frame)
        self.keyword = keyword

        # gets searched products and clears products set from basket
        products = self.database.get_searched_products(self.keyword)
        self.products = []

        # loops for all products found by search criteria
        # creates product object, displays on frame and adds to list
        for product in products:
            # checks if already in basket and sets quantity accordingly
            if product[0] in self.basket_quantities:
                quantity = self.basket_quantities[product[0]]
            else:
                quantity = 0
            prod = productInSearch(self.database, product[0], product[1], product[2],
                                   quantity, product[3], product[4], self.basket_view)
            prod.product_listing(frame)
            self.products.append(prod)
