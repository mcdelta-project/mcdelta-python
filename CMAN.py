import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile

version = "0.0.1"

def get_json(modname):
	if(os.path.exists(execdir + "/LocalData/CMAN-Archive")):
		os.chdir(execdir + "/LocalData/CMAN-Archive")
	else:
		print("CMAN archive not found. Please update archive.")
		return(-1)
	if(os.path.exists(modname + ".json")):
		# JSON parsing
		with open(modname + ".json") as json_file:
			json_data = json.load(json_file)
			return(json_data)
	else:
		return(None)

def get_installed_json(modname):
	if(os.path.exists(execdir + "/LocalData/installed")):
		os.chdir(execdir + "/LocalData/installed")
	else:
		return(False) #no mods installed, so obviously modname isn't installed
	if(os.path.exists(modname + ".json")):
		# JSON parsing
		with open(modname + ".json") as json_file:
			json_data = json.load(json_file)
			return(json_data)
	else:
		return(None)

def mod_installed(modname):
	os.chdir(modfolder)
	files = glob.glob(modname + "-*.jar")
	return(len(files)>0)


def get_installed_jsons():
	jsons = []
	if(os.path.exists(execdir + "/LocalData/installed")):
		mods = os.listdir(execdir + "/LocalData/installed")
		os.chdir(execdir + "/LocalData/installed")
		for mod in mods:
			json_data = get_installed_json(mod[:-5])
			jsons.append(json_data)
		return jsons
	else:
		return([])



def update_archive():
	return #blocks updating for debug
	#Delete old archive
	if(os.path.exists(execdir + "/LocalData/CMAN-Archive")):
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
	os.rename(tarlist[0], "CMAN-Archive")
	print("Done.")

def install_mod(modname):
	os.chdir(execdir + "/LocalData/CMAN-Archive")
	if(modname == None):
		modname = input("Enter mod name: ")

	if(os.path.exists(modname + ".json")):  # Telling user that file exists
		for file in glob.glob(modname + ".json"):
			print(file + " found.")
	else:
		print("Mod not found.")
		return

	json_data = get_json(modname)

	# Install
	modtype = json_data["Type"]
	IsUnstable = json.loads(json_data["Unstable"])
	if (IsUnstable == True):
		if (input("This mod may be unstable. Type OK to install, or anything else to cancel: ") == "OK"):
			pass
		else:
			print("Install canceled.")
			return
	if (modtype == "Basemod"):
		print("Not Implemented.")
		pass
	elif (modtype == "Forge"):
		os.chdir(execdir + "/LocalData/installed")
		if (os.path.exists("MinecraftForge.json") == False):
			print("You must install Forge first!")
			return
		else:
			os.chdir(execdir + "/LocalData")
			url = json_data["Link"]
			version = json_data["Version"]
			print(modname + " is at version " + version)
			file_name = modname + "-" + version + ".jar"
			shutil.copy(execdir + "/LocalData/CMAN-Archive/"+modname+".json", execdir + "/LocalData/installed") #copying json to /localdata/installed, keeps version data
			os.chdir(modfolder)
			print("Downloading " + url + " as " + file_name)
			with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
				shutil.copyfileobj(response, out_file)
			print("Done.")

	elif (modtype == "Liteloader"):
		os.chdir(execdir + "/LocalData/installed")
		if (os.path.exists("Liteloader.json") == False):
			print("You must install Liteloader first!")
			return
		else:
			os.chdir(execdir + "/LocalData")
			url = json_data["Link"]
			version = json_data["Version"]
			print(modname + " is at version " + version)
			file_name = modname + "-" + version + ".litemod"
			shutil.copy(execdir + "/LocalData/CMAN-Archive/"+modname+".json", execdir + "/LocalData/installed") #copying json to /localdata/installed, keeps version data
			os.chdir(modfolder)
			print("Downloading " + url + " as " + file_name)
			with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
				shutil.copyfileobj(response, out_file)
			print("Done.")

	elif (modtype == "Installer"):
		os.chdir(execdir + "/LocalData")
		url = json_data["Link"]
		version = json_data["Version"]
		print(modname + " is at version " + version)
		file_name = json_data["InstallerName"]
		shutil.copy(execdir + "/LocalData/CMAN-Archive/"+modname+".json", execdir + "/LocalData/installed") #copying json to /localdata/installed, keeps version data. Also is a temporary way to check for the installation of mods that use installers (doesn't actually detect whether the user ran the installer, or that it is the right version)
		os.chdir(execdir)
		files = os.listdir(execdir)

		print("Downloading " + url + " as " + file_name)
		with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
		print("Done. Please run the installer.")


def remove_mod(modname): #behavior not guaranteed on mods installed outside of CMAN
	if(modname == None):
		modname = input("Enter mod name: ")
		print(mod_installed(modname))
	if(mod_installed(modname)):
		os.chdir(modfolder)
		files = glob.glob(modname + "-*.jar") #get all versions of mod
		for file in files:
			if(input("Delete \""+file+"\"? Type OK to delete, or anything else to skip: ") == "OK"):
				os.remove(file)
				print("Deleted \""+file+"\".")
			else:
				print("Skipped \""+file+"\".")
		os.remove(execdir + "/LocalData/installed/"+modname+".json") #removing json in "installed" dir
	else:
		print("Mod not installed.")


def update_mod(modname):
	os.chdir(execdir + "/LocalData/CMAN-Archive")
	if(modname == None):
		modname = input("Enter mod name: ")
	update = [get_installed_json(modname),get_json(modname)]
	if(os.path.exists(modname + ".json")):  # Telling user that file exists
		for file in glob.glob(modname + ".json"):
			print(file + " found.")
	else:
		print("Mod not found.")
		return
	os.chdir(execdir + "/LocalData") #restoring current working dir
	if(update[1]["Version"] != update[0]["Version"] and mod_installed(modname)):
		remove_mod(modname)
		install_mod(modname)
	elif(not mod_installed(modname)):
		print(modname+" is not installed.")
	else:
		print(modname+" is already up to date.")



def get_deps(modname):
	json_data = get_json(modname)
	deps = json_data["Requirements"]
	return(deps)

def install_deps(modname):
	deps = get_deps(modname)
	for dep in deps:
		if(not mod_installed(dep)):
			install_mod(dep)

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
			print("Mod not found.")



print("You are running " + sys.platform)
if (os.path.exists("Data") == False):
	os.mkdir("Data")
if (os.path.exists("LocalData") == False):
	os.mkdir("LocalData")
execdir = os.getcwd()
print(execdir)
os.chdir("Data")
for file in glob.glob("*"):
	os.remove(file)  # cleaning out Data directory


os.chdir("../LocalData/")
if (os.path.exists("config.json") == True):
	with open("config.json") as json_file:
		json_data = json.load(json_file)
	modfolder = json_data["modfolder"]
	print(modfolder)
else:
	modfolder = input("Enter mod folder location (absolute path): ")
	f = open('config.json', 'w+')
	f.write('{"modfolder":"' + modfolder + '"}')


def print_help():
	print("Commands:")
	print(" install 'mod': install the mod 'mod'")
	print(" info 'mod': get info for the mod 'mod'")
	print(" remove 'mod': remove the mod 'mod'")
	print(" update 'mod': update the mod 'mod'")
	print(" updateall: update all outdated mods")
	print(" updates: list available mod updates")
	print(" arcupdate: update the CMAN archive")
	print(" help: display this help message")
	print(" version: display the CMAN version number")
	print(" exit: exit CMAN")

def get_updates():
	update_archive()
	updates = []
	mods = get_installed_jsons()
	for mod in mods:
		json_data = get_json(mod["Name"])
		if(json_data["Version"] != mod["Version"]):
			updates.append([mod,json_data]) #append list of jsons for installed version and newest version 
	return(updates)


def check_updates(list): #list is a flag for whether to print list of updates or just updates available message
	updates = get_updates()
	if(len(updates)>0):
		if(not list):
			print("\nMod updates available!")
		else:
			for update in updates:
				print("Available Updates:")
				print(" "+update[0]["Name"]+" (current version: "+update[1]["Version"]+", you have: "+update[0]["Version"]+")")
	else:
		if(list): #don't print "no updates available" on startup
			print("No updates available.")



print("CMAN v"+version)
print_help()
check_updates(False)
while(True):
	os.chdir(execdir + "/LocalData/") #reset current working dir
	command = input("> ")
	if(command.split(" ")[0] == "arcupdate"):
		update_archive()
	elif(command.split(" ")[0] == "updates"):
		check_updates(True)
	elif(command.split(" ")[0] == "update"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			updates = get_updates() #not updating archive because get_updates does it
			update_mod(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			updates = get_updates() #not updating archive because get_updates does it
			update_mod(mod)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "updateall"):
		updates = get_updates() #not updating archive because get_updates does it
		if(len(updates) == 0):
			print("All mods up to date.")
		else:
			for update in updates:
				update_mod(update[0]["Name"])
	elif(command.split(" ")[0] == "install"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			update_archive()
			install_mod(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			update_archive()
			install_mod(mod)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "remove"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			remove_mod(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			remove_mod(mod)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "info"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			get_info(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			get_info(mod)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "version"):
		print("CMAN v"+version)
	elif(command.split(" ")[0] == "help" or command.split(" ")[0] == "?"):
		print_help()
	elif(command.split(" ")[0] == "exit"):
		sys.exit()
	elif(command == ""):
		pass #don't print "Invalid command." for empty line
	else:
		print("Invalid command.")
