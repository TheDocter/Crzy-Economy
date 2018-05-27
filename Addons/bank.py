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

            new_balance = int(amount) + int(account_amount)

        with open(self.path + "/" + username + "-checking.txt", "w") as f:
            f.write(str(new_balance))

    def withdraw(self, username, amount):
        """ Removes certain amount to checking account. """
        with open(self.path + "/" + username + "-checking.txt", "r") as f:
            account_amount = f.readline()

        new_balance = int(amount) - int(account_amount)

        with open(self.path + "/" + username + "-checking.txt", "w") as f:
            f.write(str(new_balance))

    def transfer(self, username):
        pass

    def close_account(self, username):
        pass

    def has_account(self, username):
        """ Checks to see if the user already has an account."""
        if not os.path.isfile(self.path + "/" + username + "-checking.txt"):
            return False

        return True

    def has_money_in_account(self, username, amount_wanted):
        """ Checks to see if the user has enough currency in the account to do something with it."""
        with open(self.path + "/" + username + "-checking.txt", "r") as f:
            account_amount = f.readline()

        if amount_wanted <= account_amount:
            return True

        return False


class Savings:
    def __init__(self, path):
        self.path = path

    def create_account(self, username):
        """ Creates a text file to hold Savings account info."""
        with open(self.path + "/" + username + "-savings.txt", "w") as f:
            f.write(str(0))

    def deposit(self, username, amount):
        """ Adds certain amount to Savings account. """
        with open(self.path + "/" + username + "-savings.txt", "r") as f:
            account_amount = f.readline()

        new_balance = int(amount) + int(account_amount)

        with open(self.path + "/" + username + "-savings.txt", "w") as f:
            f.write(str(new_balance))

    def withdraw(self, username, amount):
        """ Removes certain amount to Savings account. """
        with open(self.path + "/" + username + "-savings.txt", "r") as f:
            account_amount = f.readline()

        new_balance = int(amount) - int(account_amount)

        with open(self.path + "/" + username + "-savings.txt", "w") as f:
            f.write(str(new_balance))

    def transfer(self, username):
        pass

    def add_interest(self, username, interest):
        with open(self.path + "/" + username + "-savings.txt", "r") as f:
            account_amount = f.readline()

        interest_added = int(account_amount) * interest

        new_balance = int(account_amount) + interest_added

        with open(self.path + "/" + username + "-savings.txt", "w") as f:
            f.write(str(new_balance))

    def close_account(self, username):
        pass

    def has_account(self, username):
        """ Checks to see if the user already has an account."""
        if not os.path.isfile(self.path + "/" + username + "-savings.txt"):
            return False

        return True

    def has_money_in_account(self, username, amount_wanted):
        """ Checks to see if the user has enough currency in the account to do something with it."""
        with open(self.path + "/" + username + "-savings.txt", "r") as f:
            account_amount = f.readline()

        if amount_wanted <= account_amount:
            return True

        return False
