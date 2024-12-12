"""Main module that when run will run the application.
Author: Ben Thompson"""

import logging
import tkinter as tk
import atexit

from Database import Database
from Views import BasketView

logging.basicConfig(filename="logs/database_changes.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

db = Database()

# creates and set the main application window
root = tk.Tk()
root.title("Shopping Basket")
root.geometry("400x500")

# add the basket view object to the main window
view = BasketView(db, root, 565)

# create the window and run program
view.create_window()
logging.info("Window instance created.")
root.mainloop()

# handles closing the program, commits and saves changes to database
atexit.register(db.close_database)
logging.info("Window instance closed.")
