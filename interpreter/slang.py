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
# - better modularize interpreter components
# - write lexer generator that takes token spec as input
# - lexer takes program string and returns list of labelled tokens
# - write parser generator that takes CFG as input (should follow recursive descent parser website algos for normalizing cfg)
# - parser gen: (1) remove cyclic left recursion, (2) factor, (3) substitute, (4) generate rec-des productions
# - rec-des parser takes list of labelled tokens and returns parse tree
# - robust error messages during lexing/parsing
# - optional environment dump at run-time error
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
# import interpret

# Run the program string.
def run(p):
    tokens = tokenize.tokenize(p)           # Tokenize
    # print(tokens)
    tree = parse.parse(tokens)              # Parse
    parse.print_tree(tree)

    # envs = [global_env]         # Create environment stack
    # print(stms)
    # execute(envs, stms)         # Execute

# Run Slang as a script.
if __name__ == "__main__":
    from sys import argv
    script = open(argv[-1], 'r').read()
    run(script)