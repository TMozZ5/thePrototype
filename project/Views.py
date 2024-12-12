import tkinter as tk
from tkinter import ttk
from Product import ProductInBasket, ProductInSearch
from User import User


class ProductsView:

    # parent class for view containing products
    # inherited by BasketView and SearchView
    # author: Ben Thompson

    def __init__(self, database, root):

        self.database = database
        self.root = root
        self.products = []

    # creates a scrollable frame object that product can be added to
    # returns frame object
    def scroll_frame(self):
        item_frame = tk.Frame(self.root, padx=10, pady=10)
        item_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(item_frame)

        scrollbar = ttk.Scrollbar(item_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return scrollable_frame

    # removes all products currently in frame
    def hide_products(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

class BasketView (ProductsView):

    # object used to create a basket view
    # inherits ProductView since it will be used to display a basket products
    # author:

    def __init__(self, database, root, user_id):
        super().__init__(database, root)

        user = User(user_id)
        self.user_id, self.user_name = user_id, user.get_name()
        # sets basket_id when program is first launched
        self.get_current_basket()

        # create search view object to switch to when a product is searched
        self.search_view = SearchView(database, root, user_id, self)
        # scroll frame object, used to contain both products in basket and products in search
        self.scrollable_frame = self.scroll_frame()
        self.total_cost = 0

    # set self.basket id to basket_id of current open basket
    def get_current_basket(self):
        self.basket_id = self.database.get_basket_id(self.user_id)

    def calculate_total_cost(self):
        self.total_cost = sum(product.get_cost() for product in self.products)

    def update_total_price(self):
        self.calculate_total_cost()
        self.total_cost_label.config(text=f"£{round(self.total_cost, 2)}")

    def update_search_price(self, delta):
        current_total = float(self.total_cost_label.cget("text").replace("£", ""))
        new_total = current_total + delta
        self.total_cost_label.config(text=f"£{round(new_total, 2)}")
    def get_products(self):
        return self.database.get_basket_contents(self.basket_id)

    # displays current basket contents onto screen
    # calculates first each time what items are in the basket
    # updates the total price to reflect
    def show_basket(self, frame):
        # gets current products from database
        products = self.get_products()
        # clears previous product objects from list
        self.products = []

        # loops for all products, creating new object, adding to frame and appending to list
        for product in products:
            prod = ProductInBasket(self.database, product[0], product[1],
                                   product[2], product[3], product[4], product[5], self)
            prod.product_listing(frame)
            self.products.append(prod)

        self.update_total_price()

    # method to add search bar to bottom of shopping cart
    def add_search_bar(self):
        search_frame = tk.Frame(self.root, padx=10, pady=5)
        search_frame.pack(fill=tk.X)

        search_label = tk.Label(search_frame, text="Search:", anchor="w")
        search_label.pack(side=tk.LEFT, padx=5)

        search_entry = tk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # on change to search entry, trigger method to create search
        search_entry.bind("<KeyRelease>", lambda e: self.show_search(search_entry.get()))

    # method run on place order button being pressed
    # places order with database method, which simulates api post also
    # displays successful or unsuccessful verdict onto window
    def place_order(self):
        verdict = self.database.place_order()
        self.verdict_label.config(text=verdict)
        if verdict == "Order placed successfully.":

            # sets new basket_id
            self.get_current_basket()
            # clears products from window and shows products from new basket (initially none)
            self.hide_products(self.scrollable_frame)
            self.show_basket(self.scrollable_frame)

    # shows searched products on frame, replacing basket products
    def show_search(self, keyword):
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

    # creates the basket_window and displays it to the window
    def create_window(self):

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

        self.total_cost_label = tk.Label(bottom_frame,
                                         text=f"£{(lambda: (self.calculate_total_cost(), self.total_cost)[1])()}",
                                         anchor="e")
        self.total_cost_label.grid(row=0, column=2, sticky="e", padx=5)

        # adds items contained in basket to view
        self.show_basket(self.scrollable_frame)


class SearchView (ProductsView):

    # object used to create a basket view
    # inherits ProductView since it will be used to display a basket products
    # author:

    def __init__(self, database, root, user_id, basket_view):
        super().__init__(database, root)

        self.basket_view, self.basket_id = basket_view, basket_view.basket_id
        self.basket_quantities = {}

        self.user_id = user_id
        self.keyword = ''

    # creates a dictionary of product_id as key, and quantity of them in basket
    # used to determine whether searched product is already in basket and update quantity accordingly
    def set_product_quantities(self, basket):
        product_quantities = {}
        for product in basket:
            product_quantities[product.id] = product.quantity
        self.basket_quantities = product_quantities

    # method called when item is searched and the products displayed are to be changed
    def show_search(self, keyword, frame):

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
            prod = ProductInSearch(self.database, product[0], product[1], product[2],
                                   quantity, product[3], product[4], self.basket_view)
            prod.product_listing(frame)
            self.products.append(prod)
