"""Contains User object import."""
from Database import Database

class User:

    """
    Minimal user class to facilitate shopping basket function. Would
    extend usual user object from previous SSH app in practise.
    Author: Bingrui Li
    """

    def __init__(self, user_id):
        self.user_id = user_id

    # returns name associated with user_id in database
    def get_name(self):

        """
        :return: the name associated with user_id in database
        """
        return Database().get_name(self.user_id)
