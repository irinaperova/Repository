# copy_delete_files.py

import shutil
import os

source = "sample.txt"
backup = "sample_backup.txt"

# copy file
shutil.copy(source, backup)
print("File copied successfully.")

# delete file safely
if os.path.exists(backup):
    os.remove(backup)
    print("Backup file deleted.")
else:
    print("File does not exist.")
