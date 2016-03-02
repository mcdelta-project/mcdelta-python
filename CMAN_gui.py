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

class Gui(tk.Frame):
	def __init__(self, master = None):
		tk.Frame.__init__(self, master)
		self.initialise_window()
		self.pack()
	def initialise_window(self):
		self.master.title("CMAN v2.1.0")
		self.master.geometry("300x300")

		self.title = tk.Label(self, text = "Welcome to CMAN!")
		self.title.pack()

		self.output = tk.Label(self, text = "None")
		self.output.pack(side = tk.BOTTOM)

		self.button = tk.Button(self, text = "List installed mods", command =listmods, bg = "blue")
		self.button.pack(pady=20, padx = 20)