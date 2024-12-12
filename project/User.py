from Database import Database


class User:

    # minimal user class to facilitate shopping basket function
    # would extend usual user object from previous SSH app in practise
    # author: Bingrui Li

    def __init__(self, user_id):
        self.user_id = user_id

    # returns name associated with user_id in database
    def get_name(self):
        return Database().get_name(self.user_id)
