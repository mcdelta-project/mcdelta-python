import pexpect
import sys

print("Running tests on " + sys.platform)
deltamc = pexpect.spawn("python3 ./deltamc.py", encoding="UTF-8")
deltamc.logfile = sys.stdout
deltamc.expect("> ")
deltamc.sendline("install MinecraftForge")
deltamc.expect("Done. Please run the installer.")
deltamc.expect("> ")
