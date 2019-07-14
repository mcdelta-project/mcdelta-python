import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
from delta_util import *

modfolder = "@ERROR@"
jarfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"

def init_config_importexport(data): #data is a 5-tuple
	global modfolder, jarfolder, mc_version, execdir, instance, gui #makes it edit the global vars rather than create new ones
	modfolder, jarfolder, mc_version, execdir, instance, gui = data

def recieve_tkinst_importexport(data):
	global tkinst
	tkinst = data

def export_mods(filename):
	if (filename == None):
		filename = cinput("What would you like your new modlist to be called?")
	os.chdir(execdir)
	os.chdir("LocalData/Modlists")
	mods = []
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+instance)):
		mods = os.listdir(execdir + "/LocalData/ModsDownloaded/"+instance)
		i = 0
		for modtmp in mods:
			cprint(modtmp)
			modtmp = modtmp[:-10]
			modtmp = '"' + modtmp + '"'
			cprint(modtmp)
			mods[i] = modtmp
			i += 1
		cprint('{ "Mods":' + json.dumps(mods) + "}")
		f = open(filename + '.modlist', 'w')
		f.write('{ "Mods":' + json.dumps(mods) + '}')
		f.close()
		cprint("Done! now in LocalData/Modlists.")
		os.chdir(execdir)
	else:
		return

def import_mods(path):
	if (path == None):
		path = cinput("Please enter the path to the modlist.")

	if(os.path.exists(path)):  # Telling user that file exists
		cprint(path + " found.")
	else:
		cprint(path + " not found.")
		return

	json_data = json.load(path)

	mods = []

	mods = json_data["Mods"]
	for mod in mods:
			cprint(mod)
			delta_install.install_mod(mod)
