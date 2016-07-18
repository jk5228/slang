# The Slang global environment                               Jason Kim 7/16/2016
# The global environment contains built-in functions and other predefined global
# variables.

import execute
from collections import OrderedDict

# Built-in functions

# Print the given value.
def s_print(value):
    print(str(value))
    return execute.number(0)

# Return the array of integers in the interval [lo, hi).
def s_range(lo, hi):
    return execute.array([execute.number(i) for i in range(lo, hi)])

# Return the size of the array.
def s_size(arr):
    return execute.number(len(arr))

# Return an array with the given length, initialized to zeros.
def s_array(n):
    return execute.array([0 for i in range(n)])

# Return an item after adding it to the end of the given array.
def s_add(arr, item):
    arr.append(item)
    return item

# The global environment

env = OrderedDict({
    'print': execute.built_in_func(s_print),
    'range': execute.built_in_func(s_range),
    'size': execute.built_in_func(s_size),
    'array': execute.built_in_func(s_array),
    'add': execute.built_in_func(s_add)
})