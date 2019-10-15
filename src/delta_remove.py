import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
from delta_util import *
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialogs
modfolder = "@ERROR@"
jarfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"
tkinst = None


def init_config_remove(data):  # data is a 5-tuple
    # makes it edit the global vars rather than create new ones
    global modfolder, jarfolder, mc_version, execdir, instance, gui
    modfolder, jarfolder, mc_version, execdir, instance, gui = data


def recieve_tkinst_remove(data):
    global tkinst
    tkinst = data


def remove_mod(modname):  # behavior not guaranteed on mods installed outside of MCDelta
    #print("MOD NAME IS "+modname)
    if(modname == None):
        modname = cinput("Enter mod name: ")
    a = False
    if(gui):
        a = msgbox.askyesno("Confirm Removal",
                                    "Remove mod '"+modname+"'?", parent=tkinst)
    else:
        a = input(
             "Remove mod '"+modname+"'? [Y/n]: ") == "Y"
    if a:
        try:
            os.remove(execdir + "/LocalData/ModsDownloaded/"+instance+"/" +
                      modname+".installed")  # removing json in ModsDownloaded dir
        except FileNotFoundError:
            if(gui):
                msgbox.showerror("Removal Failed", "Could not remove "+modname +
                                 ".\nEither " + modname + " is not installed, or something went wrong.")
            cprint("Either " + modname +
                   " is not installed, or something went horribly wrong.")
            return
        if(get_json(modname)["Type"] == "Forge" or get_json(modname)["Type"] == "Liteloader"):
            os.chdir(modfolder)
            files = glob.glob(modname + "-*.jar")  # get all versions of mod
            for file in files:
                if(gui):
                    a = msgbox.askyesno("Confirm Deletion",
                                        "Delete \""+file+"\"?", parent=tkinst)
                else:
                    a = input(
                        "Delete \""+file+"\"? [Y/n]: ") == "Y"
                if(a):
                    os.remove(file)
                    cprint("Deleted \""+file+"\".")
                else:
                    cprint("Skipped \""+file+"\".")
        else:
            if(gui):
                msgbox.showerror(
                    "Removal Failed", "MCDelta cannot remove installer mods or base mods.\nRemoving mod from MCDelta listing only.")
            cprint("MCDelta cannot remove installer mods or base mods! (If "+modname +
                   " is not an installer mod or base mod, then something went wrong.)")
        #cprint("Removing file for mod in ModsDownloaded")