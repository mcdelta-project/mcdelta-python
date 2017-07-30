import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
import argparse
import tkinter as tk
import CMAN_remove
import CMAN_upgrade
import CMAN_install
import CMAN_importexport
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialogs
import tkinter.filedialog as filedialogs
from CMAN_util import *

modfolder = "@ERROR@"
jarfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"
tkinst = None

def init_config_gui(data): #data is a 5-tuple
    global modfolder, jarfolder, mc_version, execdir, instance, gui #makes it edit the global vars rather than create new ones
    modfolder, jarfolder, mc_version, execdir, instance, gui = data

def recieve_tkinst_gui(data):
    global tkinst
    tkinst = data

def gui_setup_config(_instance):
    global modfolder, jarfolder, instance, gui
    os.chdir(os.path.join(execdir, "LocalData"))
    instance = _instance
    modfolder, jarfolder, mc_version = read_config(_instance) #gets config stuff
    os.chdir(execdir)
    init_config_util((modfolder, jarfolder, mc_version, execdir, instance, gui)) #transferring config data (and Tkinter instance) to all files
    CMAN_install.init_config_install((modfolder, jarfolder, mc_version, execdir, instance, gui))
    CMAN_remove.init_config_remove((modfolder, jarfolder, mc_version, execdir, instance, gui))
    CMAN_upgrade.init_config_upgrade((modfolder, jarfolder, mc_version, execdir, instance, gui))
    CMAN_importexport.init_config_importexport((modfolder, jarfolder, mc_version, execdir, instance, gui))
    init_config_gui((modfolder, jarfolder, mc_version, execdir, instance, gui))


#Callbacks


def instmods():

    _mods = map(int, tkinst.mlist.curselection())
    for _mod in _mods:
        CMAN_install.install_mod(tkinst.mods[int(_mod)]["Name"])
    updateinst()


def removmods():

    _mods = map(int, tkinst.mlisti.curselection())
    for _mod in _mods:
        CMAN_remove.remove_mod(tkinst.modsi[int(_mod)]["Name"])
    updateinst()

def upgrmods():

    _mods = map(int, tkinst.mlisti.curselection())
    for _mod in _mods:
        CMAN_upgrade.upgrade_mod(tkinst.modsi[int(_mod)]["Name"])
    updateinst()

def runcmd():
    cmd = tkinst.cmdin.get()
    cprint(">"+cmd)
    parsecmd(cmd)

def updateinfo(event):
    _mods = event.widget.curselection()
    if len(_mods) == 0:
        iprint("No mod selected.")
    elif len(_mods) == 1:
        _mod = _mods[0]
        if event.widget == tkinst.mlist:
            name = tkinst.mods[int(_mod)]["Name"]
        elif event.widget == tkinst.mlisti:
            name = tkinst.modsi[int(_mod)]["Name"]
        iprint(get_info_console(name, output=False))
    else:
        iprint("Multiple mods selected.")

def sdinst():
    name = tkinst.isel.get()
    if(name == read_default_instance()):
        msgbox.showerror("Instance already default","Instance "+name+" is already set as default.", parent=tkinst)
    else:
        with open(execdir+"/LocalData/default_instance.txt", "w") as f:
            f.write(name)
        msgbox.showinfo("Default instance set", "Set default instance as "+name+".", parent=tkinst)

def addinst():
    name = dialogs.askstring("Instance Name", "Enter name for new instance:", parent=tkinst)
    if(name == None):
        return -1
    if(instance_exists(name)):
        msgbox.showerror("Instance already exists","Instance "+name+" already exists.", parent=tkinst)
    else:
        new_config(name)
        tkinst.ilist["menu"].add_command(label = name, command = lambda n=name: tkinst.isel.set(n))
        msgbox.showinfo("Instance created", "Instance "+name+" created.", parent=tkinst)

def removinst():
    name = tkinst.isel.get()
    if(not instance_exists(name)):
        msgbox.showerror("Instance does not exist","Instance "+name+" does not exist. Cannot remove.", parent=tkinst)
    elif(instance == name):
        msgbox.showerror("Instance currently selected","Instance "+name+" is currently selected. Cannot remove.", parent=tkinst)
    else:
        rm_config(name)
        msgbox.showinfo("Instance removed", "Instance "+name+" removed.", parent=tkinst)

    tkinst.ilist["menu"].delete(0, tk.END)
    insts = list(get_all_insts())
    for inst in insts:
        tkinst.ilist["menu"].add_command(label=inst, command = lambda n=inst: tkinst.isel.set(n))

def updateinst():
    name = tkinst.isel.get()
    gui_setup_config(name)
    tkinst.ilabel.configure(text = "Current Instance: "+instance)
    tkinst.mlisti.delete(0, tk.END)
    tkinst.modsi = listmods(False, False)
    upgrades = CMAN_upgrade.get_upgrade_names(instance)
    for mod in tkinst.modsi:
        if mod != None:
            if mod in upgrades:
                tkinst.mlisti.insert(tk.END, "! "+mod["Name"])
            else:
                tkinst.mlisti.insert(tk.END, mod["Name"])


def importmlist():
    fname = filedialogs.askopenfilename(parent=tkinst)
    CMAN_importexport.import_mods(fname)

def exportmlist():
    fname = filedialogs.asksaveasfilename(parent=tkinst)
    CMAN_importexport.export_mods(fname)

def exit():
    sys.exit()

class Gui(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.initialise_window()
        self.pack(expand=True, fill=tk.BOTH)
    def update_modlist(self):
        self.mods = listmods_all(False)
        self.mlist.delete(0, tk.END)
        for mod in self.mods:
            #print(mod)
            if mod != None:
                self.mlist.insert(tk.END, mod["Name"])
    def initialise_window(self):
        self.master.title("CMAN v2.1.1.0")
        #self.master.geometry("800x400")

        self.winv = tk.PanedWindow(self, orient=tk.VERTICAL, sashrelief=tk.RAISED, height=400, width=800)
        self.winv.pack(expand=True, fill=tk.BOTH)

        self.win = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, height=300, width=800)
        self.winv.add(self.win)

        self.winl = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, height=100, width=800)
        self.winv.add(self.winl)

        self.bpane = tk.Frame(self.winl, width = 200)
        self.winl.add(self.bpane)

        #self.winl.paneconfigure(self.bpane)

        self.cpane = tk.Frame(self.winl)
        self.winl.add(self.cpane)

        self.consoles = tk.Scrollbar(self.cpane, orient=tk.VERTICAL)
        self.consoles.pack(side=tk.RIGHT, fill=tk.Y)
        self.console = tk.Text(self.cpane, height = 4, yscrollcommand=self.consoles.set)
        self.console.config(state = tk.DISABLED)
        self.console.pack(expand=True, fill=tk.BOTH)
        self.consoles.config(command=self.console.yview)

        self.ccpane = tk.Frame(self.cpane)
        self.ccpane.pack(side = tk.BOTTOM)

        self.run = tk.Button(self.ccpane, text = "Run", command=runcmd)
        self.run.pack(side = tk.RIGHT)
        self.cmdin = tk.Entry(self.ccpane, text = "", width = 150)
        self.cmdin.pack(side = tk.RIGHT)

        self.instmod = tk.Button(self.bpane, text = "Install Mods", command=instmods)
        self.instmod.pack()

        self.rmod = tk.Button(self.bpane, text = "Remove Mods", command=removmods)
        self.rmod.pack()

        self.umod = tk.Button(self.bpane, text = "Upgrade Mods", command=upgrmods)
        self.umod.pack()

        insts = list(get_all_insts())
        self.isel = tk.StringVar()
        self.isel.set(instance)

        self.lpane = tk.Frame(self.win)
        self.win.add(self.lpane)

        self.ilabel = tk.Label(self.lpane, text = "Current Instance: "+instance)
        self.ilabel.pack()

        self.instf = tk.Frame(self.lpane)
        self.instf.pack(expand=True)

        self._ilabel = tk.Label(self.instf, text = "Instance:")
        self._ilabel.pack(side=tk.LEFT)

        self.ilist = tk.OptionMenu(self.instf, self.isel, *insts)
        self.ilist.pack(side=tk.RIGHT)

        self.addinst = tk.Button(self.lpane, text = "Add Instance...", command=addinst)
        self.addinst.pack()

        self.reminst = tk.Button(self.lpane, text = "Remove Instance", command=removinst)
        self.reminst.pack()

        self.setinst = tk.Button(self.lpane, text = "Select Instance", command=updateinst)
        self.setinst.pack()

        self.definst = tk.Button(self.lpane, text = "Set as Default Instance", command=sdinst)
        self.definst.pack()

        self.update = tk.Button(self.lpane, text = "Update CMAN Archive", command=update_archive)
        self.update.pack(side = tk.BOTTOM)

        self.blankf = tk.Frame(self.lpane, height = 20)
        self.blankf.pack(side = tk.BOTTOM, expand=True)

        self.explist = tk.Button(self.lpane, text = "Export Mod List...", command=exportmlist)
        self.explist.pack(side = tk.BOTTOM)

        self.implist = tk.Button(self.lpane, text = "Import Mod List...", command=importmlist)
        self.implist.pack(side = tk.BOTTOM)

        self.exit = tk.Button(self.lpane, text = "Exit CMAN", command=exit)
        self.exit.pack(side = tk.BOTTOM)

        self.mpane = tk.Frame(self.win)
        self.win.add(self.mpane)

        self.mods = listmods_all(False)
        self.modslabel = tk.Label(self.mpane, text = "Available Mods: ")
        self.modslabel.pack()
        self.mlists = tk.Scrollbar(self.mpane, orient=tk.VERTICAL)
        self.mlists.pack(side=tk.RIGHT, fill=tk.Y)
        self.mlist = tk.Listbox(self.mpane, selectmode=tk.MULTIPLE, yscrollcommand=self.mlists.set)
        self.mlist.bind("<<ListboxSelect>>", updateinfo)
        self.mlist.pack(fill = tk.BOTH, expand = 1)
        self.mlists.config(command=self.mlist.yview)

        for mod in self.mods:
            #print(mod)
            if mod != None:
                self.mlist.insert(tk.END, mod["Name"])

        self.rpane = tk.Frame(self.win)
        self.win.add(self.rpane)

        self.modsi = listmods(False, False)
        self.imodslabel = tk.Label(self.rpane, text = "Installed Mods: ")
        self.imodslabel.pack()
        self.mlistsi = tk.Scrollbar(self.rpane, orient=tk.VERTICAL)
        self.mlistsi.pack(side=tk.RIGHT, fill=tk.Y)
        self.mlisti = tk.Listbox(self.rpane, selectmode=tk.MULTIPLE, yscrollcommand=self.mlistsi.set)
        self.mlisti.bind("<<ListboxSelect>>", updateinfo)
        self.mlisti.pack(fill = tk.BOTH, expand = 1)
        self.mlistsi.config(command=self.mlisti.yview)

        for mod in self.modsi:
            #print(mod)
            if mod != None:
                self.mlisti.insert(tk.END, mod["Name"])


        self.infopane = tk.Frame(self.win)
        self.win.add(self.infopane)
        self.infos = tk.Scrollbar(self.infopane, orient=tk.VERTICAL)
        self.infos.pack(side=tk.RIGHT, fill=tk.Y)
        self.info = tk.Text(self.infopane, width = 250, yscrollcommand=self.infos.set)
        self.info.insert(tk.END, "No mod selected.")
        self.info.config(state = tk.DISABLED)
        self.info.pack(fill = tk.BOTH, expand = True)
        self.infos.config(command=self.info.yview)


def parsecmd(command):
        if(command.split(" ")[0] == "update"):
            update_archive()
        elif(command.split(" ")[0] == "upgrades"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                inst = command.split(" ")[1]
                if(inst == "*"):
                    inst = None
                if (not instance_exists(inst) and inst != None):
                    cprint("Instance "+inst+" does not exist.")
                    return
                update_archive()
                CMAN_upgrade.check_upgrades(True, inst)
            elif(len(command.split(" ")) == 1):
                cprint("upgrades: not enough arguments")
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "upgrade"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                mod = command.split(" ")[1]
                update_archive()
                upgrades = CMAN_upgrade.get_upgrades()
                CMAN_upgrade.upgrade_mod(mod)
            elif(len(command.split(" ")) == 1):
                mod = None
                update_archive()
                upgrades = CMAN_upgrade.get_upgrades()
                CMAN_upgrade.upgrade_mod(mod)
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "upgradeall"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                inst = command.split(" ")[1]
                if(inst == "*"):
                    inst = None
                if (not instance_exists(inst) and inst != None):
                    cprint("Instance "+inst+" does not exist.")
                    return
            elif(len(command.split(" ")) == 1):
                cprint("upgradeall: not enough arguments")
            else:
                cprint("Invalid command syntax.")
            update_archive()
            updates = CMAN_upgrade.get_upgrades(inst)
            if(len(updates) == 0):
                cprint("No upgrades available.")
            else:
                for update in updates:
                    CMAN_upgrade.upgrade_mod(update[0]["Name"])
        elif(command.split(" ")[0] == "install"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                mod = command.split(" ")[1]
                update_archive()
                CMAN_install.install_mod(mod)
            elif(len(command.split(" ")) == 1):
                mod = None
                update_archive()
                CMAN_install.install_mod(mod)
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "remove"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                mod = command.split(" ")[1]
                CMAN_remove.remove_mod(mod)
            elif(len(command.split(" ")) == 1):
                mod = None
                CMAN_remove.remove_mod(mod)
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "info"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                mod = command.split(" ")[1]
                get_info(mod)
            elif(len(command.split(" ")) == 1):
                mod = None
                get_info(mod)
        elif(command.split(" ")[0] == "installm" or command.split(" ")[0] == "installmany"):
            if(len(command.split(" ")) >= 2):
                modslist = command.split(" ")[1:] #separate mod names with spaces
                update_archive()
                string = "Attempting to install: "
                for item in modslist:
                    string = string + item+", "
                cprint(string[:-2]+"...") #[:-2] to cut off the extra ", " after the last element
                for item in modslist:
                    CMAN_install.install_mod(item)
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "removem" or command.split(" ")[0] == "removemany"):
            if(len(command.split(" ")) >= 2):
                modslist = command.split(" ")[1:] #separate mod names with spaces
                update_archive()
                string = "Attempting to remove: "
                for item in modslist:
                    string = string + item+", "
                cprint(string[:-2]+"...") #[:-2] to cut off the extra ", " after the last element
                for item in modslist:
                    CMAN_remove.remove_mod(item)
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "upgradem" or command.split(" ")[0] == "upgrademany"):
            if(len(command.split(" ")) >= 2):
                modslist = command.split(" ")[1:] #separate mod names with spaces
                update_archive()
                string = "Attempting to upgrade: "
                for item in modslist:
                    string = string + item+", "
                cprint(string[:-2]+"...") #[:-2] to cut off the extra ", " after the last element
                for item in modslist:
                    CMAN_upgrade.upgrade_mod(item)
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "export"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                name = command.split(" ")[1]
                update_archive()
                CMAN_importexport.export_mods(name)
            elif(len(command.split(" ")) == 1):
                name = None
                update_archive()
                CMAN_importexport.export_mods(name)
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "import"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                path = command.split(" ")[1]
                update_archive()
                CMAN_importexport.import_mods(path)
            elif(len(command.split(" ")) == 1):
                path = None
                update_archive()
                CMAN_importexport.import_mods(path)
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "instance" or command.split(" ")[0] == "inst"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                name = command.split(" ")[1]
                if(instance_exists(name)):
                    if(name == instance):
                        cprint("Instance "+name+" already selected!")
                    else:
                        gui_setup_config(name)
                        cprint("Switched to instance "+name+".")
                else:
                    cprint("Instance "+name+" does not exist.")
            elif(len(command.split(" ")) == 1):
                cprint("instance: not enough arguments")
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "setdefaultinstance" or command.split(" ")[0] == "setdefaultinst"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                name = command.split(" ")[1]
                if(instance_exists(name)):
                    if(name == read_default_instance()):
                        cprint("Instance "+name+" already set as default!")
                    else:
                        with open("default_instance.txt", "w") as f:
                            f.write(name)
                        cprint("Set default instance as "+name+".")
                else:
                    cprint("Instance "+instance+" does not exist.")
            elif(len(command.split(" ")) == 1):
                cprint("setdefaultinstance: not enough arguments")
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "addinstance" or command.split(" ")[0] == "addinst"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                name = command.split(" ")[1]
                if(instance_exists(name)):
                    cprint("Instance "+name+" already exists.")
                else:
                    new_config(name)
            elif(len(command.split(" ")) == 1):
                cprint("addinstance: not enough arguments")
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "rminstance" or command.split(" ")[0] == "removeinstance" or command.split(" ")[0] == "rminst"):
            if(len(command.split(" ")) == 2 and command.split(" ")[1] != ""):
                name = command.split(" ")[1]
                if(instance_exists(name)):
                    rm_config(name)
                else:
                    cprint("Instance "+name+" does not exist.")
            elif(len(command.split(" ")) == 1):
                cprint("removeinstance: not enough arguments")
            else:
                cprint("Invalid command syntax.")
        elif(command.split(" ")[0] == "instances" or command.split(" ")[0] == "insts"):
            with open("config.json") as json_file:
                json_data = json.load(json_file)
                insts = json_data.keys()
                cprint("Instances:")
                for inst in insts:
                    if(inst == instance):
                        cprint(inst+" (selected)")
                    else:
                        cprint(inst)
        elif(command.split(" ")[0] == "list"):
            listmods()
        elif(command.split(" ")[0] == "version"):
            cprint("CMAN v"+version)
        elif(command.split(" ")[0] == "help" or command.split(" ")[0] == "?"):
            print_help()
        elif(command.split(" ")[0] == "exit"):
            sys.exit()
        elif(command == ""):
            pass #don't print "Unknown command." for empty line
        else:
            cprint("Unknown command.")
