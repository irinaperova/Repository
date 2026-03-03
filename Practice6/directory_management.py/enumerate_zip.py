# enumerate_zip_examples.py

names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

# enumerate example
print("Enumerate example:")
for index, name in enumerate(names):
    print(index, name)

# zip example
print("\nZip example:")
for name, score in zip(names, scores):
    print(name, score)

# sorted example
numbers = [5, 2, 9, 1]
print("\nSorted numbers:", sorted(numbers))

# built-in functions
print("\nBuilt-in functions examples:")
print("Length:", len(numbers))
print("Min:", min(numbers))
print("Max:", max(numbers))
print("Sum:", sum(numbers))

# type conversion
num_str = "123"
num_int = int(num_str)
print("\nConverted to int:", num_int)
print("Type:", type(num_int))
