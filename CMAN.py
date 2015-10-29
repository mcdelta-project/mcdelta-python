import urllib.request
import shutil
import os
import glob
import json


print("You are running " + os.name)
if (os.path.exists("Data") == False):  # cleaning out Data directory
    os.mkdir("Data")
os.chdir("Data")
for file in glob.glob("*"):
    os.remove(file)

command = input()

if(command == "update"):
	update_archive()
if(command == "install"):
	update_archive()
	find_mod()
	install_mod()
if(command == "remove"):
	remove_mod()


def update_archive:
	url = "http://html.williambl.com/CMAN/CMAN.tar.gz"  # Archive Download
	file_name = "CMAN.tar.gz"
	# Download it.
	with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
	    shutil.copyfileobj(response, out_file)
	print("Done.")

	print("Extracting Archive...")
	tar = tarfile.open("CMAN.tar.gz") // untar
	tar.extractall()
	tarlist = tar.getnames()
	print(tarlist)


def find_mod:
	mod = input("Enter mod name.")
	if(os.path.exists(modname + ".json")):  # Telling user that file exists
		for file in glob.glob(modname + ".json"):
		print(file + " found.")
	else:
		print("Mod not found.")

	# JSON parsing, to get download link
	with open(modname + ".json") as json_file:
    json_data = json.load(json_file)
    pass  # I need help getting the download link from the JSON...


def install_mod:
	pass  # Add code to download file and move to mods directory


def remove_mod:
	mod = input("Enter mod name.")
	pass
