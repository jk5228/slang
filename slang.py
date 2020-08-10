#!/usr/local/bin/python3

# StupidLang (aka Slang)                                     Jason Kim, 7/7/2016
# A stupid Python-interpreted, dynamically-typed, imperative programming
# language, featuring first-class functions and multitype arrays.

# Language notes:
# - Comments run from # to the end of the line.
# - Only 0, "", and [] are falsy.
# - Functions without a return value return the value of the last statement.
# - For loops work like Python for loops, iterating over an array.
# - Built-in functions include: print, size, array.
# - The range n..m evaluates to the array of numbers from n to m.
# - The range n...m evaluates to the array of numbers from n to m-1.
# - An array comprehension returns a new array.
# - An array comprehension with a filter expression evaluates the filter
#   expression and places each result into the return array.

# BUGS:
# - variable names that have keywords as prefixes aren't tokenized correctly
# - fix env stack so function calls can only see local and global envs

# TODO:
# - add negative sign
# - split out built-ins from env.py
# - if, else if
# - implement built-in functions in Slang
# - have well-defined interfaces with Python functions for I/O and other OS features
# - complete error-handling
# - optional environment dump at run-time error
# - classes
# - flesh out built-in classes with methods
# - lambdas
# - slice syntax (a la Python)
# - built-in, first-class regexes
# - Currying?
# - optional static type-checking?
# - strong typing?
# - "compilation" into condensed format or even bytecode?
# - include other useful built-in functions
# - robust pattern-matching
# - either support or disallow nested functions and closures

from collections import deque
from parsegen import parse, node
from lexgen import lex
import repl
from interpreter import env, execute

# Instantiate lexer
lexer = lex.lexer()

# Run the program string.
def run(p):
    lexer.set_str(p)
    lexer.reset()
    tree = parse.parse(lexer)               # Parse
    # node.print_tree(tree)
    stms = tree.children
    envs = [env.env]                        # Create environment stack
    return execute.execute(envs, stms)      # Execute

# Run Slang as a command-line program.
if __name__ == "__main__":
    from sys import argv
    if len(argv) >= 2:                      # Execute script(s)
        for fname in argv[1:]:
            try:
                script = open(fname, 'r').read()
                run(script)
            except Exception as err:
                print('Error: "%s": %s' % (fname, err))
    else:                                   # Launch REPL
        repl.launch()
