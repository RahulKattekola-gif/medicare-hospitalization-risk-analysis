import os
import shutil

DATA_DIR = "data"
FLAT_DIR = "data/csv"
os.makedirs(FLAT_DIR, exist_ok=True)

for root, dirs, files in os.walk(DATA_DIR):
    for file in files:
        if file.endswith(".csv"):
            src = os.path.join(root, file)
            dst = os.path.join(FLAT_DIR, file)
            if not os.path.exists(dst):
                shutil.copy(src, dst)

