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

execdir = os.getcwd()  # needed for startup


def read_default_instance():
	old_cwd = os.getcwd() #to reset cwd afterward
	if (os.path.exists("LocalData") == False):
		os.mkdir("LocalData")
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
	global modfolder, jarfolder, instance, gui
	os.chdir(os.path.join(execdir, "LocalData"))
	instance = _instance
	init_config_util_guionly(gui)  # transferring gui flag to CMAN_util 
	modfolder, jarfolder, mc_version = read_config(_instance)  # gets config stuff
	os.chdir(execdir)
	init_config_util((modfolder, jarfolder, mc_version, execdir, instance, gui))  # transferring config data (and Tkinter instance) to all files
	CMAN_install.init_config_install((modfolder, jarfolder, mc_version, execdir, instance, gui))
	CMAN_remove.init_config_remove((modfolder, jarfolder, mc_version, execdir, instance, gui))
	CMAN_upgrade.init_config_upgrade((modfolder, jarfolder, mc_version, execdir, instance, gui))
	CMAN_importexport.init_config_importexport((modfolder, jarfolder, mc_version, execdir, instance, gui))
	init_config_gui((modfolder, jarfolder, mc_version, execdir, instance, gui))


def transfer_tkinst():
	global tkinst
	recieve_tkinst_util(tkinst)
	CMAN_install.recieve_tkinst_install(tkinst)
	CMAN_remove.recieve_tkinst_remove(tkinst)
	CMAN_upgrade.recieve_tkinst_upgrade(tkinst)
	CMAN_importexport.recieve_tkinst_importexport(tkinst)
	CMAN_gui.recieve_tkinst_gui(tkinst)



# Start Program Here:

root = None

tkinst = None

parser = argparse.ArgumentParser(description="CMAN: the Comprehensive Minecraft Archive Network")

parser.add_argument("-i", "--install", help="install mod", metavar="MOD", default="None")
parser.add_argument("-r", "--remove", help="remove mod", metavar="MOD", default="None")
parser.add_argument("-u", "--upgrade", help="upgrade mod", metavar="MOD", default="None")
parser.add_argument("--info", help="give info about a mod", metavar="MOD", default="None")
parser.add_argument("-e", "--export", help="export a modlist", metavar="FILENAME", default="None")
parser.add_argument("--import", help="import a modlist", metavar="MODLIST", default="None", dest="importa")  # importa because import is already taken
parser.add_argument("-I", "--instance", help="sets the Minecraft instance to install into", metavar="INSTANCE", default=instance)
parser.add_argument("-g", "--gui", help="enable GUI", action="store_true")
args = parser.parse_args()
gui = args.gui

if (gui):
	root = tk.Tk()

# print(args.gui)
# print(gui)

# not making Data dir here because it is done later
if (os.path.exists("LocalData") == False):
	os.mkdir("LocalData")
if (os.path.exists("LocalData/ModsDownloaded") == False):
	os.mkdir("LocalData/ModsDownloaded")
if (os.path.exists("LocalData/Modlists") == False):
	os.mkdir("LocalData/Modlists")
try:
	shutil.rmtree("Data")  # deleting Data dir
except(FileNotFoundError):  # Data dir not present
	pass
if (os.path.exists("Data") == False):
	os.mkdir("Data")
if (os.path.exists("Data/temp") == False):
	os.mkdir("Data/temp")

instance = read_default_instance()

try:
	with open("LocalData/config.json") as json_file:
		json_data = json.load(json_file)
		insts = json_data.keys()
	for inst in insts:
		if(not os.path.exists(os.path.join(execdir, "LocalData/ModsDownloaded/"+inst))):  # creating modsdownloaded subdirs for each instance
			os.mkdir(os.path.join(execdir, "LocalData/ModsDownloaded/"+inst))
except:
	pass

execdir = os.getcwd()

setup_config(instance)

if (gui):
	tkinst = Gui(root)

transfer_tkinst()

cprint("You are running " + sys.platform)

update_archive(True)

if(gui):
	CMAN_gui.updateinst()

	tkinst.update_modlist()

check_for_updates()

cprint("CMAN v"+version)
instance = CMAN_gui.instance
if (args.instance != "None"):
	instance = args.instance
if(instance == "@ERROR@"):
	instance = CMAN_gui.instance
cprint("Selected Instance: "+instance)

upgradesavailable = CMAN_upgrade.get_upgrades(instance)
if (upgradesavailable == []):
	pass
else:
	cprint("The following upgrades are available for instance "+instance+":")
	for upgrade in upgradesavailable:
		cprint(" "+upgrade[0].name+" (current version: "+upgrade[1].versions[0]["Version"]+", you have: "+upgrade[0].versions[0]["Version"]+")")
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

def parsecmd(command):
		if(command.split(" ")[0] == "update"):
			update_archive()
		elif(command.split(" ")[0] == "upgrades"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				inst = command.split(" ")[1]
				if(inst == "*"):
					inst = None
				if (not instance_exists(inst) and inst != None):
					cprint("Instance "+inst+" does not exist.")
					return
				update_archive()
				CMAN_upgrade.check_upgrades(True, inst)
			elif(len(command.split(" ")) == 1):
				inst = input("Enter instance name: ")
				if(inst == "*"):
					inst = None
				if (not instance_exists(inst) and inst != None):
					cprint("Instance "+inst+" does not exist.")
					return
				update_archive()
				CMAN_upgrade.check_upgrades(True, inst)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "upgrade"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				mod = command.split(" ")[1]
				update_archive()
				upgrades = CMAN_upgrade.get_upgrades()
				CMAN_upgrade.upgrade_mod(mod)
			elif(len(command.split(" ")) == 1):
				mod = None
				update_archive()
				upgrades = CMAN_upgrade.get_upgrades()
				CMAN_upgrade.upgrade_mod(mod)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "upgradeall"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				inst = command.split(" ")[1]
				if(inst == "*"):
					inst = None
				if (not instance_exists(inst) and inst != None):
					cprint("Instance "+inst+" does not exist.")
					return
			elif(len(command.split(" ")) == 1):
				inst = input("Enter instance name: ")
				if(inst == "*"):
					inst = None
				if (not instance_exists(inst) and inst != None):
					cprint("Instance "+inst+" does not exist.")
					return
			else:
				cprint("Invalid command syntax.")
			update_archive()
			updates = CMAN_upgrade.get_upgrades(inst)
			if(len(updates) == 0):
				cprint("No upgrades available.")
			else:
				for update in updates:
					CMAN_upgrade.upgrade_mod(update[0]["Name"])
		elif(command.split(" ")[0] == "install"):
			if(len(command.split(" ")) == 3 and command.split(" ")[2] != ""):
				mod = command.split(" ")[1]
				mod_version = command.split(" ")[2]
				update_archive()
				CMAN_install.install_mod(mod, version)
			elif(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				mod = command.split(" ")[1]
				update_archive()
				CMAN_install.install_mod(mod)
			elif(len(command.split(" ")) == 1):
				mod = None
				update_archive()
				CMAN_install.install_mod(mod)
			else:
				cprint("Invalid command syntax.")
				cprint(len(command.split(" ")))
		elif(command.split(" ")[0] == "remove"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				mod = command.split(" ")[1]
				CMAN_remove.remove_mod(mod)
			elif(len(command.split(" ")) == 1):
				mod = None
				CMAN_remove.remove_mod(mod)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "info"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				mod = command.split(" ")[1]
				get_info(mod)
			elif(len(command.split(" ")) == 1):
				mod = None
				get_info(mod)
		elif(command.split(" ")[0] == "installm" or command.split(" ")[0] == "installmany"):
			if(len(command.split(" ")) >= 2):
				modslist = command.split(" ")[1:] # separate mod names with spaces
				update_archive()
				string = "Attempting to install: "
				for item in modslist:
					string = string + item+", "
				cprint(string[:-2]+"...") # [:-2] to cut off the extra ", " after the last element
				for item in modslist:
					CMAN_install.install_mod(item)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "removem" or command.split(" ")[0] == "removemany"):
			if(len(command.split(" ")) >= 2):
				modslist = command.split(" ")[1:] # separate mod names with spaces
				update_archive()
				string = "Attempting to remove: "
				for item in modslist:
					string = string + item+", "
				cprint(string[:-2]+"...") # [:-2] to cut off the extra ", " after the last element
				for item in modslist:
					CMAN_remove.remove_mod(item)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "upgradem" or command.split(" ")[0] == "upgrademany"):
			if(len(command.split(" ")) >= 2):
				modslist = command.split(" ")[1:] # separate mod names with spaces
				update_archive()
				string = "Attempting to upgrade: "
				for item in modslist:
					string = string + item+", "
				cprint(string[:-2]+"...") # [:-2] to cut off the extra ", " after the last element
				for item in modslist:
					CMAN_upgrade.upgrade_mod(item)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "export"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				name = command.split(" ")[1]
				update_archive()
				CMAN_importexport.export_mods(name)
			elif(len(command.split(" ")) == 1):
				name = None
				update_archive()
				CMAN_importexport.export_mods(name)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "import"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				path = command.split(" ")[1]
				update_archive()
				CMAN_importexport.import_mods(path)
			elif(len(command.split(" ")) == 1):
				path = None
				update_archive()
				CMAN_importexport.import_mods(path)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "instance" or command.split(" ")[0] == "inst"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				name = command.split(" ")[1]
				if(instance_exists(name)):
					if(name == instance):
						cprint("Instance "+name+" already selected!")
					else:
						setup_config(name)
						cprint("Switched to instance "+name+".")
				else:
					cprint("Instance "+name+" does not exist.")
			elif(len(command.split(" ")) == 1):
				name = input("Enter instance name: ")
				if(instance_exists(name)):
					if(name == instance):
						cprint("Instance "+name+" already selected!")
					else:
						setup_config(name)
						cprint("Switched to instance "+name+".")
				else:
					cprint("Instance "+name+" does not exist.")
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "setdefaultinstance" or command.split(" ")[0] == "setdefaultinst"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				name = command.split(" ")[1]
				if(instance_exists(name)):
					if(name == read_default_instance()):
						cprint("Instance "+name+" already set as default!")
					else:
						with open("default_instance.txt", "w") as f:
							f.write(name)
						cprint("Set default instance as "+name+".")
				else:
					cprint("Instance "+instance+" does not exist.")
			elif(len(command.split(" ")) == 1):
				name = input("Enter instance name: ")
				if(instance_exists(name)):
					if(name == read_default_instance()):
						cprint("Instance "+instance+" already set as default!")
					else:
						with open("default_instance.txt", "w") as f:
							f.write(name)
						cprint("Set default instance as "+name+".")
				else:
					cprint("Instance "+name+" does not exist.")
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "addinstance" or command.split(" ")[0] == "addinst"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				name = command.split(" ")[1]
				if(instance_exists(name)):
					cprint("Instance "+name+" already exists.")
				else:
					new_config(name)
			elif(len(command.split(" ")) == 1):
				name = input("Enter instance name: ")
				if(instance_exists(name)):
					cprint("Instance "+name+" already exists.")
				else:
					new_config(name)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "rminstance" or command.split(" ")[0] == "removeinstance" or command.split(" ")[0] == "rminst"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				name = command.split(" ")[1]
				if(instance_exists(name)):
					rm_config(name)
				else:
					cprint("Instance "+name+" does not exist.")
			elif(len(command.split(" ")) == 1):
				name = input("Enter instance name: ")
				if(instance_exists(name)):
					rm_config(name)
				else:
					cprint("Instance "+name+" does not exist.")
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "instances" or command.split(" ")[0] == "insts"):
			with open("config.json") as json_file:
				json_data = json.load(json_file)
				insts = json_data.keys()
				cprint("Instances:")
				for inst in insts:
					if(inst == instance):
						cprint(inst+" (selected)")
					else:
						cprint(inst)
		elif(command.split(" ")[0] == "list"):
			listmods()
		elif(command.split(" ")[0] == "version"):
			cprint("CMAN v"+version)
		elif(command.split(" ")[0] == "help" or command.split(" ")[0] == "?"):
			print_help()
		elif(command.split(" ")[0] == "exit"):
			sys.exit()
		elif(command == ""):
			pass # don't print "Unknown command." for empty line
		else:
			cprint("Unknown command.")



if (gui == True):
	tkinst.mainloop()

else:
	while(True):
		os.chdir(execdir + "/LocalData/") # reset current working dir
		command = input("> ")
		parsecmd(command)
