#!/usr/local/bin/python3

# StupidLang (aka Slang)                                     Jason Kim, 7/7/2016
# A stupid Python-interpreted, dynamically-typed, imperative programming
# language, featuring first-class functions and multitype arrays.

# Language notes:
# - Comments run from # to the end of the line.
# - Only 0, "", and [] are falsy.
# - Functions without a return value return the value of the last statement.
# - Expressions with more than one term must be wrapped by parentheses.
# - For loops work like Python for loops, iterating over an array.
# - Built-in functions include: print, range, size, array.

# TODO:
# - overall goal: make language I would enjoy using and resolves issues in Python
# - robust error messages during lexing/parsing
# - optional environment dump at run-time error
# - Slang REPL
# - IR optimizations (contracting a subset of the NTs [allow user to specify this in .syn file])
# - classes
# - lambdas
# - ranges (a la Ruby)
# - built-in, first-class regexes
# - Currying?
# - optional static type-checking?
# - strong typing?
# - "compilation" into condensed format or even bytecode?
# - include other useful built-in functions
# - robust pattern-matching
# - either support or disallow nested functions
# - make parethesization and general syntax more optional/flexible (make arg lists comma-separated, remove parens around program, consider ws?)
# - make operators infix

from collections import deque
import parse
import tokenize
import env
import execute
import repl

# Run the program string.
def run(p):
    tokens = tokenize.tokenize(p)           # Tokenize
    # print(tokens)
    tree = parse.parse(tokens)              # Parse
    # parse.print_tree(tree)
    stms = tree[1]
    envs = [env.env]                        # Create environment stack
    execute.execute(envs, stms)             # Execute

# Run Slang as a command-line program.
if __name__ == "__main__":
    from sys import argv
    if len(argv) >= 2:                      # Execute script
        script = open(argv[1], 'r').read()
        run(script)
    else:                                   # Launch REPL
        repl.launch()