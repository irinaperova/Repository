# write_files.py

file_path = "sample.txt"

# write mode (creates file or overwrites)
with open(file_path, "w", encoding="utf-8") as f:
    f.write("Python File Handling Example\n")
    f.write("Line 2: Learning file operations\n")
    f.write("Line 3: Practice makes perfect\n")

print("File created and written successfully.")
