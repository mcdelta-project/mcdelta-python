import urllib.request, shutil, os, glob, shutil, tarfile, json


print("You are running " + os.name)
if (os.path.exists("Archive") == False):   //cleaning out Archive directory
  os.mkdir("Archive")
os.chdir("Archive/")
for file in glob.glob("*"):
  os.remove(file)

modname = input("Enter the mod that you wish to download.")

print("Downloading archive...")
url = "http://html.williambl.com/CMAN/CMAN.tar.gz" //Archive Download
file_name = "CMAN.tar.gz"

//Download the file from `url` and save it locally under `file_name`:
with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
  shutil.copyfileobj(response, out_file)
print("Extracting Archive...")

tar = tarfile.open("CMAN.tar.gz")     //untar
tar.extractall()
tarlist = tar.getnames()

print("Done.")

if(os.path.exists(modname + ".json")):              //Telling user that file exists
  for file in glob.glob(modname + ".json"):
      print(file)
else:
  print("Mod not found.")


pass //Add code to download file and move to mods directory
