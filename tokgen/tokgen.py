#!/usr/local/bin/python3

# TokGen                                                    Jason Kim, 7/12/2016
# A tokenizer generator.
# Takes a token spec in the .tok format and returns a tokenizer that follows the
# spec. The tokenizer takes a program string and returns a list of pairs in the
# format (label, value), where label and value are both strings.
# 
# The .tok format:
# Each line specifies a token, whose label is on the left and whose value is on
# the right. Either a token is a literal in the form
#
#        label = literal
#
# or a pattern in the form
#
#        label : pattern
#
# Whitespace is ignored. Lines in the spec beginning with "#" are ignored. Only
# the last definition of a label is used. Literals are matched before patterns.

import re
from itertools import chain

tokprog = '''# A tokenizer generated from tokgen.py.

import re
from itertools import chain

ws = re.compile('\s+')
pairs = [{0}]

# Return a list of label-token pairs given a program string.
def tokfun(prog):
    tokens = []
    linecount = 1

    while len(prog):
        # print('prog: ' + prog)
        # print('tokens: ' + str(tokens))

        # Ignore whitespace
        match = re.match(ws, prog)
        if match:
            # print('ws ' + str(match))
            prog = prog[match.end(0):]
            linecount += match.group(0).count('\\n')
            continue

        # Match token patterns
        for (label, pattern) in pairs:
            match = re.match(pattern, prog)
            if match:
                # print('match ' + str(match))
                tokens.append((label, prog[:match.end(0)]))
                prog = prog[match.end(0):]
                break

        # No token patterns matched
        if not match:
            linefrag = ''
            try:
                linefrag = prog[:prog.index('\\n')]
            except ValueError:
                linefrag = prog
            raise SyntaxError('line %d: unexpected sequence "%s"'
                              % (linecount, linefrag))

    return tokens'''

# Return a list of label-type-value triples for the spec string.
def parse_spec(spec):
    lines = spec.split('\n')
    triples = []

    # Process lines
    for (i, line) in enumerate(lines):

        # Ignore empty lines and comments
        if not line.split() or line[0] == '#':
            continue

        # Validate line format
        terms = line.split()

        if len(terms) != 3:
            raise SyntaxError('line %d: expected format "label [:=] value" with' +
                '  3 terms but instead got line "%s" with %d terms.' % (i, line, len(terms)))

        triples.append(terms)

    return triples

# Return a list of label-regex pairs given a list of label-type-regex triples,
# with literals followed by patterns.
def get_pairs(triples):

    literals = dict()
    patterns = dict()

    for (label, typ, value) in triples:

        if typ == '=':                 # Literal
            literals[label] = value
        elif typ == ':':               # Pattern
            patterns[label] = re.compile(value)

    # print(literals)
    # print(patterns)

    literals = sorted(literals.items(), key=lambda x: x[1], reverse=True)
    literals = [(label, re.compile(re.escape(value))) for (label, value) in literals]

    # Return pairs
    return literals + list(patterns.items())

# Return a tokenizer function for the given spec string.
def tokenizer(spec):
    ws = re.compile('\s+')
    pairs = get_pairs(parse_spec(spec))

    def tokfun(prog):
        tokens = []
        linecount = 1

        while len(prog):
            # print('prog: ' + prog)
            # print('tokens: ' + str(tokens))

            # Ignore whitespace
            match = re.match(ws, prog)
            if match:
                # print('ws ' + str(match))
                prog = prog[match.end(0):]
                linecount += match.group(0).count('\n')
                continue

            # Match token patterns
            for (label, pattern) in pairs:
                match = re.match(pattern, prog)
                if match:
                    # print('match ' + str(match))
                    tokens.append((label, prog[:match.end(0)]))
                    prog = prog[match.end(0):]
                    break

            # No token patterns matched
            if not match:
                linefrag = ''
                try:
                    linefrag = prog[:prog.index('\n')]
                except ValueError:
                    linefrag = prog
                raise SyntaxError('line %d: unexpected sequence "%s"'
                                  % (linecount, linefrag))

        return tokens

    return tokfun

# Create a tokenizer Python program file at the given path, based on the given
# spec string.
def tok_file(path, spec):
    triples = parse_spec(spec)

    literals = dict()
    patterns = dict()
    pair_strs = []

    for (label, typ, value) in triples:

        if typ == '=':                 # Literal
            literals[label] = value
        elif typ == ':':               # Pattern
            patterns[label] = value

    # Add label-literal pairs in lexical order w/r/t literal
    for (label, value) in sorted(literals.items(), key=lambda x: x[1], reverse=True):
        pair_strs.append('(\'%s\', re.compile(re.escape(\'%s\')))' % (label, value))

    # Add label-pattern pairs in no particular order
    for (label, value) in patterns.items():
        pair_strs.append('(\'%s\', re.compile(\'%s\'))' % (label, value))

    # Write file
    f = open(path, 'w')
    f.write(tokprog.format(','.join(pair_strs)))
    f.close()

# When executed, take filepath fpath and spec filepath sfpath arguments and
# write a tokenizer program to fpath given the spec at sfpath.
if __name__ == "__main__":
    from sys import argv
    fpath = argv[1]
    spec = open(argv[2], 'r').read()
    tokfile(fpath, spec)