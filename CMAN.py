import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile


def update_archive():
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


def install_mod():
	modname = input("Enter mod name.")
	if(os.path.exists(modname + ".json")):  # Telling user that file exists
		for file in glob.glob(modname + ".json"):
			print(file + " found.")
	else:
		print("Mod not found.")
		sys.exit()

	# JSON parsing, to get download link
	with open(modname + ".json") as json_file:
		json_data = json.load(json_file)

	# Install
	modtype = json_data["Type"]
	if (modtype == Basemod):
		pass
	elif (modtype == Forge):
		os.chdir(execdir + "/LocalData")
		if (os.path.exists(Forge.json) == False):
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

	elif (modtype == Liteloader):
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

	elif (modtype == Installer):
		os.chdir(execdir)


def remove_mod():
	mod = input("Enter mod name.")
	pass

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

command = input(
	"What do you want to do? update (the archive), install (a mod) or remove (a mod)?")
if(command == "update"):
	update_archive()
if(command == "install"):
	update_archive()
	install_mod()
if(command == "remove"):
	remove_mod()
