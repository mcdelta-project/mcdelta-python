import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
import argparse
import CMAN_remove
import CMAN_upgrade
import CMAN_install
import CMAN_importexport
from CMAN_util import *

version = "1.2.0"

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
	with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
		shutil.copyfileobj(response, out_file)
	print("Done.")

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
			print(json_data["Name"]+":")
			print("\tVersion: "+json_data["Version"]+" ("+stable+")")
			print("\tAuthor(s): "+json_data["Author"])
			print("\tDescription: "+json_data["Desc"])
			print("\tRequirements: "+str(json_data["Requirements"]))
			print("\tKnown Incompatibilities: "+str(json_data["Incompatibilities"]))
			print("\tDownload Link: "+str(json_data["Link"]))
			print("\tLicense: "+json_data["License"])
		else:
			print("Mod "+modname+" not found.")

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
# Start Program Here:

instance = read_default_instance()

parser = argparse.ArgumentParser(description="CMAN: the Comprehensive Minecraft Archive Network")

parser.add_argument("-i", "--install", help="install mod", metavar="MOD", default="None")
parser.add_argument("-r", "--remove", help="remove mod", metavar="MOD", default="None")
parser.add_argument("-u", "--upgrade", help="upgrade mod", metavar="MOD", default="None")
parser.add_argument("--info", help="give info about a mod", metavar="MOD", default="None")
parser.add_argument("-e", "--export", help="export a modlist", metavar="FILENAME", default="None")
parser.add_argument("--import", help="import a modlist", metavar="MODLIST", default="None", dest="importa") # importa because import is already taken  
parser.add_argument("-I", "--instance", help="sets the Minecraft instance to install into", metavar="INSTANCE", default=instance)
args = parser.parse_args()

print("You are running " + sys.platform)
#not making Data dir here because it is done later
if (os.path.exists("LocalData") == False):
	os.mkdir("LocalData")
if (os.path.exists("LocalData/ModsDownloaded") == False):
	os.mkdir("LocalData/ModsDownloaded")
if (os.path.exists("LocalData/Modlists") == False):
	os.mkdir("LocalData/Modlists")
if (os.path.exists("Data/temp") == False):
	os.mkdir("Data/temp")
try:
	shutil.rmtree("Data") #deleting Data dir
except(FileNotFoundError): #Data dir not present
	pass

os.mkdir("Data") #creating new Data dir
execdir = os.getcwd()
def setup_config(_instance):
	global modfolder, versionsfolder, instance
	os.chdir(os.path.join(execdir, "LocalData"))
	instance = _instance
	modfolder, versionsfolder = read_config(_instance) #gets config stuff
	os.chdir(execdir)
	init_config_util((modfolder, versionsfolder, execdir, instance)) #transferring config data to all files
	CMAN_install.init_config_install((modfolder, versionsfolder, execdir, instance))
	CMAN_remove.init_config_remove((modfolder, versionsfolder, execdir, instance))
	CMAN_upgrade.init_config_upgrade((modfolder, versionsfolder, execdir, instance))
	CMAN_importexport.init_config_importexport((modfolder, versionsfolder, execdir, instance))

setup_config(instance)

with open("LocalData/config.json") as json_file:
	json_data = json.load(json_file)
	insts = json_data.keys()
for inst in insts:
	if(not os.path.exists(os.path.join(execdir, "LocalData/ModsDownloaded/"+inst))): #creating modsdownloaded subdirs for each instance
		os.mkdir(os.path.join(execdir, "LocalData/ModsDownloaded/"+inst))

def print_help():
	print("Commands:")
	print(" install 'mod': install the mod 'mod'")
	print(" installm: install multiple mods")
	print(" info 'mod': get info for the mod 'mod'")
	print(" remove 'mod': remove the mod 'mod'")
	print(" removem: remove multiple mods")
	print(" upgrade 'mod': upgrade the mod 'mod'")
	print(" upgradem: upgrade multiple mods")
	print(" upgradeall: upgrade all outdated mods")
	print(" upgrades 'inst': list available mod upgrades for Minecraft instance 'inst', or use '*' to check all instances")
	print(" update: update the CMAN archive")
	print(" help: display this help message")
	print(" version: display the CMAN version number")
	print(" list: list installed mods")
	print(" export 'name': export a modlist with the name 'name' , which can be imported later")
	print(" import 'pathtomodlist': import the modlist 'pathtomodlist'")
	print(" inst 'inst': switches to Minecraft instance 'inst'")
	print(" defaultinst 'inst': sets default Minecraft instance to 'inst'")
	print(" addinst 'inst': adds the Minecraft instance 'inst'")
	print(" rminst 'inst': removes the Minecraft instance 'inst'")
	print(" insts: lists all Minecraft instances")
	print(" exit: exit CMAN")

update_archive()
print("CMAN v"+version)
if (args.instance != "None"):
	instance = args.instance
print("Selected Instance: "+instance)
check_for_updates()
upgradesavailable = CMAN_upgrade.get_upgrades(instance)
if (upgradesavailable == []):
	pass
else:
	print("The following upgrades are available for instance "+instance+":")
	for upgrade in upgradesavailable:
		print(" "+upgrade[0]["Name"]+" (current version: "+upgrade[1]["Version"]+", you have: "+upgrade[0]["Version"]+")")
if (args.install != "None"):
	CMAN_install.install_mod(args.install)
if (args.remove != "None"):
	CMAN_remove.remove_mod(args.remove)
if (args.upgrade != "None"):
	CMAN_upgrade.upgrade_mod(args.upgrade)
if (args.info != "None"):
	get_info(args.info)
if (args.export != "None"):
	CMAN_importexport.export_mods(args.export)
if (args.importa != "None"):
	CMAN_importexport.import_mods(args.importa)

print_help()

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
			update_archive()
			CMAN_upgrade.check_upgrades(True, inst)
		elif(len(command.split(" ")) == 1):
			inst = input("Enter instance name: ")
			if(inst == "*"):
				inst = None
			update_archive()
			CMAN_upgrade.check_upgrades(True, inst)
		else:
			print("Invalid command syntax.")
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
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "upgradeall"):
		update_archive()
		updates = CMAN_upgrade.get_upgrades()
		if(len(updates) == 0):
			print("All mods up to date.")
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
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "remove"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			CMAN_remove.remove_mod(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			CMAN_remove.remove_mod(mod)
		else:
			print("Invalid command syntax.")
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
			print(string[:-2]+"...") #[:-2] to cut off the extra ", " after the last element
			for item in modslist:
				CMAN_install.install_mod(item)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "removem" or command.split(" ")[0] == "removemany"):
		if(len(command.split(" ")) >= 2):
			modslist = command.split(" ")[1:] #separate mod names with spaces
			update_archive()
			string = "Attempting to remove: "
			for item in modslist:
				string = string + item+", "
			print(string[:-2]+"...") #[:-2] to cut off the extra ", " after the last element
			for item in modslist:
				CMAN_remove.remove_mod(item)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "upgradem" or command.split(" ")[0] == "upgrademany"):
		if(len(command.split(" ")) >= 2):
			modslist = command.split(" ")[1:] #separate mod names with spaces
			update_archive()
			string = "Attempting to upgrade: "
			for item in modslist:
				string = string + item+", "
			print(string[:-2]+"...") #[:-2] to cut off the extra ", " after the last element
			for item in modslist:
				CMAN_upgrade.upgrade_mod(item)
		else:
			print("Invalid command syntax.")
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
			print("Invalid command syntax.")
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
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "instance" or command.split(" ")[0] == "inst"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			name = command.split(" ")[1]
			if(instance_exists(name)):
				if(name == instance):
					print("Instance "+name+" already selected!")
				else:
					setup_config(name)
					print("Switched to instance "+name+".")
			else:
				print("Instance "+name+" does not exist.")
		elif(len(command.split(" ")) == 1):
			name = input("Enter instance name: ")
			if(instance_exists(name)):
				if(name == instance):
					print("Instance "+name+" already selected!")
				else:
					setup_config(name)
					print("Switched to instance "+name+".")
			else:
				print("Instance "+name+" does not exist.")
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "setdefaultinstance" or command.split(" ")[0] == "setdefaultinst"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			name = command.split(" ")[1]
			if(instance_exists(name)):
				if(name == read_default_instance()):
					print("Instance "+name+" already set as default!")
				else:
					with open("default_instance.txt", "w") as f:
						f.write(name)
					print("Set default instance as "+name+".")
			else:
				print("Instance "+instance+" does not exist.")
		elif(len(command.split(" ")) == 1):
			name = input("Enter instance name: ")
			if(instance_exists(name)):
				if(name == read_default_instance()):
					print("Instance "+instance+" already set as default!")
				else:
					with open("default_instance.txt", "w") as f:
						f.write(name)
					print("Set default instance as "+name+".")
			else:
				print("Instance "+name+" does not exist.")
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "addinstance" or command.split(" ")[0] == "addinst"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			name = command.split(" ")[1]
			if(instance_exists(name)):
				print("Instance "+name+" already exists.")
			else:
				new_config(name)
		elif(len(command.split(" ")) == 1):
			name = input("Enter instance name: ")
			if(instance_exists(name)):
				print("Instance "+name+" already exists.")
			else:
				new_config(name)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "rminstance" or command.split(" ")[0] == "removeinstance" or command.split(" ")[0] == "rminst"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			name = command.split(" ")[1]
			if(instance_exists(name)):
				rm_config(name)
			else:
				print("Instance "+name+" does not exist.")
		elif(len(command.split(" ")) == 1):
			name = input("Enter instance name: ")
			if(instance_exists(name)):
				rm_config(name)
			else:
				print("Instance "+name+" does not exist.")
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "instances" or command.split(" ")[0] == "insts"):
		with open("config.json") as json_file:
			json_data = json.load(json_file)
			insts = json_data.keys()
			print("Instances:")
			for inst in insts:
				if(inst == instance):
					print(inst+" (selected)")
				else:
					print(inst)
	elif(command.split(" ")[0] == "list"):
		listmods()
	elif(command.split(" ")[0] == "version"):
		print("CMAN v"+version)
	elif(command.split(" ")[0] == "help" or command.split(" ")[0] == "?"):
		print_help()
	elif(command.split(" ")[0] == "exit"):
		sys.exit()
	elif(command == ""):
		pass #don't print "Unknown command." for empty line
	else:
		print("Unknown command.")
