import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile


def update_archive():
	# Archive Download
	os.chdir(execdir + "/Data/")
	url = "https://github.com/Comprehensive-Minecraft-Archive-Network/CMAN-Archive/raw/master/Archive.tar.gz"
	file_name = "CMAN.tar.gz"
	print("Downloading Archive...")
	# Download it.
	with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
		shutil.copyfileobj(response, out_file)
	print("Done.")

	print("Extracting Archive...")
	tar = tarfile.open("CMAN.tar.gz")  # Untar
	tar.extractall()
	tarlist = tar.getnames()
	print(tarlist)


def install_mod():
	modname = input("Enter mod name.")
	if(os.path.exists(modname + ".json")):  # Telling user that file exists
		for file in glob.glob(modname + ".json"):
			print(file + " found.")
	else:
		print("Mod not found.")  # Or not
		sys.exit()

	# JSON parsing, to get download link
	with open(modname + ".json") as json_file:
		json_data = json.load(json_file)  # Load JSON

	# Install
	modtype = json_data["Type"]  # Work out which type of mod it is
	IsUnstable = json.loads(json_data["Unstable"])
	if (IsUnstable == True):
		if (input("This mod may be unstable. Type OK to install, or anything else to cancel.") == "OK"):
			pass
		else:
			sys.exit()

	if (os.path.exists("../LocalData/" + modname + ".json") == True):  # Making sure that the mod is not already installed
		print(modname + "Is already installed!")
		sys.exit()

	originalfile = execdir + "/Data/" + modname + ".json"  # Saving Modname.json for future reference
	os.chdir(execdir + "/LocalData/ModsDownloaded/")
	newfilename = modname + ".json_data"
	newfile = open(newfilename, 'w+')
	shutil.copyfile(originalfile, newfilename)

	if (modtype == "Basemod"):
		pass
	elif (modtype == "Forge"):
		os.chdir(execdir + "/LocalData")
		if (os.path.exists(MinecraftForge.json) == False):
			print("You must install Forge first!")
			sys.exit()
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
			sys.exit()

	elif (modtype == "Liteloader"):
		os.chdir(execdir + "/LocalData")
		if (os.path.exists(Liteloader.json) == False):
			print("You must install Liteloader first!")
			sys.exit()
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
			sys.exit()

	elif (modtype == "Installer"):
		os.chdir(execdir)
		url = json_data["Link"]
		version = json_data["Version"]
		print(modname + " is at version " + version)
		file_name = json_data["InstallerName"]
		os.chdir(execdir)
		print("Downloading " + url + " as " + file_name)
		with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
		print("Done. Please run the installer.")
		sys.exit()


def remove_mod():
	mod = input("Enter mod name.")
	pass

def upgrade_mod():
	pass


# Start Program Here:
print("You are running " + sys.platform)
if (os.path.exists("Data") == False):
	os.mkdir("Data")
if (os.path.exists("LocalData") == False):
	os.mkdir("LocalData")
if (os.path.exists("LocalData/ModsDownloaded") == False):
	os.mkdir("LocalData/ModsDownloaded")

execdir = os.getcwd()
print(execdir)

os.chdir("Data")
for file in glob.glob("*"):
	os.remove(file)  # cleaning out Data directory


# Finding out whether config exists
os.chdir("../LocalData/")
if (os.path.exists("config.json") == True):
	with open("config.json") as json_file:
		json_data = json.load(json_file)
	modfolder = json_data["modfolder"]  # If config exists, get modfolder from that. Else, ask for it.
	print(modfolder)
else:
	modfolder = input("Where is your mods folder? (absolute paths)")
	f = open('config.json', 'w+')
	f.write('{"modfolder":"' + modfolder + '"}')

command = input("What do you want to do? update (the archive), install (a mod), upgrade (a mod) or remove (a mod)?")
if(command == "update"):
	update_archive()
if(command == "install"):
	update_archive()
	install_mod()
if(command == "remove"):
	remove_mod()
if(command == "upgrade"):
	upgrade_mod()
else:
	print("Unknown command")