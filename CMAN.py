import urllib.request, shutil, os, glob, json


print("You are running " + os.name)
if (os.path.exists("Data") == False):				#cleaning out Data directory
  os.mkdir("Data")
os.chdir("Data")
for file in glob.glob("*"):
  os.remove(file)

modname = input("Enter the mod that you wish to download.")

print("Downloading archive...")
url = "http://modlist.mcf.li/api/v3/1.8.json"		#JSON link
file_name = "CMAN.json"

													#Download it.
with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
  shutil.copyfileobj(response, out_file)
print("Done.")

with open("CMAN.json") as json_file:				#JSON parsing
    json_data = json.load(json_file)
    pass											#I need help getting the download link from the JSON...


pass 												#Add code to download file and move to mods directory
