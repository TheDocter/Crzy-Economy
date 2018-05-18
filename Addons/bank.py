"""
Programmer: TheCrzyDoctor
Description: Handles all the banking.
Date: 05/10/2017
Version: 1
"""
import os


class Checking:
    def __init__(self, path):
        self.path = path

    def create_account(self, username):
        """ Creates a text file to hold checking account info."""
        with open(self.path + "/" + username + "-checking.txt", "w") as f:
            f.write(str(0))

    def deposit(self, username, amount):
        """ Adds certain amount to checking account. """
        with open(self.path + "/" + username + "-checking.txt", "r") as f:
            account_amount = f.readline()

        add = int(amount) + int(account_amount)

        with open(self.path + "/" + username + "-checking.txt", "w") as f:
            f.write(str(add))

    def withdraw(self, username):
        pass

    def transfer(self, username):
        pass

    def close_account(self, username):
        pass

    def has_account(self, username):
        """ Checks to see if the user already has an account."""
        if not os.path.isfile(self.path + "/" + username + "-checking.txt"):
            return False

        return True


class Savings:
    def __init__(self, path):
        self.path = path

    def create_account(self, username):
        """ Creates a text file to hold checking account info."""
        with open(self.path + "/" + username + "-savings.txt", "w") as f:
            f.write(str(0))

    def deposit(self, username, amount):
        """ Adds certain amount to checking account. """
        with open(self.path + "/" + username + "-savings.txt", "r") as f:
            account_amount = f.readline()

        add = int(amount) + int(account_amount)

        with open(self.path + "/" + username + "-savings.txt", "w") as f:
            f.write(str(add))

    def withdraw(self, username):
        pass

    def transfer(self, username):
        pass

    def add_interest(self, username):
        pass

    def close_account(self, username):
        pass

    def has_account(self, username):
        pass


class WireTransfer:
    def __init__(self, path):
        self.path = path
