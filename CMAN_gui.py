import urllib.request
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
from CMAN_util import *

modfolder = "@ERROR@"
versionsfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"
tkinst = None

def init_config_gui(data): #data is a 6-tuple
	global modfolder, versionsfolder, execdir, instance, gui, tkinst #makes it edit the global vars rather than create new ones
	modfolder, versionsfolder, execdir, instance, gui, tkinst = data



#Callbacks


def instmods():

	_mods = map(int, tkinst.mlist.curselection())
	for _mod in _mods:
		CMAN_install.install_mod(tkinst.mods[int(_mod)]["Name"])
		tkinst.mlisti.insert(tk.END, tkinst.mods[int(_mod)]["Name"])


def removmods():

	_mods = map(int, tkinst.mlisti.curselection())
	print(_mods)
	for _mod in _mods:
		CMAN_remove.remove_mod(tkinst.modsi[int(_mod)]["Name"])
	print(_mods)
	for _mod in _mods:
		print(_mod)
		tkinst.mlisti.delete(int(_mod), int(_mod))

def upgrmods():

	_mods = map(int, tkinst.mlisti.curselection())
	for _mod in _mods:
		CMAN_upgrade.upgrade_mod(tkinst.modsi[int(_mod)]["Name"])

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


class Gui(tk.Frame):
	def __init__(self, master = None):
		tk.Frame.__init__(self, master)
		self.initialise_window()
		self.pack()
	def update_modlist(self):
		self.mods = listmods_all(False)
		self.mlist.delete(0, tk.END)
		for mod in self.mods:
			#print(mod)
			if mod != None:
				self.mlist.insert(tk.END, mod["Name"])
	def initialise_window(self):
		self.master.title("CMAN v2.1.0")
		self.master.geometry("800x400")

		self.winv = tk.PanedWindow(self, orient=tk.VERTICAL, sashrelief=tk.RAISED, height=400, width=800)
		self.winv.pack()

		self.win = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, height=300, width=800)
		self.winv.add(self.win)

		self.winl = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, height=100, width=800)
		self.winv.add(self.winl)

		self.bpane = tk.Frame(self.winl, width = 200)
		self.winl.add(self.bpane)

		#self.winl.paneconfigure(self.bpane)

		self.cpane = tk.Frame(self.winl)
		self.winl.add(self.cpane)

		self.console = tk.Text(self.cpane, height = 4)
		self.console.config(state = tk.DISABLED)
		self.console.pack()

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

		self.instf = tk.Frame(self.lpane)
		self.instf.pack()

		self.ilabel = tk.Label(self.instf, text = "Instance:")
		self.ilabel.pack(side=tk.LEFT)

		self.ilist = tk.OptionMenu(self.instf, self.isel, *insts)
		self.ilist.pack(side=tk.RIGHT)

		self.addinst = tk.Button(self.lpane, text = "Add Instance...")
		self.addinst.pack()

		self.reminst = tk.Button(self.lpane, text = "Remove Instance...")
		self.reminst.pack()

		self.definst = tk.Button(self.lpane, text = "Set as Default Instance")
		self.definst.pack()

		self.update = tk.Button(self.lpane, text = "Update CMAN Archive", command=update_archive)
		self.update.pack(side = tk.BOTTOM)

		self.blankf = tk.Frame(self.lpane, height = 20)
		self.blankf.pack(side = tk.BOTTOM)

		self.explist = tk.Button(self.lpane, text = "Export Mod List...")
		self.explist.pack(side = tk.BOTTOM)

		self.implist = tk.Button(self.lpane, text = "Import Mod List...")
		self.implist.pack(side = tk.BOTTOM)

		self.mpane = tk.Frame(self.win)
		self.win.add(self.mpane)

		self.mods = listmods_all(False)
		self.mlist = tk.Listbox(self.mpane, selectmode=tk.MULTIPLE)
		self.mlist.bind("<<ListboxSelect>>", updateinfo)
		self.mlist.pack(fill = tk.BOTH, expand = 1)

		for mod in self.mods:
			#print(mod)
			if mod != None:
				self.mlist.insert(tk.END, mod["Name"])

		self.rpane = tk.Frame(self.win)
		self.win.add(self.rpane)

		self.modsi = listmods(False)
		self.mlisti = tk.Listbox(self.rpane, selectmode=tk.MULTIPLE)
		self.mlisti.bind("<<ListboxSelect>>", updateinfo)
		self.mlisti.pack(fill = tk.BOTH, expand = 1)

		for mod in self.modsi:
			#print(mod)
			if mod != None:
				self.mlisti.insert(tk.END, mod["Name"])


		self.infopane = tk.Frame(self.win)
		self.win.add(self.infopane)
		self.info = tk.Text(self.infopane, width = 250)
		self.info.insert(tk.END, "No mod selected.")
		self.info.config(state = tk.DISABLED)
		self.info.pack(fill = tk.BOTH, expand = 1)


