# create_list_dirs.py

import os

# current directory
print("Current directory:", os.getcwd())

# create directories
os.makedirs("test_dir/sub_dir", exist_ok=True)

print("Directories created.")

# list directory contents
print("\nFiles and folders:")
for item in os.listdir("."):
    print(item)
