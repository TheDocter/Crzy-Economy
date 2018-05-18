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
Version = "0.0.1"

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings:
    def __init__(self, settingsFile=None):
        if settingsFile is not None and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
        else:
            self.OnlyLive = False
            # Banking Commands
            self.EnableBanking = True
            self.cmdCreateChecking = '!createchecking'
            self.cmdDepositChecking = '!depositchecking'
            self.cmdCreateSavings = '!createsavings'
            self.cmdDepositSavings = '!depositsavings'
            self.SavingsInterestPercent = 1.5
            self.SavingsInterestAdd = 30
            self.cmdWireTransfer = '!wiretransfer'
            self.WireTransferCost = 25
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
    global CESettings, Checking, Savings, WireTransfer
    CESettings = Settings(settingsFile)
    Checking = bank.Checking()
    Savings = bank.Savings()
    WireTransfer = bank.WireTransfer()

    # Check to see if the folders are created.
    if not os.path.exists(BASE_DIR + '/Banking/checkingaccounts'):
        os.mkdir(BASE_DIR + '/Banking/checkingaccounts')

    if not os.path.exists(BASE_DIR + '/Banking/savingsaccount'):
        os.mkdir(BASE_DIR + '/Banking/savingaccounts')

    if not os.path.exists(BASE_DIR + '/Banking/wiretransfers'):
        os.mkdir(BASE_DIR + '/Banking/wiretransfer')

    return


def Execute(data):
    """ Executes data and processes the message. """
    pass


def Tick():
    """Required tick function"""
    pass

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


def haspermission(data):
    """ CHecks to see if the user hs the correct permission.  Based on Castorr91's Gamble"""
    if not Parent.HasPermission(data.User, CESettings.Permission, CESettings.PermissionInfo):
        message = CESettings.PermissionResp.format(data.UserName, CESettings.Permission, CESettings.PermissionInfo)
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


def addcooldown(data):
    """Create Cooldowns Based on Castorr91's Gamble"""
    if Parent.HasPermission(data.User, "Caster", "") and CESettings.CasterCD:
        Parent.AddCooldown(ScriptName, CESettings.Command, CESettings.CoolDown)
        return

    else:
        Parent.AddUserCooldown(ScriptName, CESettings.Command, data.User, CESettings.UserCoolDown)
        Parent.AddCooldown(ScriptName, CESettings.Command, CESettings.CoolDown)
