import requests
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
from CMAN_util import *
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialogs
from modclass import Mod

modfolder = "@ERROR@"
jarfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"
tkinst = None

def init_config_install(data): #data is a 5-tuple
	global modfolder, jarfolder, execdir, instance, gui #makes it edit the global vars rather than create new ones
	modfolder, jarfolder, execdir, instance, gui = data

def recieve_tkinst_install(data):
	global tkinst
	tkinst = data


def install_mod(modname, version = None):
	os.chdir(execdir + "/Data/CMAN-Archive")
	if(modname == None):
		modname = cinput("Enter mod name: ")

	if(os.path.exists(modname + ".json")):  # Telling user that file exists
		for file in glob.glob(modname + ".json"):
			cprint(file + " found.")
	else:
		cprint("Mod "+modname+" not found.")
		return -1

	mod_data = get_mod_from_name(modname)

	# Install
	modtype = mod_data._type # Work out which type of mod it is
	IsUnstable = mod_data.unstable
	if (IsUnstable == True):
		if not gui:
			a = input("This mod may be unstable. Type OK to install, or anything else to cancel: ") == "OK"
		else:
			a = msgbox.askokcancel("Confirm Installation", "This mod may be unstable.\nClick OK to install.", parent=tkinst)
		if (a):
			pass
		else:
			cprint("Install canceled.")
			return
	if (mod_installed(modname)):  # Making sure that the mod is not already installed
		cprint(modname + " is already installed!")
		return

	originalfile = execdir + "/Data/CMAN-Archive/" + modname + ".json"  # Saving Modname.json for future reference
	if(not os.path.exists(execdir + "/LocalData/ModsDownloaded/"+instance)):
			os.mkdir(execdir + "/LocalData/ModsDownloaded/"+instance)
	os.chdir(execdir + "/LocalData/ModsDownloaded/"+instance)
	newfilename = modname + ".installed"
	newfile = open(newfilename, 'w+')
	shutil.copyfile(originalfile, newfilename)

	requirements = mod_data.requirements
	for requirement in requirements:
		if (os.path.exists(requirement + ".installed") == False):
			cprint("You must install " + requirement + " first!")
			if not gui:
				wanttoinstall = input("Do you want to install it? Y or n?") == "Y"
			else:
				wanttoinstall = msgbox.askyesno("Confirm Installation", "This mod requires " + requirement + ".\nInstall "+requirement+"?", parent=tkinst)
			if(wanttoinstall):
				install_mod(requirement)
			elif(not wanttoinstall):
				msgbox.showerror("Installation Canceled", "The installation has been canceled due to required mod "+requirement+" not being installed.", parent=tkinst)
				return -1
	recommended = mod_data.recommended
	for recommendation in recommended:
		if (os.path.exists(recommendation + ".installed") == False):
			cprint("This mod recommends " + recommendation + "!")
			if not gui:
				wanttoinstall = input("Do you want to install it? Y or n?") == "Y"
			else:
				wanttoinstall = msgbox.askyesno("Confirm Installation", "This mod recommends " + recommendation + ".\nInstall "+recommendation+"?", parent=tkinst)
			if(wanttoinstall):
				install_mod(recommendation)
			elif(not wanttoinstall):
				pass
	incompatibilities = mod_data.incompatibilities
	for incompatibility in incompatibilities:
		if (os.path.exists(incompatibility + ".installed") == True):
			msgbox.showerror("Installation Canceled", "The installation has been canceled due to incompatible mod "+incompatibility+" being installed.", parent=tkinst)
			return -1
	if (modtype == "Basemod"):
		os.chdir(execdir + "/Data/temp")
		version = get_latest_version(mod_data)
		mcversion = mod_data.Versions[3]
		url = get_url(mod_data, version)
		cprint(modname + " is at version " + version)
		file_name = modname + "-" + version + "-CMANtemp.zip"
		cprint("Downloading " + url)
		with open(file_name, 'wb') as out_file:
			response = requests.get(url)
			out_file.write(response.content)
		zipfile.ZipFile(file_name).extractall(path="./"+modname)
		vname = cinput("Enter name (as displayed in launcher) of minecraft instance to install into (compatible versions: "+display_versions(mcversions)+"): ")
		#cannot check for compatibility because you may be installing into a modded jar with a nonstandard name
		vpath = os.path.join(jarfolder, vname)
		while(not os.path.exists(vpath)):
			cprint("The instance you selected was not found. Select another instance.")
			vname = cinput("Enter name (as displayed in launcher) of minecraft instance to install into (compatible versions: "+display_versions(mcversions)+"): ")
			vpath = os.path.join(jarfolder, vname)
		jarname = vname+".jar"
		jarpath = os.path.join(vpath, jarname)
		foldername =  modname + "-" + version #the default version folder name
		foldernamefinal = cinput("Enter install folder name or leave blank for default (default: "+foldername+"): ")
		if(foldername == ""):
			foldernamefinal = foldername
		newjarname = foldername+".jar"
		cprint("Installing on version "+vname+" as "+foldernamefinal+".")
		if(os.path.exists(os.path.join(jarfolder, foldernamefinal))):
			if(cinput("The folder "+foldernamefinal+" already exists. Type OK to overwrite, or anything else to choose a new name: ") == "OK"):
				shutil.rmtree(os.path.join(jarfolder, foldernamefinal))
			else:
				foldernamefinal = cinput("Enter new install folder name (current name: "+foldernamefinal+"): ")
		folderpath = os.path.join(jarfolder, foldernamefinal)
		shutil.copytree(vpath, folderpath)
		fix_names(folderpath, vname, foldernamefinal)
		zipfile.ZipFile(os.path.join(jarfolder, foldernamefinal, newjarname)).extractall(path="./"+file_name+"CMANtemp")
		mergedirs(modname, file_name+"CMANtemp")
		os.chdir(file_name+"CMANtemp")
		shutil.rmtree("META-INF") #delete META-INF
		cprint("Making jar (this might take a while).")
		shutil.make_archive("../"+foldername, "zip")
		shutil.move("../"+foldername+".zip", folderpath+"/"+foldernamefinal+".jar")
		os.chdir("../../LocalData") #get back to LocalData
		cprint("Done.")

	elif (modtype == "Forge"):
		os.chdir(execdir + "/LocalData")
		version = get_latest_version(mod_data)
		url = get_url(mod_data, version)
		cprint(modname + " is at version " + version)
		file_name = modname + "-" + version + ".jar"
		os.chdir(modfolder)
		cprint("Downloading " + url + " as " + file_name)
		with open(file_name, 'wb') as out_file:
			response = requests.get(url)
			out_file.write(response.content)
		cprint("Done.")

	elif (modtype == "Liteloader"):
		os.chdir(execdir + "/LocalData")
		version = get_latest_version(mod_data)
		url = get_url(mod_data, version)
		cprint(modname + " is at version " + version)
		file_name = modname + "-" + version + ".litemod"
		os.chdir(modfolder)
		cprint("Downloading " + url + " as " + file_name)
		with open(file_name, 'wb') as out_file:
			response = requests.get(url)
			out_file.write(response.content)
		cprint("Done.")

	elif (modtype == "Installer"):
		os.chdir(execdir + "/LocalData")
		version = get_latest_version(mod_data)
		url = get_url(mod_data, version)
		cprint(modname + " is at version " + version)
		file_name = mod_data.installer_name
		os.chdir(execdir)
		files = os.listdir(execdir)

		cprint("Downloading " + url + " as " + file_name)
		with open(file_name, 'wb') as out_file:
			response = requests.get(url)
			out_file.write(response.content)
		if(gui):
			msgbox.showinfo("Installer Downloaded", "The installer for "+modname+" has been downloaded.\nRun the installer, then click OK to continue.", parent=tkinst)
		cprint("Done. Please run the installer.")
		if (gui):
			tkinst.mlisti.insert(tk.END, modname)
	return 0

def install_deps(modname):
	deps = get_deps(modname)
	for dep in deps:
		if(not mod_installed(dep)):
			install_mod(dep)
