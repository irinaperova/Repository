# move_files.py

import os
import shutil

source_dir = "."
target_dir = "txt_files"

os.makedirs(target_dir, exist_ok=True)

# find .txt files
for file in os.listdir(source_dir):
    if file.endswith(".txt"):
        shutil.move(file, os.path.join(target_dir, file))
        print(f"Moved: {file}")
