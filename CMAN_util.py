import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile

modfolder = "@ERROR@"
versionsfolder = "@ERROR@"
execdir = "@ERROR@"

def init_config_util(data): #data is a 3-tuple
	global modfolder, versionsfolder, execdir #makes it edit the global vars rather than create new ones
	modfolder, versionsfolder, execdir = data

def read_config():
	os.chdir("LocalData")
	if (os.path.exists("config.json") == True):
		with open("config.json") as json_file:
			try:
				json_data = json.load(json_file)
			except(json.decoder.JSONDecodeError):
				print("The config JSON appears to be invalid. Delete it and run CMAN again.")
				json_file.close()
				sys.exit()
			json_file.close()
		try:
			modfolder = json_data["modfolder"] # If config exists, get modfolder and versions folder from that. Else, ask for it.
		except(KeyError): #modfolder data missing
			f = open("config.json", "w")
			modfolder = input("Enter mod folder location (absolute path): ")
			f.write('{"modfolder":"' + modfolder + '","versionsfolder":"' + versionsfolder + '"}')
			f.close()
		try:
			versionsfolder = json_data["versionsfolder"]
		except(KeyError): #versionsfolder data missing
			f = open("config.json", "w")
			versionsfolder = input("Enter versions folder location (absolute path): ")
			f.write('{"modfolder":"' + modfolder + '","versionsfolder":"' + versionsfolder + '"}')
			f.close()
	else:
		modfolder = input("Enter mod folder location (absolute path): ")
		versionsfolder = input("Enter versions folder location (absolute path): ")
		f = open('config.json', 'w')
		f.write('{"modfolder":"' + modfolder + '","versionsfolder":"' + versionsfolder + '"}')
		f.close()
	return(modfolder, versionsfolder)

def get_json(modname):
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		os.chdir(execdir + "/Data/CMAN-Archive")
	else:
		print("CMAN archive not found. Please update the CMAN archive.")
		return(-1)
	if(os.path.exists(modname + ".json")):
		# JSON parsing
		with open(modname + ".json") as json_file:
			try:
				json_data = json.load(json_file)
				json_file.close()
			except(json.decoder.JSONDecodeError):
				print("The JSON file \""+modname+".json\" appears to be invalid. Please update the CMAN archive.")
				json_file.close()
				return
		return(json_data)
	else:
		return(None)

def get_installed_json(modname):
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded")):
		os.chdir(execdir + "/LocalData/ModsDownloaded")
	else:
		return(None) #no mods installed, so obviously modname isn't installed
	if(os.path.exists(modname + ".installed")):
		# JSON parsing
		with open(modname + ".installed") as json_file:
			try:
				json_data = json.load(json_file)
			except(json.decoder.JSONDecodeError):
				print("The JSON file \""+modname+".installed\" appears to be invalid. Using data from CMAN archive.")
				json_data = (get_json(modname))
			finally:
				json_file.close()
		return(json_data)
	else:
		return(None)

def mod_installed(modname):
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded")):
		os.chdir(execdir + "/LocalData/ModsDownloaded")
	else:
		return(False) #no mods installed, so obviously modname isn't installed
	files = glob.glob(modname + ".installed")
	return(len(files)>0)


def get_installed_jsons():
	jsons = []
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded")):
		mods = os.listdir(execdir + "/LocalData/ModsDownloaded")
		os.chdir(execdir + "/LocalData/ModsDownloaded")
		for mod in mods:
			json_data = get_installed_json(mod[:-10]) #[:-10] cuts off the .installed extension
			jsons.append(json_data)
		return jsons
	else:
		return([])

def switch_path_dir(path, dir): #switches root of path to dir given
	pathsplit = path.split(os.sep)
	pathsplit[0] = dir.split(os.sep)[-1] #just in case it ends with os.sep
	return(os.sep.join(pathsplit))

def listmods():
	modsinstalled = get_installed_jsons()
	print("Installed mods:")
	print(str(modsinstalled))

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
			print(file_)
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
