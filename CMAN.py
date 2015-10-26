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
	print("Downloading archive...")
	url = "http://modlist.mcf.li/api/v3/1.8.json"  # JSON link
	file_name = "CMAN.json"
	# Download it.
	with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
	    shutil.copyfileobj(response, out_file)
	print("Done.")


def find_mod:
	mod = input("Enter mod name.")
	with open("CMAN.json") as json_file:  # JSON parsing
    json_data = json.load(json_file)
    pass  # I need help getting the download link from the JSON...


def install_mod:
	pass  # Add code to download file and move to mods directory


def remove_mod:
	mod = input("Enter mod name.")
	pass
