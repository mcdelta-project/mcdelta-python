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
instance = "@ERROR@"

def init_config_install(data): #data is a 4-tuple
	global modfolder, versionsfolder, execdir, instance #makes it edit the global vars rather than create new ones
	modfolder, versionsfolder, execdir, instance = data

def install_mod(modname):
	os.chdir(execdir + "/Data/CMAN-Archive")
	if(modname == None):
		modname = input("Enter mod name: ")

	if(os.path.exists(modname + ".json")):  # Telling user that file exists
		for file in glob.glob(modname + ".json"):
			print(file + " found.")
	else:
		print("Mod "+modname+" not found.")
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
			wanttoinstall = input("Do you want to install it? Y or n?")
			if(wanttoinstall == "Y"):
				install_mod(requirement)
			elif(wanttoinstall == "n"):
				return
	recommendations = json_data["Recommended"]
	for recommendation in recommendations:
		if (os.path.exists(recommendation + ".installed") == False):
			print("This mod recommends " + recommendation + "!")
			wanttoinstall = input("Do you want to install it? Y or n?")
			if(wanttoinstall == "Y"):
				install_mod(recommendation)
				return
			elif(wanttoinstall == "n"):
				pass
	incompatibilities = json_data["Incompatibilities"]
	for incompatibility in incompatibilities:
		if (os.path.exists(incompatibility + ".installed") == True):
			print("You cannot have " + incompatibility + " and " + modname + " installed at the same time!")
			return
	if (modtype == "Basemod"):
		os.chdir(execdir + "/Data/temp")
		url = json_data["Link"]
		version = json_data["Version"]
		mcversions = json_data["MCVersion"]
		print(modname + " is at version " + version)
		file_name = modname + "-" + version + "-CMANtemp.zip"
		print("Downloading " + url)
		with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
		zipfile.ZipFile(file_name).extractall(path="./"+modname)
		vname = input("Enter name (as displayed in launcher) of minecraft instance to install into (compatible versions: "+display_versions(mcversions)+"): ")
		#cannot check for compatibility because you may be installing into a modded jar with a nonstandard name
		vpath = os.path.join(versionsfolder, vname)
		while(not os.path.exists(vpath)):
			print("The instance you selected was not found. Select another instance.")
			vname = input("Enter name (as displayed in launcher) of minecraft instance to install into (compatible versions: "+display_versions(mcversions)+"): ")
			vpath = os.path.join(versionsfolder, vname)
		jarname = vname+".jar"
		jarpath = os.path.join(vpath, jarname)
		foldername =  modname + "-" + version #the default version folder name
		foldernamefinal = input("Enter install folder name or leave blank for default (default: "+foldername+"): ")
		if(foldername == ""):
			foldernamefinal = foldername
		newjarname = foldername+".jar"
		print("Installing on version "+vname+" as "+foldernamefinal+".")
		if(os.path.exists(os.path.join(versionsfolder, foldernamefinal))):
			if(input("The folder "+foldernamefinal+" already exists. Type OK to overwrite, or anything else to choose a new name: ") == "OK"):
				shutil.rmtree(os.path.join(versionsfolder, foldernamefinal))
			else:
				foldernamefinal = input("Enter new install folder name (current name: "+foldernamefinal+"): ")
		folderpath = os.path.join(versionsfolder, foldernamefinal)
		shutil.copytree(vpath, folderpath)
		fix_names(folderpath, vname, foldernamefinal)
		zipfile.ZipFile(os.path.join(versionsfolder, foldernamefinal, newjarname)).extractall(path="./"+file_name+"CMANtemp")
		mergedirs(modname, file_name+"CMANtemp")
		os.chdir(file_name+"CMANtemp")
		shutil.rmtree("META-INF") #delete META-INF
		print("Making jar (this might take a while).")
		shutil.make_archive("../"+foldername, "zip")
		shutil.move("../"+foldername+".zip", folderpath+"/"+foldernamefinal+".jar")
		os.chdir("../../LocalData") #get back to LocalData
		print("Done.")

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

def install_deps(modname):
	deps = get_deps(modname)
	for dep in deps:
		if(not mod_installed(dep)):
			install_mod(dep)
