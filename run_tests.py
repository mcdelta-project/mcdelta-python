import pexpect
import sys

print("Running tests on " + sys.platform)
deltamc = pexpect.spawn("python3 ./deltamc.py", encoding="UTF-8")
deltamc.logfile = sys.stdout
print("\n *** Attempting to set up the default instance... *** \n")
deltamc.expect("Enter mod folder location for instance default \(absolute path\)\: ")
deltamc.sendline(".")
deltamc.expect("Enter jar folder location for instance default \(absolute path\)\:")
deltamc.sendline(".")
deltamc.expect("Enter Minecraft version for instance default:")
deltamc.sendline("1.12")
print("\n *** Attempting to install MinecraftForge... ***\n")
deltamc.expect("> ")
deltamc.sendline("install MinecraftForge")
deltamc.expect("Done. Please run the installer.")
deltamc.expect("> ")
print("\n *** Test passed! *** \n")
