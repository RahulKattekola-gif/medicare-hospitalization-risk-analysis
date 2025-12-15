import zipfile
import os

DATA_DIR = "data"

for file in os.listdir(DATA_DIR):
    if file.endswith(".zip"):
        zip_path = os.path.join(DATA_DIR, file)
        extract_dir = os.path.join(DATA_DIR, file.replace(".zip", ""))

        if os.path.exists(extract_dir):
            continue

        print(f"Extracting {file}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

