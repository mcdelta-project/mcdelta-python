import urllib.request
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile

version = "0.0.1"

def get_json(modname):
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		os.chdir(execdir + "/Data/CMAN-Archive")
	else:
		print("CMAN archive not found. Please update archive.")
		return(-1)
	if(os.path.exists(modname + ".json")):
		# JSON parsing
		with open(modname + ".json") as json_file:
			json_data = json.load(json_file)
			json_file.close()
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
			json_data = json.load(json_file)
			json_file.close()
			return(json_data)
	else:
		return(None)

def mod_installed(modname):
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded")):
		os.chdir(execdir + "/LocalData/ModsDownloaded")
	else:
		return(False) #no mods installed, so obviously modname isn't installed
	files = glob.glob(modname + "-*.installed")
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

def update_archive():
	return
	#Delete old archive
	os.chdir(execdir + "/Data")
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		shutil.rmtree("CMAN-Archive")
	# Archive Download
	url = "https://github.com/Comprehensive-Minecraft-Archive-Network/CMAN-Archive/tarball/master/Archive.tar.gz"
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
	os.rename(tarlist[0], "CMAN-Archive") #remane the resulting folder to CMAN-Archive
	print("Done.")


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


def install_mod(modname):
	os.chdir(execdir + "/Data/CMAN-Archive")
	if(modname == None):
		modname = input("Enter mod name: ")

	if(os.path.exists(modname + ".json")):  # Telling user that file exists
		for file in glob.glob(modname + ".json"):
			print(file + " found.")
	else:
		print("Mod not found.")
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
			return
	incompatibilities = json_data["Incompatibilities"]
	for incompatibility in incompatibilities:
		if (os.path.exists(incompatibility + ".installed") == True):
			print("You cannot have " + incompatibility + " and " + modname + " installed at the same time!")
			return
	if (modtype == "Basemod"):
		os.chdir(execdir + "/LocalData/temp")
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
		os.chdir("..") #get back do LocalData
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


def remove_mod(modname): #behavior not guaranteed on mods installed outside of CMAN
	if(modname == None):
		modname = input("Enter mod name: ")
	print("Removing file for mod in ModsDownloaded")
	try:
		os.remove(execdir + "/LocalData/ModsDownloaded/"+modname+".installed") #removing json in ModsDownloaded dir
	except FileNotFoundError:
		print("Either " + modname + " is not installed, or something went horribly wrong.")
		return
	if(get_json(modname)["Type"] == "Forge" or get_json(modname)["Type"] == "Liteloader"):
		os.chdir(modfolder)
		files = glob.glob(modname + "-*.jar") #get all versions of mod
		for file in files:
			if(input("Delete \""+file+"\"? Type OK to delete, or anything else to skip: ") == "OK"):
				os.remove(file)
				print("Deleted \""+file+"\".")
			else:
				print("Skipped \""+file+"\".")
	else:
		print("I cannot remove installer mods or basemods! (If your mod is not an installermod or basemod, then something went horribly wrong.)")


def upgrade_mod(modname):
	os.chdir(execdir + "/Data/CMAN-Archive")
	if(modname == None):
		modname = input("Enter mod name: ")
	update = [get_installed_json(modname),get_json(modname)]
	if(os.path.exists(modname + ".installed")):  # Telling user that file exists
		for file in glob.glob(modname + ".installed"):
			print(file + " found.")
	else:
		print("Mod not found.")
		return
	os.chdir(execdir + "/LocalData") #restoring current working dir
	if(update[1]["Version"] != update[0]["Version"] and mod_installed(modname)):
		remove_mod(modname)
		install_mod(modname)
	elif(not mod_installed(modname)):
		print(modname+" is not installed.")
	else:
		print(modname+" is already up to date.")



def get_deps(modname):
	json_data = get_json(modname)
	deps = json_data["Requirements"]
	return(deps)

def install_deps(modname):
	deps = get_deps(modname)
	for dep in deps:
		if(not mod_installed(dep)):
			install_mod(dep)

def get_info(modname):
	if(modname == None):
		modname = input("Enter mod name: ")

	json_data = get_json(modname)
	if(json_data == -1):
		return
	else:
		if (json_data != None):
			if(json_data["Unstable"] == "false"):
				stable = "Stable" 
			else:
				stable = "Unstable" 
			print(json_data["Name"]+":")
			print("\tVersion: "+json_data["Version"]+" ("+stable+")")
			print("\tAuthor(s): "+json_data["Author"])
			print("\tDescription: "+json_data["Desc"])
			print("\tRequirements: "+str(json_data["Requirements"]))
			print("\tKnown Incompatibilities: "+str(json_data["Incompatibilities"]))
			print("\tDownload Link: "+str(json_data["Link"]))
			print("\tLicense: "+json_data["License"])
		else:
			print("Mod not found.")


# Start Program Here:
print("You are running " + sys.platform)
#not making Data dir here because it is done later
if (os.path.exists("LocalData") == False):
	os.mkdir("LocalData")
if (os.path.exists("LocalData/ModsDownloaded") == False):
	os.mkdir("LocalData/ModsDownloaded")
if (os.path.exists("LocalData/temp") == False):
	os.mkdir("LocalData/temp")
execdir = os.getcwd()
'''try:
	shutil.rmtree("Data") #deleting Data dir
except(FileNotFoundError): #Data dir not present
	pass
os.mkdir("Data") #creating new Data dir'''



os.chdir("LocalData")
if (os.path.exists("config.json") == True):
	with open("config.json") as json_file:
		try:
			json_data = json.load(json_file)
		except(KeyError):#json.decoder.JSONDecodeError):
			print("The config JSON appears to be invalid. Delete it and run CMAN again.")
			json_file.close()
			sys.exit()
		json_file.close()
	modfolder = "@#ERROR#@" #starting values
	versionsfolder = "@#ERROR#@"
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


def print_help():
	print("Commands:")
	print(" install 'mod': install the mod 'mod'")
	print(" info 'mod': get info for the mod 'mod'")
	print(" remove 'mod': remove the mod 'mod'")
	print(" upgrade 'mod': upgrade the mod 'mod'")
	print(" upgradeall: upgrade all outdated mods")
	print(" upgrades: list available mod upgrades")
	print(" update: update the CMAN archive")
	print(" help: display this help message")
	print(" version: display the CMAN version number")
	print(" exit: exit CMAN")

def get_upgrades(): #returns a list of 2-element lists of jsons (in which index 0 is the version you have and index 1 is the newest version)
	updates = []
	mods = get_installed_jsons()
	for mod in mods:
		if(mod != None):
			json_data = get_json(mod["Name"])
			if(json_data["Version"] != mod["Version"]):
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


update_archive()
print("CMAN v"+version)
print_help()
upgradesavailible = get_upgrades()
if (upgradesavailible == []):
	pass
else:
	print("The following upgrades are availible:")
	for upgrade in upgradesavailible:
		print(" "+upgrade[0]["Name"]+" (current version: "+upgrade[1]["Version"]+", you have: "+upgrade[0]["Version"]+")")
while(True):
	os.chdir(execdir + "/LocalData/") #reset current working dir
	command = input("> ")
	if(command.split(" ")[0] == "update"):
		update_archive()
	elif(command.split(" ")[0] == "upgrades"):
		update_archive()
		check_upgrades(True)
	elif(command.split(" ")[0] == "upgrade"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			update_archive()
			upgrades = get_upgrades()
			update_mod(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			update_archive()
			upgrades = get_upgrades()
			upgrade_mod(mod)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "upgradeall"):
		update_archive()
		updates = get_upgrades()
		if(len(updates) == 0):
			print("All mods up to date.")
		else:
			for update in updates:
				update_mod(update[0]["Name"])
	elif(command.split(" ")[0] == "install"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			update_archive()
			install_mod(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			update_archive()
			install_mod(mod)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "remove"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			remove_mod(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			remove_mod(mod)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "info"):
		if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
			mod = command.split(" ")[1]
			get_info(mod)
		elif(len(command.split(" ")) == 1):
			mod = None
			get_info(mod)
		else:
			print("Invalid command syntax.")
	elif(command.split(" ")[0] == "version"):
		print("CMAN v"+version)
	elif(command.split(" ")[0] == "help" or command.split(" ")[0] == "?"):
		print_help()
	elif(command.split(" ")[0] == "exit"):
		sys.exit()
	elif(command == ""):
		pass #don't print "Unknown command." for empty line
	else:
		print("Unknown command.")
