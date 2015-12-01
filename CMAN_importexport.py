import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
from CMAN_util import *

modfolder = "@ERROR@"
versionsfolder = "@ERROR@"
execdir = "@ERROR@"

def init_config_importexport(data): #data is a 3-tuple
	global modfolder, versionsfolder, execdir #makes it edit the global vars rather than create new ones
	modfolder, versionsfolder, execdir = data

def export_mods(filename):
	if (filename == None):
		filename = input("What would you like your new modlist to be called?")
	os.chdir(execdir)
	os.chdir("LocalData/Modlists")
	mods = []
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded")):
		mods = os.listdir(execdir + "/LocalData/ModsDownloaded")
		i = 0
		for modtmp in mods:
			print(modtmp)
			modtmp = modtmp[:-10]
			modtmp = '"' + modtmp + '"'
			print(modtmp)
			mods[i] = modtmp
			i += 1
		print('{ "Mods":' + json.dumps(mods) + "}")
		f = open(filename + '.modlist', 'w')
		f.write('{ "Mods":' + json.dumps(mods) + '}')
		f.close()
		print("Done! now in LocalData/Modlists.")
		os.chdir(execdir)
	else:
		return

def import_mods(path):
	if (path == None):
		path = input("Please enter the path to the modlist.")

	if(os.path.exists(path)):  # Telling user that file exists
		print(path + " found.")
	else:
		print(path + " not found.")
		return

	json_data = get_json(path)

	mods = []

	mods = json_data["Mods"]
	for mod in mods:
			print(mod)
			CMAN_install.install_mod(mod)
