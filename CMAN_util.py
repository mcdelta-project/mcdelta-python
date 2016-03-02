import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
import tkinter as tk

modfolder = "@ERROR@"
versionsfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"
tkinst = None

def init_config_util(data): #data is a 6-tuple
	global modfolder, versionsfolder, execdir, instance, gui, tkinst #makes it edit the global vars rather than create new ones
	modfolder, versionsfolder, execdir, instance, gui, tkinst = data
	
def cprint(text): #outputs text to console pane in GUI if gui enabled, otherwise prints it
	if (gui == True):
		tkinst.console.config(state = tk.NORMAL)
		tkinst.console.insert(tk.END, text+"\n")
		tkinst.console.config(state = tk.DISABLED)
	else:
		print(text)

def instance_exists(instance):
	with open(execdir+ "/LocalData/config.json") as json_file:
		try:
			json_data = json.load(json_file)
		except(json.decoder.JSONDecodeError):
			cprint("The config JSON appears to be invalid. Delete it and run CMAN again.")
			json_file.close()
			sys.exit()
	return(instance in json_data.keys())

def read_config(instance):
	if (os.path.exists("config.json")):
		with open("config.json") as json_file:
			try:
				json_data = json.load(json_file)
			except(json.decoder.JSONDecodeError):
				cprint("The config JSON appears to be invalid. Delete it and run CMAN again.")
				json_file.close()
				sys.exit()
			json_file.close()
		if(instance in json_data.keys()):
			try:
				modfolder = json_data[instance]["modfolder"] # If config exists, get modfolder and versions folder from that. Else, ask for it.
			except(KeyError): #modfolder data missing
				f = open("config.json", "w")
				json_data[instance]["modfolder"] = input("Enter mod folder location for instance "+instance+" (absolute path): ")
				json.dump(json_data, f)
				f.close()
			try:
				versionsfolder = json_data[instance]["versionsfolder"]
			except(KeyError): #versionsfolder data missing
				f = open("config.json", "w")
				son_data[instance]["versionsfolder"] = input("Enter versions folder location for instance "+instance+" (absolute path): ")
				json.dump(json_data, f)
				f.close()
		else:
			print("Config for instance "+instance+" is missing. Setting up config.")
			modfolder = input("Enter mod folder location for instance "+instance+" (absolute path): ")
			versionsfolder = input("Enter versions folder location for instance "+instance+" (absolute path): ")
			f = open("config.json", 'w')
			json_data[instance] = {"modfolder": modfolder, "versionsfolder": versionsfolder}
			json.dump(json_data, f)
			f.close()
	else:
		print("Config for instance "+instance+" is missing. Setting up config.")
		modfolder = input("Enter mod folder location for instance "+instance+" (absolute path): ")
		versionsfolder = input("Enter versions folder location for instance "+instance+" (absolute path): ")
		f = open("config.json", 'w')
		json_data = {instance: {"modfolder": modfolder, "versionsfolder": versionsfolder}}
		json.dump(json_data, f)
		f.close()
	return(modfolder, versionsfolder)

def new_config(instance):
		with open("config.json") as json_file: #can assume it exists and is valid, the program has loaded before this is called
			json_data = json.load(json_file)
			json_file.close()
		if(instance in json_data.keys()):
			cprint("Instance "+instance+" already exists, cannot add it.")
		else:
			modfolder = input("Enter mod folder location for instance "+instance+" (absolute path): ")
			versionsfolder = input("Enter versions folder location for instance "+instance+" (absolute path): ")
			f = open("config.json", 'w')
			json_data[instance] = {"modfolder": modfolder, "versionsfolder": versionsfolder}
			json.dump(json_data, f)
			f.close()
		cprint("Done.")
		return(modfolder, versionsfolder)

def rm_config(_instance):
	if instance == _instance:
		cprint("Cannot remove instance while it is active! Select another instance first.")
	else:
		with open("config.json") as json_file: #can assume it exists, the program has loaded before this is called
			try:
				json_data = json.load(json_file)
			except(json.decoder.JSONDecodeError):
				cprint("The config JSON appears to be invalid. Delete it and run CMAN again.")
				json_file.close()
				sys.exit()
			json_file.close()
		if(_instance in json_data.keys()):
			del json_data[_instance]
			with open("config.json", "w") as f:
				json.dump(json_data, f)
			cprint("Removed config data for instance "+_instance+".")
			if(os.path.exists(os.path.join("ModsDownloaded", _instance))):
				if(input("Delete installed mod listing for instance "+_instance+"? Type OK to delete, or anything else to skip: ") == "OK"):
					shutil.rmtree(os.path.join("ModsDownloaded", _instance))
					cprint("Deleted installed mod listing.")
				else:
					cprint("Skipped installed mod listing.")
	cprint("Done.")

def get_json(modname):
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		os.chdir(execdir + "/Data/CMAN-Archive")
	else:
		cprint("CMAN archive not found. Please update the CMAN archive.")
		return(-1)
	if(os.path.exists(modname + ".json")):
		# JSON parsing
		with open(modname + ".json") as json_file:
			try:
				json_data = json.load(json_file)
				json_file.close()
			except(json.decoder.JSONDecodeError):
				cprint("The JSON file \""+modname+".json\" appears to be invalid. Please update the CMAN archive.")
				json_file.close()
				return
		return(json_data)
	else:
		return(None)

def get_installed_json(modname):
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+instance)):
		os.chdir(execdir + "/LocalData/ModsDownloaded/"+instance)
	else:
		return(None) #no mods installed, so obviously modname isn't installed
	if(os.path.exists(modname + ".installed")):
		# JSON parsing
		with open(modname + ".installed") as json_file:
			try:
				json_data = json.load(json_file)
			except(json.decoder.JSONDecodeError):
				cprint("The JSON file \""+modname+".installed\" appears to be invalid. Using data from CMAN archive.")
				json_data = (get_json(modname))
			finally:
				json_file.close()
		return(json_data)
	else:
		return(None)

def mod_installed(modname):
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+instance)):
		os.chdir(execdir + "/LocalData/ModsDownloaded/"+instance)
	else:
		return(False) #no mods installed, so obviously modname isn't installed
	files = glob.glob(modname + ".installed")
	return(len(files)>0)

def get_all_insts():
	with open(execdir + "/LocalData/config.json") as json_file: #can assume it exists and is valid, the program has loaded before this is called
			json_data = json.load(json_file)
			json_file.close()
	insts = json_data.keys()
	return insts


def get_installed_jsons(inst = None):
	jsons = []
	if(inst == None):
		with open(execdir + "/LocalData/config.json") as json_file: #can assume it exists and is valid, the program has loaded before this is called
			json_data = json.load(json_file)
			json_file.close()
		insts = json_data.keys()
	else:
		insts = [inst]
	for inst in insts:
		if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+inst)):
			mods = os.listdir(execdir + "/LocalData/ModsDownloaded/"+inst)
			os.chdir(execdir + "/LocalData/ModsDownloaded/"+inst)
			for mod in mods:
				json_data = get_installed_json(mod[:-10]) #[:-10] cuts off the .installed extension
				jsons.append(json_data)
	return(jsons)


def get_all_jsons():
	jsons = []
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		mods = os.listdir(execdir + "/Data/CMAN-Archive")
		for mod in mods:
			json_data = get_json(mod[:-5]) #[:-5] cuts off the .json extension
			jsons.append(json_data)
	return(jsons)

def switch_path_dir(path, dir): #switches tkinst of path to dir given
	pathsplit = path.split(os.sep)
	pathsplit[0] = dir.split(os.sep)[-1] #just in case it ends with os.sep
	return(os.sep.join(pathsplit))

def listmods(output=True):
	modsinstalled = get_installed_jsons()
	if output:
		cprint("Installed mods:")
		cprint(str(modsinstalled))
	else:
		return modsinstalled

def listmods_all(output=True):
	mods = get_all_jsons()
	if output:
		cprint("Mods:")
		cprint(str(mods))
	else:
		return mods

def mergedirs(dir1, dir2):
	files1 = []
	files2 = []
	for tuple1 in os.walk(dir1):
		files1.append(tuple1[0])
		for file1 in tuple1[2]:
			files1.append(os.path.join(tuple1[0], file1))
	for file_ in files1: #file_ because file() is a builtin function
		if(os.path.split(file_)[0] == ''): #if file_ == dir1
			continue #skip it
		if(not os.path.exists(os.path.split(switch_path_dir(file_, dir2))[0])): #if parent dir does not exist in dir2 
			cprint(file_)
			os.makedirs(os.path.split(switch_path_dir(file_, dir2))[0]) #make parent dir in dir2
		if(os.path.isfile(file_)):
			shutil.copy(file_, switch_path_dir(file_, dir2))
		else: #if it is a dir, because it can only be either a file or a dir
			if(not os.path.exists(switch_path_dir(file_, dir2))):
				os.mkdir(switch_path_dir(file_, dir2))

def fix_names(path, oldname, name):
	old_cwd = os.getcwd() #to reset cwd afterwards
	os.chdir(path)
	os.rename(oldname+".jar", name+".jar")
	os.rename(oldname+".json", name+".json")
	with open(name+".json") as f:
		data = json.load(f)
		f.close()
	data["id"] = name
	with open(name+".json", "w") as f:
		json.dump(data, f)
		f.close()
	os.chdir(old_cwd) #restoring cwd

def display_versions(versions): #just makes the version list into a nicer string for printing (minus the brackets and quotes)
	versionstr = ""
	for version in versions:
		versionstr = versionstr + version +", "
	return(versionstr[:-2]) #cuts off the extra ", " at the end

def get_deps(modname):
	json_data = get_json(modname)
	deps = json_data["Requirements"]
	return(deps)
