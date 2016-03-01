import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
from CMAN_util import *
modfolder = "@ERROR@"
versionsfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"
tkinst = None

def init_config_remove(data): #data is a 6-tuple
	global modfolder, versionsfolder, execdir, instance, gui, tkinst #makes it edit the global vars rather than create new ones
	modfolder, versionsfolder, execdir, instance, gui, tkinst = data

def remove_mod(modname): #behavior not guaranteed on mods installed outside of CMAN
	if(modname == None):
		modname = input("Enter mod name: ")
	cprint("Removing file for mod in ModsDownloaded")
	try:
		os.remove(execdir + "/LocalData/ModsDownloaded/"+instance+"/"+modname+".installed") #removing json in ModsDownloaded dir
	except FileNotFoundError:
		cprint("Either " + modname + " is not installed, or something went horribly wrong.")
		return
	if(get_json(modname)["Type"] == "Forge" or get_json(modname)["Type"] == "Liteloader"):
		os.chdir(modfolder)
		files = glob.glob(modname + "-*.jar") #get all versions of mod
		for file in files:
			if(input("Delete \""+file+"\"? Type OK to delete, or anything else to skip: ") == "OK"):
				os.remove(file)
				cprint("Deleted \""+file+"\".")
			else:
				cprint("Skipped \""+file+"\".")
	else:
		cprint("I cannot remove installer mods or basemods! (If your mod is not an installermod or basemod, then something went horribly wrong.)")