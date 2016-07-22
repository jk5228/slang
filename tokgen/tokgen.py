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
#       label = literal
#
# or a pattern in the form
#
#       label [ : | < ] pattern
#
# Whitespace is ignored. Lines in the spec beginning with "#" are ignored.
# Literals are matched before patterns. The separator ":" denotes a pattern that
# should be included in the token list and the separator "<" denotes a pattern
# that should be omitted from the token list. To use only a particular group of
# a matched pattern as the value of the token, name that group "val" according
# to the Python re module convention
#
#       ...(?P<val>pattern)...
#
# where "pattern" is the pattern to match and use, and "..." is a (possibly
# empty) pattern to match and discard.

import re
from itertools import chain

tokprog = '''# A tokenizer generated from tokgen.py.
# This code is automatically generate. Do not edit!

import re
from itertools import chain

ws = re.compile('\s+')
triples = [{0}]

# Return a list of label-token pairs given a program string.
def tokenize(prog):
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
        for (label, typ, pattern) in triples:
            match = re.match(pattern, prog)
            if match:
                if typ == '<': pass
                # print('match ' + str(match))
                elif match.groups('val'):
                    tokens.append((label, match.group('val')))
                else:
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
            raise SyntaxError('line %d: unexpected sequence "%s".'
                              % (linecount, linefrag))

    return tokens'''

# Return a list of label-type-value triples for the spec string.
def parse_spec(spec):
    lines = spec.split('\n')
    triples = []
    literals = []
    patterns = []

    # Process lines
    for (i, line) in enumerate(lines):

        # Ignore empty lines and comments
        if not line.split() or line[0] == '#':
            continue

        # Validate line format
        terms = line.split()

        if len(terms) != 3:
            raise SyntaxError('line %d: expected format "label [:=<] value" with' +
                '  3 terms but instead got line "%s" with %d terms.' % (i, line, len(terms)))

        if terms[1] == '=':
            literals.append(terms)
        else:
            patterns.append(terms)

    # Sort literals
    triples.extend(sorted(literals, key=lambda x: x[0], reverse=True))
    triples.extend(patterns)

    return triples

# Return a tokenizer function for the given spec string.
def tokenizer(spec):
    ws = re.compile('\s+')
    triples = parse_spec(spec)

    def tokenize(prog):
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
            for (label, typ, pattern) in triples:
                match = re.match(pattern, prog)
                if match:
                    if typ == '<': pass
                    # print('match ' + str(match))
                    elif match.groups('val'):
                        tokens.append((label, match.group('val')))
                    else:
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
                raise SyntaxError('line %d: unexpected sequence "%s".'
                                  % (linecount, linefrag))

        return tokens

    return tokenize

# Create a tokenizer Python program file at the given path, based on the given
# spec string.
def tok_file(path, spec):
    triples = parse_spec(spec)
    triple_strs = []

    for (label, typ, value) in triples:
        if typ == '=':
            triple_strs.append('(\'%s\', \'%s\', re.compile(re.escape(\'%s\')))' % (label, typ, value))
        else:
            triple_strs.append('(\'%s\', \'%s\', re.compile(\'%s\'))' % (label, typ, value))

    # Write file
    f = open(path, 'w')
    f.write(tokprog.format(','.join(triple_strs)))
    f.close()

# When executed, take filepath fpath and spec filepath sfpath arguments and
# write a tokenizer program to fpath given the spec at sfpath.
if __name__ == "__main__":
    from sys import argv
    fpath = argv[1]
    spec = open(argv[2], 'r').read()
    tok_file(fpath, spec)