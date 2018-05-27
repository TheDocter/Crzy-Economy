"""
Programmer: TheCrzyDoctor
Description: Gives your Twitch chat a simulated Economy.
Date: 04/19/2017
Version: 1
"""

# ---------------------------------------
# Import Libraries
# ---------------------------------------

import clr
import os
import codecs
import json
import sys
import datetime

# Lets get all the addons
sys.path.append(os.path.join(os.path.dirname(__file__), "Addons"))
import bank

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------------------
# [Required] Script Information
# ---------------------------------------
ScriptName = "Crzy Economy"
Website = "https://www.twitch.tv/thecrzydoc"
Description = "Simulates a full blown economy for the chat bot."
Creator = "TheCrzyDoctor"
Version = "1.0.0"

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKING_DIR = BASE_DIR + '/Banking/checkingaccounts'
SAVINGS_DIR = BASE_DIR + '/Banking/savingaccounts'
# WIRE_TRANSFER_DIR = BASE_DIR + '/Banking/wiretransfer'
INTEREST_ADD_DAY = datetime.datetime.now()


class Settings:
    def __init__(self, settingsFile=None):
        if settingsFile is not None and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
        else:
            self.OnlyLive = False
            # Banking Commands
            self.EnableBanking = True
            self.BankName = 'TheCrzyDoctor\'s Bank'
            self.cmdBankInfo = '!bankinfo'
            self.cmdCreateChecking = '!createchecking'
            self.cmdDepositChecking = '!depositchecking'
            self.cmdWithdrawChecking = '!withdrawchecking'
            self.cmdCreateSavings = '!createsavings'
            self.cmdDepositSavings = '!depositsavings'
            self.cmdWithdrawSavings = '!withdrawsavings'
            self.cmdCheckAccounts = '!checkaccounts'
            self.cmdWireTransfer = '!wiretransfer'
            # Banking Variables
            self.SavingsInterestPercent = 1
            self.SavingsInterestAdd = 30
            self.WireTransferCost = 25
            # Banking Responses
            self.CheckingAccountCreated = '{0}, you have created a new checking account at {1}.'
            self.CheckingAccountAlreadyCreated = '{0}, you already created a checking account.'
            self.NoCheckingAccount = '{0}, you do not have a checking account at {1}.'
            self.CheckingAccountDeposit = '{0}, you just deposited {1} {2} at {3}.'
            self.CheckingWithdrawal = '{0}, you just withdrew {1} {2} from your checking account at {3}.'
            self.SavingAccountCreated = '{0}, you have created a new savings account at {1}.'
            self.SavingsAccountAlreadyCreated = '{0}, you already created a savings account.'
            self.NoSavingsAccount = '{0}, you do not have a savings account at {1}.'
            self.SavingsDeposit = '{0}, you just deposited {1} {2} at {2}.'
            self.SavingsWithdrawal = '{0}, you just withdrew {1} {2} from your savings accounts at {3}.'
            self.WireTransferSent = '{0}, you just sent {1} {2}.'
            self.WireTransferFailed = '{0}, there was a problem with sending {1} {2}.'
            # Banking Permissions
            self.BankingUsage = 'Stream Chat'
            self.BankingPermissions = 'Everyone'
            self.BankingPermissionInfo = ''
            # Permissions/Usage
            self.Usage = 'Stream Chat'
            self.Permission = 'Everyone'
            self.PermissionInfo = ''
            self.PermissionResp = '{0} -> only {1} and higher can use this command'
            # Cool Downs
            self.UseCD = True
            self.CoolDown = 100
            self.OnCoolDown = "{0} the command is still on cooldown for {1} seconds!"
            self.UserCoolDown = 10
            self.OnUserCoolDown = "{0} the command is still on user cooldown for {1} seconds!"
            self.CasterCD = True
            # Responses
            self.NoCurrency = "{0} -> You don't have any currency"
            self.InfoResponse = 'Info coming in next version'

    def ReloadSettings(self, data):
        """ Reload settings file. """
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    def SaveSettings(self, settingsFile):
        """ Saves settings File """
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))


def ReloadSettings(jsonData):
    """ Reload Settings on Save """
    global CESettings
    return


# ---------------------------------------
# 	[Required] Functions
# ---------------------------------------
def Init():
    """ Intialize Data (only called on load) """
    global CESettings, Checking, Savings, INTEREST_ADD_DAY

    # Create global vars to use banking
    CESettings = Settings(settingsFile)
    Checking = bank.Checking(CHECKING_DIR)
    Savings = bank.Savings(SAVINGS_DIR)
    # WireTransfer disabled and handled in Execute function for now.
    #WireTransfer = bank.WireTransfer(WIRE_TRANSFER_DIR)

    # Check to see if the folders are created.
    if not os.path.exists(CHECKING_DIR):
        os.mkdir(CHECKING_DIR)

    if not os.path.exists(SAVINGS_DIR):
        os.mkdir(SAVINGS_DIR)

    # Wire Transfer is disabled in bank.py and is jsut handeled in the execute function for now.
    #if not os.path.exists(WIRE_TRANSFER_DIR):
    #    os.mkdir(WIRE_TRANSFER_DIR)

    # check if file exists and if not create the file that holds when to update the interest...
    if not os.path.isfile(BASE_DIR + "interest_add_date.txt"):
        # det date x days from now.
        date_now = datetime.datetime.now()
        interest_add_day = date_now + datetime.timedelta(days=int(CESettings.SavingsInterestAdd))
        with open(SAVINGS_DIR + "/interest_add_date.txt", "w") as f:
            f.write(str(interest_add_day))
        INTEREST_ADD_DAY = interest_add_day
    else:
        # get the date and store it into vairable
        with open(SAVINGS_DIR + "/interest_add_date.txt", "r") as f:
            day = f.readline()
        datetime_object = datetime.datetime.strptime(day, '%b %d %Y %I:%M%p')
        INTEREST_ADD_DAY = datetime_object
    return


def Execute(data):
    """ Executes data and processes the message. """
    if data.IsChatMessage() and not CESettings.OnlyLive or Parent.IsLive():
        # find out what command they are using.
        if data.GetParam(0).lower() == CESettings.cmdCreateChecking.lower():
            # check to see if the user has banking permissions
            if not has_banking_permission(data):
                return

            # check if the user has an account
            if Checking.has_account(data.UserName):
                SendResp(data, CESettings.BankingUsage, CESettings.CheckingAccountAlreadyCreated.format(data.UserName))
                return

            # Create the account.
            Checking.create_account(data.UserName)
            SendResp(data, CESettings.BankingUsage,
                     CESettings.CheckingAccountCreated.format(data.UserName, CESettings.BankName))
            return

        if data.GetParam(0).lower() == CESettings.cmdDepositChecking.lower() and data.GetParamCount() == 2:
            # check to see if the user has banking permissions
            if not has_banking_permission(data):
                return

            # check if the user has an account
            if not Checking.has_account(data.UserName):
                SendResp(data, CESettings.BankingUsage,
                         CESettings.NoCheckingAccount.format(data.UserName, CESettings.BankName))
                return

            # make sure the user has enough points
            if Parent.GetPoints(data.User) > data.GetParam(1):
                SendResp(data, CESettings.BankingUsage, CESettings.NoCurrency.format(data.UserName))
                return

            # deposit into checking.
            Checking.deposit(data.UserName, data.GetParam(1))
            Parent.RemovePoints(data.User, int(data.GetParam(1)))
            SendResp(data, CESettings.BankingUsage,
                     CESettings.CheckingAccountDeposit.format(data.UserName, data.GetParam(1),
                                                              Parent.GetCurrencyName(),
                                                              CESettings.BankName))
            return

        if data.GetParam(0).lower() == CESettings.cmdWithdrawChecking.lower() and data.GetParamCount() == 2:
            # check to see if the user has banking permissions
            if not has_banking_permission(data):
                return

            # check if the user has an account
            if not Checking.has_account(data.UserName):
                SendResp(data, CESettings.BankingUsage,
                         CESettings.NoCheckingAccount.format(data.UserName, CESettings.BankName))
                return

            # make sure the user has enough points
            if not Checking.has_money_in_account(data.User, data.GetParam(1)):
                SendResp(data, CESettings.BankingUsage, CESettings.NoCurrency.format(data.UserName))
                return

            # withdraw from checking.
            Checking.withdraw(data.UserName, data.GetParam(1))
            Parent.AddPoints(data.User, int(data.GetParam(1)))
            SendResp(data, CESettings.BankingUsage,
                     CESettings.CheckingWithdrawal.format(data.UserName, data.GetParam(1),
                                                              Parent.GetCurrencyName(),
                                                              CESettings.BankName))
            return

        if data.GetParam(0).lower() == CESettings.cmdCreateSavings.lower():
            # check to see if the user has banking permissions
            if not has_banking_permission(data):
                return

            if Savings.has_account(data.UserName):
                SendResp(data, CESettings.BankingUsage,
                         CESettings.SavingsAccountAlreadyCreated.format(data.UserName, CESettings.BankName))
                return

            Savings.create_account(data.UserName)
            SendResp(data, CESettings.BankingUsage, CESettings.SavingAccountCreated.format(data.UserName, CESettings.BankName))

            return

        if data.GetParam(0).lower() == CESettings.cmdDepositSavings.lower() and data.GetParamCount() == 2:
            # check to see if the user has banking permissions
            if not has_banking_permission(data):
                return

            if not Savings.has_account(data.UserName):
                SendResp(data, CESettings.BankingUsage,
                         CESettings.NoSavingsAccount.format(data.UserName, CESettings.BankName))
                return

            # make sure the user has enough points
            if Parent.GetPoints(data.User) > data.GetParam(1):
                SendResp(data, CESettings.BankingUsage, CESettings.NoCurrency.format(data.UserName))
                return
            # deposit into savings
            Savings.deposit(data.UserName, data.GetParam(1))
            Parent.RemovePoints(data.User, int(data.GetParam(1)))
            SendResp(data, CESettings.BankingUsage,
                     CESettings.SavingsDeposit.format(data.UserName, data.GetParam(1),
                                                      Parent.GetCurrencyName(),
                                                      CESettings.BankName))
            return

        if data.GetParam(0).lower() == CESettings.cmdWithdrawSavings.lower() and data.GetParamCount() == 2:
            # check to see if the user has banking permissions
            if not has_banking_permission(data):
                return

            if not Savings.has_account(data.UserName):
                SendResp(data, CESettings.BankingUsage,
                         CESettings.NoSavingsAccount.format(data.UserName, CESettings.BankName))
                return

            # make sure the user has enough points
            if not Savings.has_money_in_account(data.User, data.GetParam(1)):
                SendResp(data, CESettings.BankingUsage, CESettings.NoCurrency.format(data.UserName))
                return

            # withdraw from savings.
            Checking.withdraw(data.UserName, data.GetParam(1))
            Parent.AddPoints(data.User, data.GetParam(1))
            SendResp(data, CESettings.BankingUsage,
                     CESettings.SavingsWithdrawal.format(data.UserName, data.GetParam(1),
                                                      Parent.GetCurrencyName(),
                                                      CESettings.BankName))
            return

        if data.GetParam(0).lower() == CESettings.cmdWireTransfer.lower()and data.GetParamCount() == 3:
            # check to see if the user has banking permissions
            if not has_banking_permission(data):
                return

            # make sure the user has enough points
            points = int(data.GetParam(2)) + CESettings.WireTransferCost
            if Parent.GetPoints(data.User) < points:
                SendResp(data, CESettings.BankingUsage, CESettings.NoCurrency.format(data.UserName))
                return

            # remove currency from person sending transfer
            Parent.RemovePoints(data.User, points)

            # add currency to person it was sent to
            Parent.AddPoints(data.GetParam(1), int(data.GetParam(2)))
            SendResp(data, CESettings.BankingUsage, CESettings.WireTransferSent.format(data.User, data.GetParam(1), data.GetParam(2)))
            return

    return


def Tick():
    """Required tick function"""
    # check interest add date. IF the date is equal to or less than INTEREST_ADD_DAY then add interest
    if datetime.datetime.now() > INTEREST_ADD_DAY:
        # add interest
        Savings.add_interest(CESettings.SavingsInterestPercent)
        update_interest_time()
        Parent.SendStreamMessage("Interest of {0}% has been added to everyone's savings account at {1}".format(CESettings.SavingsInterestPercent, CESettings.BankName))
        return
    return


# ---------------------------------------
# 	[Optional] Usage functions
# ---------------------------------------

def SendResp(data, rUsage, sendMessage):
    """Sends message to Stream or discord chat depending on settings"""

    # Set a list with all possible usage options that would trigger Stream chat message
    l = ["Stream Chat", "Chat Both", "All", "Stream Both"]

    # check if message is from Stream, from chat and if chosen usage is in the list above
    if (data.IsFromTwitch() or data.IsFromYoutube()) and (rUsage in l) and not data.IsWhisper():
        # send Stream message
        Parent.SendStreamMessage(sendMessage)

    # Set a list with all possible usage options that would trigger Stream whisper
    l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]

    # check if message is from Stream, from whisper and if chosen usage is in the list above
    if (data.IsFromTwitch() or data.IsFromYoutube()) and data.IsWhisper() and (rUsage in l):
        # send Stream whisper
        Parent.SendStreamWhisper(data.User, sendMessage)

    # Set a list with all possible usage options that would trigger discord message
    l = ["Discord Chat", "Chat Both", "All", "Discord Both"]

    # check if message is from discord
    if data.IsFromDiscord() and not data.IsWhisper() and (rUsage in l):
        # send Discord message
        Parent.SendDiscordMessage(sendMessage)

    # Set a list with all possible usage options that would trigger discord DM
    l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]

    # check if message is from discord, from DM and if chosen usage is in the list above
    if data.IsFromDiscord() and data.IsWhisper() and (rUsage in l):
        # send Discord whisper
        Parent.SendDiscordDM(data.User, sendMessage)

    return


# ---------------------------------------------
#  Required custom fucntions needed for plugin.
# ---------------------------------------------


def openreadme():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return


def has_permission(data):
    """ CHecks to see if the user hs the correct permission.  Based on Castorr91's Gamble"""
    if not Parent.HasPermission(data.User, CESettings.Permission, CESettings.PermissionInfo):
        message = CESettings.PermissionResp.format(data.UserName, CESettings.Permission, CESettings.PermissionInfo)
        SendResp(data, CESettings.Usage, message)
        return False
    return True


def has_banking_permission(data):
    """ CHecks to see if the user hs the correct permission.  Based on Castorr91's Gamble"""
    if not Parent.HasPermission(data.User, CESettings.BankingPermissions, CESettings.BankingPermissionInfo):
        message = CESettings.PermissionResp.format(data.UserName, CESettings.BankingPermission, CESettings.BankingPermissionInfo)
        SendResp(data, CESettings.Usage, message)
        return False
    return True


def is_on_cooldown(data):
    """ Checks to see if user is on cooldown. Based on Castorr91's Gamble"""
    # check if command is on cooldown
    cooldown = Parent.IsOnCooldown(ScriptName, CESettings.Command)
    user_cool_down = Parent.IsOnUserCooldown(ScriptName, CESettings.Command, data.User)
    caster = Parent.HasPermission(data.User, "Caster", "")

    if (cooldown or user_cool_down) and caster is False and not CESettings.CasterCD:

        if CESettings.UseCD:
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, CESettings.Command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, CESettings.Command, data.User)

            if cooldownDuration > userCDD:
                m_CooldownRemaining = cooldownDuration

                message = CESettings.OnCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CESettings.Usage, message)

            else:
                m_CooldownRemaining = userCDD
                message = CESettings.OnUserCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CESettings.Usage, message)
        return True
    elif (cooldown or user_cool_down) and CESettings.CasterCD:
        if CESettings.UseCD:
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, CESettings.Command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, CESettings.Command, data.User)

            if cooldownDuration > userCDD:
                m_CooldownRemaining = cooldownDuration

                message = CESettings.OnCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CESettings.Usage, message)

            else:
                m_CooldownRemaining = userCDD

                message = CESettings.OnUserCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CESettings.Usage, message)
        return True
    return False


def add_cooldown(data):
    """Create Cooldowns Based on Castorr91's Gamble"""
    if Parent.HasPermission(data.User, "Caster", "") and CESettings.CasterCD:
        Parent.AddCooldown(ScriptName, CESettings.Command, CESettings.CoolDown)
        return

    else:
        Parent.AddUserCooldown(ScriptName, CESettings.Command, data.User, CESettings.UserCoolDown)
        Parent.AddCooldown(ScriptName, CESettings.Command, CESettings.CoolDown)


def update_interest_time():
    global INTEREST_ADD_DAY
    date_now = datetime.datetime.now()
    interest_add_day = date_now + datetime.timedelta(days=int(CESettings.SavingsInterestAdd))
    with open(SAVINGS_DIR + "/interest_add_date.txt", "w") as f:
        f.write(str(interest_add_day))
    INTEREST_ADD_DAY = interest_add_day
