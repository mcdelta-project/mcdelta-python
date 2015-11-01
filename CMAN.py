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

def mod_installed(modname):
	os.chdir(modfolder)
	files = glob.glob(modname + "-*.jar")
	return(len(files)>0)



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
		os.chdir(execdir + "/LocalData")
		if (os.path.exists("MinecraftForge.installed") == False):
			print("You must install Forge first!")
			return
		else:
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
		if (os.path.exists("Liteloader.installed") == False):
			print("You must install Liteloader first!")
			return
		else:
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
		f = open(modname+".installed", "w") #adding file as "installed" flag, temporary way to detect installer mods
		f.close()
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
		files = glob.glob(modname + "-*.jar")
		for file in files:
			if(input("Delete \""+file+"\"? Type OK to delete, or anything else to skip: ") == "OK"):
				os.remove(file)
				print("Deleted \""+file+"\".")
			else:
				print("Skipped \""+file+"\".")
	else:
		print("Mod not installed.")


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
	print(" update: update the CMAN archive")
	print(" help: display this help message")
	print(" version: display the CMAN version number")
	print(" exit: exit CMAN")

print("CMAN v"+version)
print_help()
while(True):
	os.chdir(execdir + "/LocalData/") #reset current working dir
	command = input("> ")
	if(command.split(" ")[0] == "update"):
		update_archive()
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
