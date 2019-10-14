import requests
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialogs
import tkinter.filedialog as filedialogs
import textwrap
from modclass import Mod

modfolder = "@ERROR@"
jarfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"
tkinst = None
gui = False
tk_ready = False

mod_list = []

version = "2.1.0"


def read_default_instance():
    old_cwd = os.getcwd()  # to reset cwd afterward
    # at this point in startup, old_cwd is execdir
    os.chdir(os.path.join(execdir, "LocalData"))
    try:
        with open("default_instance.txt") as f:
            default = f.read().strip()  # don't want leading trailing whitespace/newlines
    except(FileNotFoundError):
        default = "default"
        with open("default_instance.txt", "w") as f:
            f.write(default)

    os.chdir(old_cwd)  # restoring cwd
    return default


def check_for_updates():
    response = requests.get(
        'https://raw.githubusercontent.com/deltamc-project/deltamc-python/master/version.txt')
    latestversion = response.text
    if (str(version).strip() != str(latestversion).strip()):
        # if (gui):
        #	msgbox.askyesno("Update available", "You are running DeltaMC " + version + ".\nThe newest version is " + str(latestversion) + ".", parent=tkinst, master=tkinst)
        # else:
        cprint("!!Update Available! You are running DeltaMC " + version +
               ". The newest version is " + str(latestversion) + "!!")


def init_config_util(data):  # data is a 5-tuple
    # makes it edit the global vars rather than create new ones
    global modfolder, jarfolder, mc_version, execdir, instance, gui
    modfolder, jarfolder, mc_version, execdir, instance, gui = data


def init_config_util_guionly(data):
    global gui  # makes it edit the global var
    gui = data
    tk_ready = False


def recieve_tkinst_util(data):
    global tkinst, tk_ready
    tkinst = data
    tk_ready = True


def cprint(text, terminator="\n"):  # outputs text to console pane in GUI if gui enabled, otherwise prints it
    if (gui == True and tk_ready == True):
        tkinst.console.config(state=tk.NORMAL)
        tkinst.console.insert(tk.END, str(text)+terminator)
        tkinst.console.config(state=tk.DISABLED)
        tkinst.console.see(tk.END)
    else:
        print(text, end=terminator)


def iprint(text):  # outputs text to info pane in GUI if gui enabled, otherwise prints it
    if (gui == True):
        tkinst.info.config(state=tk.NORMAL)
        tkinst.info.delete("1.0", tk.END)
        tkinst.info.insert(tk.END, str(text))
        tkinst.info.config(state=tk.DISABLED)
    else:
        cprint(text)


def instance_exists(instance):
    with open(execdir + "/LocalData/config.json") as json_file:
        try:
            json_data = json.load(json_file)
        except(json.decoder.JSONDecodeError):
            cprint(
                "The config JSON appears to be invalid. Delete it and run DeltaMC again.")
            json_file.close()
            sys.exit()
    return(instance in json_data.keys())


def read_config(instance):
    if (os.path.exists("config.json")):
        with open("config.json") as json_file:
            try:
                json_data = json.load(json_file)
            except(json.decoder.JSONDecodeError):
                cprint(
                    "The config JSON appears to be invalid. Delete it and run DeltaMC again.")
                json_file.close()
                sys.exit()
            json_file.close()
        if(instance in json_data.keys()):
            try:
                # If config exists, get modfolder and versions folder from that. Else, ask for it.
                modfolder = json_data[instance]["modfolder"]
            except(KeyError):  # modfolder data missing
                f = open("config.json", "w")
                json_data[instance]["modfolder"] = cinput(
                    "Enter mod folder location for instance "+instance+" (absolute path): ", "Mod folder for "+instance, 'path')
                json.dump(json_data, f)
                f.close()
            try:
                jarfolder = json_data[instance]["jarfolder"]
            except(KeyError):  # jarfolder data missing
                f = open("config.json", "w")
                json_data[instance]["jarfolder"] = cinput(
                    "Enter jar folder location for instance "+instance+" (absolute path): ", "Jar folder for "+instance, 'path')
                json.dump(json_data, f)
                f.close()
            try:
                mc_version = json_data[instance]["mc_version"]
            except(KeyError):  # mc version data missing
                f = open("config.json", "w")
                json_data[instance]["mc_version"] = cinput(
                    "Enter Minecraft version for instance "+instance+": ", "Minecraft Version:")
                json.dump(json_data, f)
                f.close()
        else:
            cprint("Config for instance "+instance +
                   " is missing. Setting up config.")
            modfolder = cinput("Enter mod folder location for instance " +
                               instance+" (absolute path): ", "Mod folder for "+instance, 'path')
            jarfolder = cinput("Enter jar folder location for instance " +
                               instance+" (absolute path): ", "Jar folder for "+instance, 'path')
            mc_version = cinput(
                "Enter Minecraft version for instance "+instance+": ", "Minecraft Version:")
            f = open("config.json", 'w')
            json_data[instance] = {"modfolder": modfolder,
                                   "jarfolder": jarfolder, "mc_version": mc_version}
            json.dump(json_data, f)
            f.close()
    else:
        cprint("Config for instance "+instance +
               " is missing. Setting up config.")
        modfolder = cinput("Enter mod folder location for instance " +
                           instance+" (absolute path): ", "Mod folder for "+instance, 'path')
        jarfolder = cinput("Enter jar folder location for instance " +
                           instance+" (absolute path): ", "Jar folder for "+instance, 'path')
        mc_version = cinput(
            "Enter Minecraft version for instance "+instance+": ", "Minecraft Version")
        f = open("config.json", 'w')
        json_data = {instance: {"modfolder": modfolder,
                                "jarfolder": jarfolder, "mc_version": mc_version}}
        json.dump(json_data, f)
        f.close()
    return(modfolder, jarfolder, mc_version)


def new_config(instance):
    # can assume it exists and is valid, the program has loaded before this is called
    with open(execdir+"/LocalData/config.json") as json_file:
        json_data = json.load(json_file)
        json_file.close()
    if(instance in json_data.keys()):
        cprint("Instance "+instance+" already exists, cannot add it.")
    else:
        modfolder = cinput("Enter mod folder location for instance " +
                           instance+" (absolute path): ", "Mod folder for "+instance, 'path')
        if(modfolder == None):
            return (-1, -1)
        jarfolder = cinput("Enter jar folder location for instance " +
                           instance+" (absolute path): ", "Jar folder for "+instance, 'path')
        if(jarfolder == None):
            return (-1, -1)
        mc_version = cinput(
            "Enter Minecraft version for instance "+instance+": ", "Minecraft Version")
    f = open(execdir+"/LocalData/config.json", 'w')
    json_data[instance] = {"modfolder": modfolder,
                           "jarfolder": jarfolder, "mc_version": mc_version}
    json.dump(json_data, f)
    f.close()
    cprint("Done.")
    return(modfolder, jarfolder)


def rm_config(_instance):
    if instance == _instance:
        cprint(
            "Cannot remove instance while it is active! Select another instance first.")
    else:
        # can assume it exists, the program has loaded before this is called
        with open(execdir+"/LocalData/config.json") as json_file:
            try:
                json_data = json.load(json_file)
            except(json.decoder.JSONDecodeError):
                cprint(
                    "The config JSON appears to be invalid. Delete it and run DeltaMC again.")
                json_file.close()
                sys.exit()
            json_file.close()
        if(_instance in json_data.keys()):
            del json_data[_instance]
            with open(execdir+"/LocalData/config.json", "w") as f:
                json.dump(json_data, f)
            cprint("Removed config data for instance "+_instance+".")
            if(os.path.exists(os.path.join("ModsDownloaded", _instance))):
                a = cinput("Delete installed mod listing for instance "+_instance+"? Type OK to delete, or anything else to skip: ",
                           "Delete installed mod listing for instance "+_instance+"?", 'bool') in ["OK", True]
                if(a):
                    shutil.rmtree(os.path.join("ModsDownloaded", _instance))
                    cprint("Deleted installed mod listing.")
                else:
                    cprint("Skipped installed mod listing.")
    cprint("Done.")


def get_json(modname):
    if(os.path.exists(execdir + "/Data/DeltaMC-Archive")):
        os.chdir(execdir + "/Data/DeltaMC-Archive")
    else:
        cprint("DeltaMC archive not found. Please update the DeltaMC archive.")
        return(-1)
    if(os.path.exists(modname + ".json")):
        # JSON parsing
        with open(modname + ".json") as json_file:
            try:
                json_data = json.load(json_file)
                json_file.close()
            except(json.decoder.JSONDecodeError):
                cprint("The JSON file \""+modname +
                       ".json\" appears to be invalid. Please update the DeltaMC archive.")
                json_file.close()
                return
        return(json_data)
    else:
        curse = get_mod_from_curse(modname)
        if curse != None:
            return(curse)
        else:
            return(None)


def get_installed_json(modname):
    if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+instance)):
        os.chdir(execdir + "/LocalData/ModsDownloaded/"+instance)
    else:
        return(None)  # no mods installed, so obviously modname isn't installed
    if(os.path.exists(modname + ".installed")):
        # JSON parsing
        with open(modname + ".installed") as json_file:
            try:
                json_data = json.load(json_file)
            except(json.decoder.JSONDecodeError):
                cprint("The JSON file \""+modname +
                       ".installed\" appears to be invalid. Using data from DeltaMC archive.")
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
        return(False)  # no mods installed, so obviously modname isn't installed
    files = glob.glob(modname + ".installed")
    return(len(files) > 0)


def get_all_insts():
    # can assume it exists and is valid, the program has loaded before this is called
    with open(execdir + "/LocalData/config.json") as json_file:
        json_data = json.load(json_file)
        json_file.close()
    insts = json_data.keys()
    return insts


def get_installed_jsons(inst=None, allinst=True):
    jsons = []
    if(inst == None and allinst):
        # can assume it exists and is valid, the program has loaded before this is called
        with open(execdir + "/LocalData/config.json") as json_file:
            json_data = json.load(json_file)
            json_file.close()
        insts = json_data.keys()
    elif(inst == None and not allinst):
        insts = [instance]
    else:
        insts = [inst]
    for inst in insts:
        if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+inst)):
            mods = os.listdir(execdir + "/LocalData/ModsDownloaded/"+inst)
            os.chdir(execdir + "/LocalData/ModsDownloaded/"+inst)
            for mod in mods:
                # [:-10] cuts off the .installed extension
                json_data = get_installed_json(mod[:-10])
                jsons.append(json_data)
    return(jsons)


def get_installed_mods(inst=None, allinst=True):
    mods = []
    if(inst == None and allinst):
        # can assume it exists and is valid, the program has loaded before this is called
        with open(execdir + "/LocalData/config.json") as json_file:
            json_data = json.load(json_file)
            json_file.close()
        insts = json_data.keys()
    elif(inst == None and not allinst):
        insts = [instance]
    else:
        insts = [inst]
    for inst in insts:
        if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+inst)):
            _mods = os.listdir(execdir + "/LocalData/ModsDownloaded/"+inst)
            os.chdir(execdir + "/LocalData/ModsDownloaded/"+inst)
            for _mod in _mods:
                if _mod == '.DS_Store':
                    continue
                # [:-10] cuts off the .installed extension
                json_data = get_installed_json(_mod[:-10])
                mods.append(get_mod_from_json(json_data))
    return(mods)


def get_all_jsons():
    jsons = []
    if(os.path.exists(execdir + "/Data/DeltaMC-Archive")):
        mods = os.listdir(execdir + "/Data/DeltaMC-Archive")
        for mod in mods:
            if mod == "README.md":
                continue
            # [:-5] cuts off the .json extension
            json_data = get_json(mod[:-5])
            if json_data != None:
                jsons.append(json_data)
    return(jsons)


def switch_path_dir(path, dir):  # switches tkinst of path to dir given
    pathsplit = path.split(os.sep)
    pathsplit[0] = dir.split(os.sep)[-1]  # just in case it ends with os.sep
    return(os.sep.join(pathsplit))


def listmods(allinst=True):
    modsinstalled = listmods_no_output(allinst=allinst)
    cprint("Installed mods:")
    cprint(str(modsinstalled))


def listmods_no_output(allinst=True):
    return get_installed_jsons(inst=None, allinst=allinst)


def listmods_all():
    mods = listmods_all_no_output()
    cprint("Mods:")
    cprint(str(mods))


def listmods_all_no_output():
    return get_all_jsons()


def mergedirs(dir1, dir2):
    files1 = []
    files2 = []
    for tuple1 in os.walk(dir1):
        files1.append(tuple1[0])
        for file1 in tuple1[2]:
            files1.append(os.path.join(tuple1[0], file1))
    for file_ in files1:  # file_ because file() is a builtin function
        if(os.path.split(file_)[0] == ''):  # if file_ == dir1
            continue  # skip it
        # if parent dir does not exist in dir2
        if(not os.path.exists(os.path.split(switch_path_dir(file_, dir2))[0])):
            cprint(file_)
            os.makedirs(os.path.split(switch_path_dir(file_, dir2))
                        [0])  # make parent dir in dir2
        if(os.path.isfile(file_)):
            shutil.copy(file_, switch_path_dir(file_, dir2))
        else:  # if it is a dir, because it can only be either a file or a dir
            if(not os.path.exists(switch_path_dir(file_, dir2))):
                os.mkdir(switch_path_dir(file_, dir2))


def fix_names(path, oldname, name):
    old_cwd = os.getcwd()  # to reset cwd afterwards
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
    os.chdir(old_cwd)  # restoring cwd


# just makes the version list into a nicer string for printing (minus the brackets and quotes)
def display_versions(versions):
    versionstr = ""
    for version in versions:
        versionstr = versionstr + version + ", "
    return(versionstr[:-2])  # cuts off the extra ", " at the end


def get_deps(modname):
    mod = get_mod(modname)
    return(mod.requirements)


def update_archive(start=False):
    # Delete old archive
    os.chdir(execdir + "/Data")
    if(os.path.exists(execdir + "/Data/DeltaMC-Archive")):
        shutil.rmtree("DeltaMC-Archive")
    # Archive Download
    url = "https://github.com/deltamc-project/deltamc-archive/tarball/master"
    # curse_url = "https://addons-ecs.forgesvc.net/api/v2/addon/search?&gameId=432" #this is from the Twitch/Curse API, it gets all mods on CurseForge at once
    file_name = "DeltaMC.tar.gz"
    #curse_file_name = "cursemods.json"
    cprint("Updating archive...", "")
    # Download it.
    try:
        with open(file_name, 'wb') as out_file:
            response = requests.get(
                'https://github.com/deltamc-project/deltamc-archive/tarball/new-syntax')
            out_file.write(response.content)
        cprint("downloaded...", "")
    except Exception as e:
        cprint("Something went wrong while downloading the archive.")
        cprint("Error: " + str(e))
        if(gui and not start):
            msgbox.showerror("Archive download failed",
                             "Something went wrong while downloading the archive.", parent=tkinst)
        if(start):
            print("DeltaMC: fatal: Something went wrong while downloading the archive.")
            sys.exit()
        else:
            return -1
    # Download it.
    tar = tarfile.open("DeltaMC.tar.gz")  # untar
    tar.extractall()
    tarlist = tar.getnames()
    # rename the resulting folder to DeltaMC-Archive
    os.rename(tarlist[0], "DeltaMC-Archive")
    for json_data in get_all_jsons():
        mod_item = get_mod_from_json(json_data)
        mod_list.append(mod_item)

    cprint("extracted")
    if(gui and not start):
        msgbox.showinfo(
            "Archive updated", "The DeltaMC archive has been successfully updated.", parent=tkinst)


def get_info_console(modname):
    istr = []
    ostr = ""
    if(modname == None):
        modname = cinput("Enter mod name: ")

    mod_data = get_mod_from_name(modname)
    if (mod_data != None):
        stable = "Unstable" if mod_data.unstable else "Stable"
        istr += [mod_data.name+":"+"\n\n"]
        istr += ["Latest Version: " +
                 get_latest_version(mod_data)+" ("+stable+")"+"\n\n"]
        istr += ["Author(s): "+mod_data.author+"\n\n"]
        istr += ["Description: "+mod_data.desc+"\n\n"]
        istr += ["Requirements: "+str(mod_data.requirements)+"\n\n"]
        istr += ["Known Incompatibilities: " +
                 str(mod_data.incompatibilities)+"\n\n"]
        istr += ["Download Link: "+get_url(mod_data, version)+"\n\n"]
        istr += ["License: "+mod_data.license]
    else:
        istr += "Mod "+modname+" not found."
    for _istr in istr:
        _istr = textwrap.fill(_istr, 46)
        ostr = ostr+_istr+"\n\n"
    #print(textwrap.fill(istr, 46).replace("  *", "\n\n"))
    return(ostr)


def get_info_console_output(modname):
    cprint(get_info_console(modname))


def get_info_no_output(modname):
    istr = ""
    if(modname == None):
        modname = cinput("Enter mod name: ")

    mod_data = get_mod_from_name(modname)
    if (mod_data != None):
        stable = "Unstable" if mod_data.unstable else "Stable"
        istr += mod_data.name+":"+"\n\n"
        istr += "Latest Version: " + \
            get_latest_version(mod_data)+" ("+stable+")"+"\n\n"
        istr += "Author(s): "+mod_data.author+"\n\n"
        istr += "Description: "+mod_data.desc+"\n\n"
        istr += "Requirements: "+str(mod_data.requirements)+"\n\n"
        istr += "Known Incompatibilities: " + \
            str(mod_data.incompatibilities)+"\n\n"
        istr += "Download Link: "+get_url(mod_data, version)+"\n\n"
        istr += "License: "+mod_data.license
    else:
        istr += "Mod "+modname+" not found."
    return(istr)


def get_info(modname):
    cprint(get_info_no_output(modname))


def print_help():
    cprint("Commands:")
    cprint(" install 'mod' 'version': install the mod 'mod', version 'version'. 'version' argument is optional")
    cprint(" installm: install multiple mods")
    cprint(" info 'mod': get info for the mod 'mod'")
    cprint(" remove 'mod': remove the mod 'mod'")
    cprint(" removem: remove multiple mods")
    cprint(" upgrade 'mod': upgrade the mod 'mod'")
    cprint(" upgradem: upgrade multiple mods")
    cprint(" upgradeall: upgrade all outdated mods for Minecraft instance 'inst', or use '*' to check all instances")
    cprint(" upgrades 'inst': list available mod upgrades for Minecraft instance 'inst', or use '*' to check all instances")
    cprint(" update: update the DeltaMC archive")
    cprint(" help: display this help message")
    cprint(" version: display the DeltaMC version number")
    cprint(" list: list installed mods")
    cprint(" export 'name': export a modlist with the name 'name' , which can be imported later")
    cprint(" import 'pathtomodlist': import the modlist 'pathtomodlist'")
    cprint(" inst 'inst': switches to Minecraft instance 'inst'")
    cprint(" defaultinst 'inst': sets default Minecraft instance to 'inst'")
    cprint(" addinst 'inst': adds the Minecraft instance 'inst'")
    cprint(" rminst 'inst': removes the Minecraft instance 'inst'")
    cprint(" insts: lists all Minecraft instances")
    cprint(" exit: exit DeltaMC")


def get_mod_from_json(json_data):
    if (json_data["Type"] == "Installer"):
        mod = Mod(json_data["Name"], json_data["Author"],
                  json_data["Desc"], json_data["License"], json_data["Requirements"],
                  json_data["Incompatibilities"], json_data["Recommended"], json_data["Type"],
                  json_data["Unstable"], json_data["Versions"], json_data["InstallerName"])
    else:
        mod = Mod(json_data["Name"], json_data["Author"],
                  json_data["Desc"], json_data["License"], json_data["Requirements"],
                  json_data["Incompatibilities"], json_data["Recommended"], json_data["Type"],
                  json_data["Unstable"], json_data["Versions"])
    return mod


def get_mod_from_json_curse(entry):
    authors = []
    for author in entry["authors"]:
        authors.append(author["name"])
    versions = []
    for version in entry["gameVersionLatestFiles"]:
        versiondict = {}
        versiondict["Version"] = version["projectFileId"]
        versiondict["MCVersion"] = [version["gameVersion"]]
        versiondict["Link"] = "https://www.curseforge.com/minecraft/mc-mods/" + \
            entry["slug"]+"/download/"+str(version["projectFileId"])
        versions.append(versiondict)
    mod = Mod(entry["slug"], ", ".join(authors),
              entry["summary"], "N/A", "N/A", "Forge", "N/A", versions)
    return mod


def get_json_from_curse(entry):
    authors = []
    for author in entry["authors"]:
        authors.append(author["name"])
    versions = []
    for version in entry["gameVersionLatestFiles"]:
        versiondict = {}
        versiondict["Version"] = str(version["projectFileId"])
        versiondict["MCVersion"] = [version["gameVersion"]]
        versiondict["Link"] = "https://www.curseforge.com/minecraft/mc-mods/" + \
            entry["slug"]+"/download/"+str(version["projectFileId"])
        versions.append(versiondict)
    mod = {"Name": entry["key"], "Author": ", ".join(authors), "Desc": entry["summary"], "License": "N/A", "Requirements": [
    ], "Incompatibilities": [], "Recommended": [], "Type": "Forge", "Unstable": "N/A", "Versions": versions}
    return mod


def get_mod_from_curse(modname):
    entry = json.loads(requests.get(
        "https://ddph1n5l22.execute-api.eu-central-1.amazonaws.com/dev/mod/"+modname).text)["result"]
    if entry == None:
        return(None)
    versions_data = json.loads(requests.get(
        "https://ddph1n5l22.execute-api.eu-central-1.amazonaws.com/dev/mod/"+modname+"/files").text)["result"]
    versions = []
    for version in versions_data:
        versiondict = {}
        versiondict["Version"] = str(version["id"])
        versiondict["MCVersion"] = version["minecraft_version"][0]
        versiondict["Link"] = version["download_url"]
        versions.append(versiondict)
    mod = {"Name": entry["key"], "Author": entry["owner"], "Desc": entry["description"], "License": "Not available for CurseForge mods",
           "Requirements": [], "Incompatibilities": [], "Recommended": [], "Type": "Forge", "Unstable": "N/A", "Versions": versions}
    return mod


def get_mod_from_name(modname):
    return get_mod_from_json(get_json(modname))


def get_url(mod, version):
    version_number = 0

    for x in range(len(mod.versions)):
        if (version == mod.versions[x]['Version']):
            version_number = x
            break
    link = mod.versions[x]['Link']
    return link


def get_latest_version(mod):
    return mod.versions[0]['Version']


def get_latest_compatible_version(mod):
    for mod_version in mod.versions:
        if (mc_version in mod_version['MCVersion']):
            return mod_version['Version']


def is_any_version_compatible(mod):
    for mod_version in mod.versions:
        if (mc_version in mod_version['MCVersion']):
            return True
    return False


def cinput(terminal_text, gui_text=None, input_type='text', title="DeltaMC"):
    if gui_text == None:
        gui_text = terminal_text
    if (gui):
        if (input_type == 'text'):
            return dialogs.askstring(parent=tkinst, prompt=gui_text, title=title)
        elif (input_type == 'path'):
            return filedialogs.askdirectory(parent=tkinst, title=gui_text)
        elif (input_type == 'boolean'):
            return dialogs.askyesno(parent=tkinst, prompt=gui_text, title=title)

    return input(terminal_text)
