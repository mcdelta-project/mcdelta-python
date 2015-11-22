import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
from CMAN_util import *
import CMAN_install
import CMAN_remove

modfolder = "@ERROR@"
versionsfolder = "@ERROR@"
execdir = "@ERROR@"

def init_config_upgrade(data): #data is a 3-tuple
	global modfolder, versionsfolder, execdir #makes it edit the global vars rather than create new ones
	modfolder, versionsfolder, execdir = data

def upgrade_mod(modname):
	os.chdir(execdir + "/Data/CMAN-Archive")
	if(modname == None):
		modname = input("Enter mod name: ")
	update = [get_installed_json(modname),get_json(modname)]
	if(os.path.exists(os.path.join(execdir + "/LocalData/ModsDownloaded", modname + ".installed"))):  # Telling user that file exists
		for file in glob.glob(modname + ".installed"):
			print(file + " found.")
	else:
		print("Mod "+modname+" not found.")
		return
	os.chdir(execdir + "/LocalData") #restoring current working dir
	if(update[1]["Version"] != update[0]["Version"] and mod_installed(modname)):
		remove_mod(modname)
		install_mod(modname)
	elif(not mod_installed(modname)):
		print(modname+" is not installed.")
	else:
		print(modname+" is already up to date.")

def get_upgrades(): #returns a list of 2-element lists of jsons (in which index 0 is the version you have and index 1 is the newest version)
	updates = []
	mods = get_installed_jsons()
	for mod in mods:
		if(mod != None):
			json_data = get_json(mod["Name"])
			if(json_data != None and json_data["Version"] != mod["Version"]):
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