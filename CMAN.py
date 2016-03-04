import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
import argparse
import tkinter as tk
import CMAN_remove
import CMAN_upgrade
import CMAN_install
import CMAN_importexport
from CMAN_gui import *
import CMAN_gui
from CMAN_util import *
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialogs

execdir = os.getcwd() #needed for startup

def read_default_instance():
	old_cwd = os.getcwd() #to reset cwd afterward
	os.chdir(os.path.join(execdir, "LocalData")) #at this point in startup, old_cwd is execdir
	try:
		with open("default_instance.txt") as f:
			default = f.read().strip() #don't want leading trailing whitespace/newlines
	except(FileNotFoundError):
		default = "default"
		with open("default_instance.txt", "w") as f:
			f.write(default)

	os.chdir(old_cwd) #restoring cwd
	return default

def setup_config(_instance):
	global modfolder, versionsfolder, instance, gui
	os.chdir(os.path.join(execdir, "LocalData"))
	instance = _instance
	modfolder, versionsfolder = read_config(_instance) #gets config stuff
	os.chdir(execdir)
	init_config_util((modfolder, versionsfolder, execdir, instance, gui, tkinst)) #transferring config data (and Tkinter instance) to all files
	CMAN_install.init_config_install((modfolder, versionsfolder, execdir, instance, gui, tkinst))
	CMAN_remove.init_config_remove((modfolder, versionsfolder, execdir, instance, gui, tkinst))
	CMAN_upgrade.init_config_upgrade((modfolder, versionsfolder, execdir, instance, gui, tkinst))
	CMAN_importexport.init_config_importexport((modfolder, versionsfolder, execdir, instance, gui, tkinst))
	CMAN_gui.init_config_gui((modfolder, versionsfolder, execdir, instance, gui, tkinst))


# Start Program Here:

root = tk.Tk()

tkinst = None

parser = argparse.ArgumentParser(description="CMAN: the Comprehensive Minecraft Archive Network")

parser.add_argument("-i", "--install", help="install mod", metavar="MOD", default="None")
parser.add_argument("-r", "--remove", help="remove mod", metavar="MOD", default="None")
parser.add_argument("-u", "--upgrade", help="upgrade mod", metavar="MOD", default="None")
parser.add_argument("--info", help="give info about a mod", metavar="MOD", default="None")
parser.add_argument("-e", "--export", help="export a modlist", metavar="FILENAME", default="None")
parser.add_argument("--import", help="import a modlist", metavar="MODLIST", default="None", dest="importa") # importa because import is already taken  
parser.add_argument("-I", "--instance", help="sets the Minecraft instance to install into", metavar="INSTANCE", default=instance)
parser.add_argument("-g", "--gui", help="enable GUI", action="store_true")
args = parser.parse_args()
gui = args.gui
#print(args.gui)
#print(gui)

#not making Data dir here because it is done later
if (os.path.exists("LocalData") == False):
	os.mkdir("LocalData")
if (os.path.exists("LocalData/ModsDownloaded") == False):
	os.mkdir("LocalData/ModsDownloaded")
if (os.path.exists("LocalData/Modlists") == False):
	os.mkdir("LocalData/Modlists")
try:
	shutil.rmtree("Data") #deleting Data dir
except(FileNotFoundError): #Data dir not present
	pass
if (os.path.exists("Data") == False):
	os.mkdir("Data")
if (os.path.exists("Data/temp") == False):
	os.mkdir("Data/temp")

instance = read_default_instance()

execdir = os.getcwd()

setup_config(instance)

with open("LocalData/config.json") as json_file:
	json_data = json.load(json_file)
	insts = json_data.keys()
for inst in insts:
	if(not os.path.exists(os.path.join(execdir, "LocalData/ModsDownloaded/"+inst))): #creating modsdownloaded subdirs for each instance
		os.mkdir(os.path.join(execdir, "LocalData/ModsDownloaded/"+inst))


if (gui == True):
	tkinst = Gui(root)

setup_config(instance)

cprint("You are running " + sys.platform)

update_archive(True)

CMAN_gui.updateinst()

tkinst.update_modlist()

check_for_updates()

#print("CMAN v"+version)
if (args.instance != "None"):
	instance = args.instance
cprint("Selected Instance: "+instance)

upgradesavailable = CMAN_upgrade.get_upgrades(instance)
if (upgradesavailable == []):
	pass
else:
	cprint("The following upgrades are available for instance "+instance+":")
	for upgrade in upgradesavailable:
		cprint(" "+upgrade[0]["Name"]+" (current version: "+upgrade[1]["Version"]+", you have: "+upgrade[0]["Version"]+")")
if (args.install != "None"):
	CMAN_install.install_mod(args.install)
	sys.exit()
if (args.remove != "None"):
	CMAN_remove.remove_mod(args.remove)
	sys.exit()
if (args.upgrade != "None"):
	CMAN_upgrade.upgrade_mod(args.upgrade)
	sys.exit()
if (args.info != "None"):
	get_info(args.info)
	sys.exit()
if (args.export != "None"):
	CMAN_importexport.export_mods(args.export)
	sys.exit()
if (args.importa != "None"):
	CMAN_importexport.import_mods(args.importa)
	sys.exit()

if (gui == False):
	print_help()


if (gui == True):
	tkinst.mainloop()


else:
	while(True):
		os.chdir(execdir + "/LocalData/") #reset current working dir
		command = input("> ")
		parsecmd(command)