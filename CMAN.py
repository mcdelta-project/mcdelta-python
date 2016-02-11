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
from CMAN_util import *

version = "2.0.0"

execdir = os.getcwd() #needed for startup

def check_for_updates():
	with urllib.request.urlopen('http://raw.githubusercontent.com/Comprehensive-Minecraft-Archive-Network/CMAN-Python/master/version.txt') as response:
		latestversion = response.read()
		latestversion = latestversion.decode("utf-8").strip() #it is using a bytes string and printing the b prefix and newline
		if (version != str(latestversion)):
			print("WARNING! YOU ARE USING OLD VERSION " + version + "! NEWEST VERSION IS " + str(latestversion) + "!")

def update_archive():
	#Delete old archive
	os.chdir(execdir + "/Data")
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		shutil.rmtree("CMAN-Archive")
	# Archive Download
	url = "https://github.com/Comprehensive-Minecraft-Archive-Network/CMAN-Archive/tarball/master"
	file_name = "CMAN.tar.gz"
	print("Downloading Archive...")
	# Download it.
	try:
		with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
		print("Done.")
	except:
		print("Something went wrong while downloading the archive.")
		sys.exit()
	print("Extracting Archive...")
	tar = tarfile.open("CMAN.tar.gz")  # untar
	tar.extractall()
	tarlist = tar.getnames()
	os.rename(tarlist[0], "CMAN-Archive") #remane the resulting folder to CMAN-Archive
	print("Done.")

def get_info(modname):
	if(modname == None):
		modname = input("Enter mod name: ")

	json_data = get_json(modname)
	if(json_data == -1):
		return
	else:
		if (json_data != None):
			if(json_data["Unstable"] == "false"):
				stable = "Stable" 
			else:
				stable = "Unstable" 
			cprint(json_data["Name"]+":")
			cprint("\tVersion: "+json_data["Version"]+" ("+stable+")")
			cprint("\tAuthor(s): "+json_data["Author"])
			cprint("\tDescription: "+json_data["Desc"])
			cprint("\tRequirements: "+str(json_data["Requirements"]))
			cprint("\tKnown Incompatibilities: "+str(json_data["Incompatibilities"]))
			cprint("\tDownload Link: "+str(json_data["Link"]))
			cprint("\tLicense: "+json_data["License"])
		else:
			cprint("Mod "+modname+" not found.")

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

def print_help():
	cprint("Commands:")
	cprint(" install 'mod': install the mod 'mod'")
	cprint(" installm: install multiple mods")
	cprint(" info 'mod': get info for the mod 'mod'")
	cprint(" remove 'mod': remove the mod 'mod'")
	cprint(" removem: remove multiple mods")
	cprint(" upgrade 'mod': upgrade the mod 'mod'")
	cprint(" upgradem: upgrade multiple mods")
	cprint(" upgradeall: upgrade all outdated mods for Minecraft instance 'inst', or use '*' to check all instances")
	cprint(" upgrades 'inst': list available mod upgrades for Minecraft instance 'inst', or use '*' to check all instances")
	cprint(" update: update the CMAN archive")
	cprint(" help: display this help message")
	cprint(" version: display the CMAN version number")
	cprint(" list: list installed mods")
	cprint(" export 'name': export a modlist with the name 'name' , which can be imported later")
	cprint(" import 'pathtomodlist': import the modlist 'pathtomodlist'")
	cprint(" inst 'inst': switches to Minecraft instance 'inst'")
	cprint(" defaultinst 'inst': sets default Minecraft instance to 'inst'")
	cprint(" addinst 'inst': adds the Minecraft instance 'inst'")
	cprint(" rminst 'inst': removes the Minecraft instance 'inst'")
	cprint(" insts: lists all Minecraft instances")
	cprint(" exit: exit CMAN")

def setup_config(_instance):
	global modfolder, versionsfolder, instance, gui
	os.chdir(os.path.join(execdir, "LocalData"))
	instance = _instance
	modfolder, versionsfolder = read_config(_instance) #gets config stuff
	os.chdir(execdir)
	init_config_util((modfolder, versionsfolder, execdir, instance, gui)) #transferring config data to all files
	CMAN_install.init_config_install((modfolder, versionsfolder, execdir, instance, gui))
	CMAN_remove.init_config_remove((modfolder, versionsfolder, execdir, instance, gui))
	CMAN_upgrade.init_config_upgrade((modfolder, versionsfolder, execdir, instance, gui))
	CMAN_importexport.init_config_importexport((modfolder, versionsfolder, execdir, instance, gui))


def initialise_window():
	root.title("CMAN v2.1.0")
	root.geometry("300x300")

	title = tk.Label(root, text = "Welcome to CMAN!")
	title.pack()

	output = tk.Label(root, text = "None")
	output.pack(side = tk.BOTTOM)

	button = tk.Button(root, text = "List installed mods", command =listmods, bg = "blue")
	button.pack(pady=20, padx = 20)

# Start Program Here:

root = tk.Tk()

parser = argparse.ArgumentParser(description="CMAN: the Comprehensive Minecraft Archive Network")

parser.add_argument("-i", "--install", help="install mod", metavar="MOD", default="None")
parser.add_argument("-r", "--remove", help="remove mod", metavar="MOD", default="None")
parser.add_argument("-u", "--upgrade", help="upgrade mod", metavar="MOD", default="None")
parser.add_argument("--info", help="give info about a mod", metavar="MOD", default="None")
parser.add_argument("-e", "--export", help="export a modlist", metavar="FILENAME", default="None")
parser.add_argument("--import", help="import a modlist", metavar="MODLIST", default="None", dest="importa") # importa because import is already taken  
parser.add_argument("-I", "--instance", help="sets the Minecraft instance to install into", metavar="INSTANCE", default=instance)
parser.add_argument("-g", "--gui", help="enable modlist", action="store_true")
args = parser.parse_args()
gui = args.gui
print(args.gui)
print(gui)

print("You are running " + sys.platform)
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

update_archive()
print("CMAN v"+version)
if (args.instance != "None"):
	instance = args.instance
print("Selected Instance: "+instance)

if (gui == True):
	initialise_window()

check_for_updates()
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
	root.mainloop()
else:
	while(True):
		os.chdir(execdir + "/LocalData/") #reset current working dir
		command = input("> ")
		if(command.split(" ")[0] == "update"):
			update_archive()
		elif(command.split(" ")[0] == "upgrades"):
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				inst = command.split(" ")[1]
				if(inst == "*"):
					inst = None
				if (not instance_exists(inst) and inst != None):
					cprint("Instance "+inst+" does not exist.")
					continue
				update_archive()
				CMAN_upgrade.check_upgrades(True, inst)
			elif(len(command.split(" ")) == 1):
				inst = input("Enter instance name: ")
				if(inst == "*"):
					inst = None
				if (not instance_exists(inst) and inst != None):
					cprint("Instance "+inst+" does not exist.")
					continue
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
					continue
			elif(len(command.split(" ")) == 1):
				inst = input("Enter instance name: ")
				if(inst == "*"):
					inst = None
				if (not instance_exists(inst) and inst != None):
					cprint("Instance "+inst+" does not exist.")
					continue
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
			if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
				mod = command.split(" ")[1]
				update_archive()
				CMAN_install.install_mod(mod)
			elif(len(command.split(" ")) == 1):
				mod = None
				update_archive()
				CMAN_install.install_mod(mod)
			else:
				cprint("Invalid command syntax.")
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
				modslist = command.split(" ")[1:] #separate mod names with spaces
				update_archive()
				string = "Attempting to install: "
				for item in modslist:
					string = string + item+", "
				cprint(string[:-2]+"...") #[:-2] to cut off the extra ", " after the last element
				for item in modslist:
					CMAN_install.install_mod(item)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "removem" or command.split(" ")[0] == "removemany"):
			if(len(command.split(" ")) >= 2):
				modslist = command.split(" ")[1:] #separate mod names with spaces
				update_archive()
				string = "Attempting to remove: "
				for item in modslist:
					string = string + item+", "
				cprint(string[:-2]+"...") #[:-2] to cut off the extra ", " after the last element
				for item in modslist:
					CMAN_remove.remove_mod(item)
			else:
				cprint("Invalid command syntax.")
		elif(command.split(" ")[0] == "upgradem" or command.split(" ")[0] == "upgrademany"):
			if(len(command.split(" ")) >= 2):
				modslist = command.split(" ")[1:] #separate mod names with spaces
				update_archive()
				string = "Attempting to upgrade: "
				for item in modslist:
					string = string + item+", "
				cprint(string[:-2]+"...") #[:-2] to cut off the extra ", " after the last element
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
			pass #don't print "Unknown command." for empty line
		else:
			cprint("Unknown command.")