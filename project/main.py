import tkinter as tk
import atexit

from Database import Database
from Views import BasketView

db = Database()

# creates and set the main application window
root = tk.Tk()
root.title("Shopping Basket")
root.geometry("400x500")

# add the basket view object to the main window
view = BasketView(db, root, 565)

# create the window and run program
view.create_window()
root.mainloop()

# handles closing the program, commits and saves changes to database
atexit.register(db.close_database)

