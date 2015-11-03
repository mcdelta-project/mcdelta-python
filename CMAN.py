import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile

version = "0.0.1"

def get_json(modname):
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		os.chdir(execdir + "/Data/CMAN-Archive")
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
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded")):
		os.chdir(execdir + "/LocalData/ModsDownloaded")
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
	os.chdir(execdir + "/LocalData/ModsDownloaded/")
	files = glob.glob(modname + "-*.installed")
	return(len(files)>0)


def get_installed_jsons():
	jsons = []
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded")):
		mods = os.listdir(execdir + "/LocalData/ModsDownloaded")
		os.chdir(execdir + "/LocalData/ModsDownloaded")
		for mod in mods:
			json_data = get_installed_json(mod[:-5])
			jsons.append(json_data)
		return jsons
	else:
		return([])



def update_archive():
	#Delete old archive
	os.chdir(execdir + "/Data")
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		shutil.rmtree("CMAN-Archive")
	# Archive Download
	url = "https://github.com/Comprehensive-Minecraft-Archive-Network/CMAN-Archive/tarball/master/Archive.tar.gz"
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
	os.chdir(execdir + "/Data/CMAN-Archive")
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
	modtype = json_data["Type"] # Work out which type of mod it is
	IsUnstable = json.loads(json_data["Unstable"])
	if (IsUnstable == True):
		if (input("This mod may be unstable. Type OK to install, or anything else to cancel: ") == "OK"):
			pass
		else:
			print("Install canceled.")
			return 
	if (mod_installed(modname)):  # Making sure that the mod is not already installed
		print(modname + " is already installed!")
		return
 
	originalfile = execdir + "/Data/CMAN-Archive/" + modname + ".json"  # Saving Modname.json for future reference
	os.chdir(execdir + "/LocalData/ModsDownloaded/")
	newfilename = modname + ".installed"
	newfile = open(newfilename, 'w+')
	shutil.copyfile(originalfile, newfilename)
 
	requirements = json_data["Requirements"]
	for requirement in requirements:
		if (os.path.exists(requirement + ".installed") == False):
			print("You must install " + requirement + " first!")
			return
	incompatibilities = json_data["Incompatibilities"]
	for incompatibility in incompatibilities:
		if (os.path.exists(incompatibility + ".installed") == True):
			print("You cannot have " + incompatibility + " and " + modname + " installed at the same time!")
			return
	if (modtype == "Basemod"):
		print("Not Implemented.")
		pass
	elif (modtype == "Forge"):
		os.chdir(execdir + "/LocalData")
		url = json_data["Link"]
		version = json_data["Version"]
		print(modname + " is at version " + version)
		file_name = modname + "-" + version + ".jar"
		os.chdir(modfolder)
		print("Downloading " + url + " as " + file_name)
		with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
		print("Done.")

	elif (modtype == "Liteloader"):
		os.chdir(execdir + "/LocalData")
		url = json_data["Link"]
		version = json_data["Version"]
		print(modname + " is at version " + version)
		file_name = modname + "-" + version + ".litemod"
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
	print("Removing file for mod in ModsDownloaded")
	try:
		os.remove(execdir + "/LocalData/ModsDownloaded/"+modname+".installed") #removing json in ModsDownloaded dir
	except FileNotFoundError:
		print("Either " + modname + " is not installed, or something went horribly wrong.")
		return
	if(mod_installed(modname)):
		os.chdir(modfolder)
		files = glob.glob(modname + "-*.jar") #get all versions of mod
		for file in files:
			if(input("Delete \""+file+"\"? Type OK to delete, or anything else to skip: ") == "OK"):
				os.remove(file)
				print("Deleted \""+file+"\".")
			else:
				print("Skipped \""+file+"\".")
	else:
		print("I cannot remove installer mods or basemods! (If your mod is not an installermod or basemod, then something went horribly wrong.)")


def upgrade_mod(modname):
	os.chdir(execdir + "/Data/CMAN-Archive")
	if(modname == None):
		modname = input("Enter mod name: ")
	update = [get_installed_json(modname),get_json(modname)]
	if(os.path.exists(modname + ".installed")):  # Telling user that file exists
		for file in glob.glob(modname + ".installed"):
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


# Start Program Here:
print("You are running " + sys.platform)
#not making Data dir here because it is done later
if (os.path.exists("LocalData") == False):
	os.mkdir("LocalData")
if (os.path.exists("LocalData/ModsDownloaded") == False):
	os.mkdir("LocalData/ModsDownloaded")
execdir = os.getcwd()
print(execdir)
try:
	shutil.rmtree("Data") #deleting Data dir
except(FileNotFoundError): #Data dir not present
	pass
os.mkdir("Data") #creating new Data dir



os.chdir("LocalData")
if (os.path.exists("config.json") == True):
	with open("config.json") as json_file:
		json_data = json.load(json_file)
	modfolder = json_data["modfolder"] # If config exists, get modfolder from that. Else, ask for it.
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
	print(" upgrade 'mod': upgrade the mod 'mod'")
	print(" upgradeall: upgrade all outdated mods")
	print(" upgrades: list available mod upgrades")
	print(" update: update the CMAN archive")
	print(" help: display this help message")
	print(" version: display the CMAN version number")
	print(" exit: exit CMAN")

def get_upgrades():
	updates = []
	mods = get_installed_jsons()
	for mod in mods:
		if(mod != None):
			json_data = get_json(mod["Name"])
			if(json_data["Version"] != mod["Version"]):
				updates.append([mod,json_data]) #append list of jsons for installed version and newest version 
	return(updates)


def check_upgrades(full): #full is a flag for whether to print full list of updates or just updates available message
	updates = get_upgrades()
	if(len(updates)>0):
		if(not full):
			print("\nMod updates available!")
		else:
			for update in updates:
				print("Available Updates:")
				print(" "+update[0]["Name"]+" (current version: "+update[1]["Version"]+", you have: "+update[0]["Version"]+")")
	else:
		if(full): #don't print "no updates available" on startup
			print("No updates available.")


update_archive()
print("CMAN v"+version)
print_help()
upgradesavailible = get_upgrades()
if (upgradesavailible == []):
	pass
else:
	print("The following upgrades are availible:" + str(upgradesavailible))
while(True):
	os.chdir(execdir + "/LocalData/") #reset current working dir
	command = input("> ")
	if(command.split(" ")[0] == "update"):
		update_archive()
	elif(command.split(" ")[0] == "upgrades"):
		update_archive()
		check_upgrades(True)
	elif(command.split(" ")[0] == "upgrade"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			update_archive()
			upgrades = get_upgrades()
			update_mod(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			update_archive()
			upgrades = get_upgrades()
			upgrade_mod(mod)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "upgradeall"):
		update_archive()
		updates = get_upgrades()
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
		print("Unknown command.")
