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
	mods = []
	for _mod in _mods:
		CMAN_install.install_mod(tkinst.mods[int(_mod)]["Name"])
		tkinst.mlisti.insert(tk.END, tkinst.mods[int(_mod)]["Name"])


def removmods():

	_mods = map(int, tkinst.mlisti.curselection())
	mods = []
	for _mod in _mods:
		remove_mod(tkinst.mods[int(_mod)]["Name"])

def upgrmods():

	_mods = map(int, tkinst.mlisti.curselection())
	mods = []
	for _mod in _mods:
		upgrade_mod(tkinst.mods[int(_mod)]["Name"])

def runcmd():
	pass

class Gui(tk.Frame):
	def __init__(self, master = None):
		tk.Frame.__init__(self, master)
		self.initialise_window()
		self.pack()
	def initialise_window(self):
		self.master.title("CMAN v2.1.0")
		self.master.geometry("600x400")

		self.winv = tk.PanedWindow(self, orient=tk.VERTICAL, sashrelief=tk.RAISED, height=400, width=800)
		self.winv.pack()

		self.win = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, height=300, width=800)
		self.winv.add(self.win)

		self.winl = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, height=100, width=800)
		self.winv.add(self.winl)

		self.bpane = tk.Frame(self.winl)
		self.winl.add(self.bpane)

		self.cpane = tk.Frame(self.winl)
		self.winl.add(self.cpane)

		self.console = tk.Text(self.cpane, height = 4)
		self.console.config(state = tk.DISABLED)
		self.console.pack()

		self.ccpane = tk.Frame(self.cpane)
		self.ccpane.pack(side = tk.BOTTOM)

		self.run = tk.Button(self.ccpane, text = "Run")
		self.run.pack(side = tk.RIGHT)	
		self.cmdin = tk.Entry(self.ccpane, text = "", width = 750)
		self.cmdin.pack(side = tk.RIGHT)		

		self.instmod = tk.Button(self.bpane, text = "Install Mod", command=instmods)
		self.instmod.pack()

		self.rmod = tk.Button(self.bpane, text = "Remove Mod")
		self.rmod.pack()

		self.umod = tk.Button(self.bpane, text = "Upgrade Mod")
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

		self.update = tk.Button(self.lpane, text = "Update CMAN Archive")
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
		self.mlist.pack()

		for mod in self.mods:
			#print(mod)
			if mod != None:
				self.mlist.insert(tk.END, mod["Name"])

		self.rpane = tk.Frame(self.win)
		self.win.add(self.rpane)

		self.modsi = listmods(False)
		self.mlisti = tk.Listbox(self.rpane, selectmode=tk.MULTIPLE)
		self.mlisti.pack()

		for mod in self.modsi:
			#print(mod)
			if mod != None:
				self.mlisti.insert(tk.END, mod["Name"])


		self.infopane = tk.Frame(self.win)
		self.win.add(self.infopane)
		self.info = tk.Text(self.infopane)
		self.info.insert(tk.END, "No mod selected.")
		self.info.config(state = tk.DISABLED)
		self.info.pack()

