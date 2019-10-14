import pexpect
import sys
import os

print("Running tests on " + sys.platform)
print(os.getcwd())
mcdelta = pexpect.spawn("python3 ./src/mcdelta.py", encoding="UTF-8")
mcdelta.logfile = sys.stdout
print("\n *** Attempting to set up the default instance... *** \n")
mcdelta.expect(
    "Enter mod folder location for instance default \(absolute path\)\: ")
mcdelta.sendline(".")
mcdelta.expect(
    "Enter jar folder location for instance default \(absolute path\)\:")
mcdelta.sendline(".")
mcdelta.expect("Enter Minecraft version for instance default:")
mcdelta.sendline("1.12")
print("\n *** Attempting to get info about MinecraftForge... ***\n")
mcdelta.expect("> ")
mcdelta.sendline("info MinecraftForge")
print("\n *** Info test passed! *** \n")
print("\n *** Attempting to install MinecraftForge... ***\n")
mcdelta.expect("> ")
mcdelta.sendline("install MinecraftForge")
mcdelta.expect("Done. Please run the installer.")
mcdelta.expect("> ")
print("\n *** Installation test passed! *** \n")
print("\n *** Attempting to remove MinecraftForge *** \n")
mcdelta.sendline("remove MinecraftForge")
mcdelta.sendline("Y")
mcdelta.expect("> ")
print("\n *** Removal test passed! *** \n")
print("\n *** Test passed! *** \n")
