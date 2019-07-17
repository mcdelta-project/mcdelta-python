import requests
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
from delta_util import *
import delta_install
import delta_remove

modfolder = "@ERROR@"
jarfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"
tkinst = None


def init_config_upgrade(data):  # data is a 5-tuple
    # makes it edit the global vars rather than create new ones
    global modfolder, jarfolder, mc_version, execdir, instance, gui
    modfolder, jarfolder, mc_version, execdir, instance, gui = data


def recieve_tkinst_upgrade(data):
    global tkinst
    tkinst = data


def upgrade_mod(modname):
    os.chdir(execdir + "/Data/DeltaMC-Archive")
    if(modname == None):
        modname = cinput("Enter mod name: ")
    update = [get_installed_json(modname), get_json(modname)]
    if(os.path.exists(os.path.join(execdir + "/LocalData/ModsDownloaded/"+instance, modname + ".installed"))):  # Telling user that file exists
        for file in glob.glob(modname + ".installed"):
            cprint(file + " found.")
    else:
        cprint("Mod "+modname+" not found.")
        return
    os.chdir(execdir + "/LocalData")  # restoring current working dir
    if(update[1]["Versions"][0]["Version"] != get_latest_compatible_version(get_mod_from_json(update[0])) and mod_installed(modname)):
        delta_remove.remove_mod(modname)
        delta_install.install_mod(modname)
    elif(not mod_installed(modname)):
        cprint(modname+" is not installed.")
    else:
        cprint(modname+" is already up to date.")


def get_upgrades(inst=None):  # returns a list of 2-element lists of jsons (in which index 0 is the version you have and index 1 is the newest version)
    updates = []
    mods = get_installed_mods(inst)
    for mod in mods:
        if(mod != None):
            mod_data = get_mod_from_name(mod.name)
            if(mod_data != None and get_latest_compatible_version(mod_data) != mod.versions[0]["Version"]):
                # append list of jsons for installed version and newest version
                updates.append([mod, mod_data])
    return(updates)


def get_upgrade_names(inst=None):  # returns a list of mod names
    updates = []
    mods = get_installed_mods(inst)
    for mod in mods:
        if(mod != None):
            mod_data = get_mod_from_name(mod.name)
            if(mod_data != None and get_latest_compatible_version(mod_data) != mod.versions[0]["Version"]):
                updates.append(mod_data.name)  # append mod name
    return(updates)


# full is a flag for whether to print full list of updates or just updates available message
def check_upgrades(full, inst=None):
    if(not instance_exists(inst) and inst != None):
        cprint("Instance "+inst+" does not exist.")
        return
    updates = get_upgrades(inst)
    if(len(updates) > 0):
        if(not full):
            cprint("\nMod upgrades available!")
        else:
            for update in updates:
                cprint("Available Updates:")
                cprint(" "+update[0].name+" (current version: "+update[1].versions[0]
                       ["Version"]+", you have: "+update[0].versions[0]["Version"]+")")
    else:
        if(full):  # don't print "no updates available" on startup
            cprint("No upgrades available.")
