# map_filter_reduce.py

from functools import reduce

numbers = [1, 2, 3, 4, 5]

# map example (square numbers)
squares = list(map(lambda x: x**2, numbers))
print("Squares:", squares)

# filter example (even numbers)
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", evens)

# reduce example (sum of numbers)
total = reduce(lambda a, b: a + b, numbers)
print("Sum:", total)
