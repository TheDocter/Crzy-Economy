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


"""

Required custom fucntions needed for plugin.

"""
def openreadme():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return

def haspermission(data):
    """ CHecks to see if the user hs the correct permission.  Based on Castorr91's Gamble"""
    if not Parent.HasPermission(data.User, CGift.Permission, CGift.PermissionInfo):
        message = CGift.PermissionResp.format(data.UserName, CGift.Permission, CGift.PermissionInfo)
        SendResp(data, CGift.Usage, message)
        return False
    return True

def is_on_cooldown(data):
    """ Checks to see if user is on cooldown. Based on Castorr91's Gamble"""
    # check if command is on cooldown
    cooldown = Parent.IsOnCooldown(ScriptName, CGift.Command)
    user_cool_down = Parent.IsOnUserCooldown(ScriptName, CGift.Command, data.User)
    caster = Parent.HasPermission(data.User, "Caster", "")

    if (cooldown or user_cool_down) and caster is False and not CGift.CasterCD:

        if CGift.UseCD:
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, CGift.Command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, CGift.Command, data.User)

            if cooldownDuration > userCDD:
                m_CooldownRemaining = cooldownDuration

                message = CGift.OnCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGift.Usage, message)

            else:
                m_CooldownRemaining = userCDD

                message = CGift.OnUserCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGift.Usage, message)
        return True
    elif (cooldown or user_cool_down) and CGift.CasterCD:
        if CGift.UseCD:
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, CGift.Command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, CGift.Command, data.User)

            if cooldownDuration > userCDD:
                m_CooldownRemaining = cooldownDuration

                message = CGift.OnCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGift.Usage, message)

            else:
                m_CooldownRemaining = userCDD

                message = CGift.OnUserCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGift.Usage, message)
        return True
    return False


def addcooldown(data):
    """Create Cooldowns Based on Castorr91's Gamble"""
    if Parent.HasPermission(data.User, "Caster", "") and CGift.CasterCD:
        Parent.AddCooldown(ScriptName, CGift.Command, CGift.CoolDown)
        return

    else:
        Parent.AddUserCooldown(ScriptName, CGift.Command, data.User, CGift.UserCoolDown)
        Parent.AddCooldown(ScriptName, CGift.Command, CGift.CoolDown)