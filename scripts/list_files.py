
import os
print(f"CWD: {os.getcwd()}")
print("Files:")
for f in os.listdir("."):
    print(f" - {f}")
