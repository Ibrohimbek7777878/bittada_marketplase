import subprocess
import os

try:
    print("Checking git log for base.py...")
    output = subprocess.check_output(["git", "log", "-n", "2", "--pretty=format:%H", "config/settings/base.py"])
    hashes = output.decode("utf-8").strip().split()
    print("Hashes:", hashes)
    if len(hashes) > 1:
        prev_hash = hashes[1]
        print(f"Restoring from {prev_hash}...")
        content = subprocess.check_output(["git", "show", f"{prev_hash}:config/settings/base.py"])
        with open("config/settings/base.py.restored", "wb") as f:
            f.write(content)
        print("Restored successfully to base.py.restored")
    else:
        print("Only one commit found for base.py or none.")
except Exception as e:
    print("Error:", e)
