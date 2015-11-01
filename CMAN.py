import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile



def get_json(mod):
	if(os.path.exists(execdir + "/LocalData/CMAN-Archive")):
		os.chdir(execdir + "/LocalData/CMAN-Archive")
	else:
		print("Archive not found. Please update archive.")
		return(-1)
	if(os.path.exists(mod + ".json")):
		# JSON parsing
		with open(mod + ".json") as json_file:
			json_data = json.load(json_file)
			return(json_data)
	else:
		return(None)

def mod_installed(mod):
	os.chdir(execdir + "/LocalData")
	return(os.path.exists(modname + ".json"))



def update_archive():
	#Delete old archive
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
	print(tarlist)
	os.rename(tarlist[0], "CMAN-Archive")

def install_mod():
	os.chdir(execdir + "/LocalData/CMAN-Archive")
	modname = input("Enter mod name.")
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
		if (input("This mod may be unstable. Type OK to install, or anything else to cancel.") == "OK"):
			pass
		else:
			return
	if (modtype == "Basemod"):
		pass
	elif (modtype == "Forge"):
		os.chdir(execdir + "/LocalData")
		if (os.path.exists("MinecraftForge.json") == False):
			print("You must install Forge first!")
			return
		else:
			url = json_data["Link"]
			version = json_data["Version"]
			print(modname + " is at version " + version)
			file_name = modname + "-" + version + ".jar"
			f = open(modname+".installed", "w") #adding file as "installed" flag
			f.close()
			os.chdir(modfolder)
			print("Downloading " + url + " as " + file_name)
			with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
				shutil.copyfileobj(response, out_file)
			print("Done.")

	elif (modtype == "Liteloader"):
		os.chdir(execdir + "/LocalData")
		if (os.path.exists("Liteloader.json") == False):
			print("You must install Liteloader first!")
			return
		else:
			url = json_data["Link"]
			version = json_data["Version"]
			print(modname + " is at version " + version)
			file_name = modname + "-" + version + ".litemod"
			f = open(modname+".installed", "w") #adding file as "installed" flag
			f.close()
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
		f = open(modname+".installed", "w") #adding file as "installed" flag
		f.close()
		os.chdir(execdir)
		files = os.listdir(execdir)

		print("Downloading " + url + " as " + file_name)
		with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
		print("Done. Please run the installer.")


def remove_mod():
	mod = input("Enter mod name.")
	os.chdir(modfolder)
	#find file(s) with name
	#if one file, delete it
	#if more than one, list names and ask which one or all to delete

def get_deps(mod):
	deps = json_data["Requirements"]
	return(deps)

def install_deps(mod):
	deps = get_deps(mod, json_data)
	for dep in deps:
		if(not mod_installed(dep)):
			install_mod(dep)

def print_info(mod, json_data):
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




def get_info():
	modname = input("Enter mod name.")
	json_data = get_json(modname)
	if(json_data == -1):
		return
	else:
		if (json_data != None):
			print_info(modname, json_data)
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
	modfolder = input("Where is your mods folder? (absolute paths)")
	f = open('config.json', 'w+')
	f.write('{"modfolder":"' + modfolder + '"}')

while(True):
	command = input(
		"What do you want to do? update (the archive), install (a mod) or remove (a mod), (get) info (about a mod), or exit?")
	if(command == "update"):
		#update_archive()
		pass
	if(command == "install"):
		#update_archive()
		install_mod()
	if(command == "remove"):
		remove_mod()
	if(command == "info"):
		get_info()
	if(command == "exit"):
		sys.exit()
