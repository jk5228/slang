#!/usr/bin/python

# TokGen                                                    Jason Kim, 7/12/2016
# A tokenizer generator.
# Takes a token spec in the .tok format and returns a tokenizer that follows the
# spec. The tokenizer takes a program string and returns a list of strings
# labelled as pairs (label, string).
# 
# The .tok format:
# Each line specifies a token, whose label is on the left and whose value is on
# the right. Either a token is a literal in the form
#        label = literal
# or a regex in the form
#        label : regex
# Whitespace is ignored. Lines in the spec beginning with "#" are ignored. Only
# the last definition of a label is used. Literals are always matched before
# regexes.

import re
from itertools import chain

# Returns a tokenizer for the given dictionaries of literals and regexes.
def tokenizer(literals, regexes):
    ws = re.compile('\s+')
    def tokfun(prog):
        tokens = []

        while len(prog):
            print('prog: ' + prog)
            print('tokens: ' + str(tokens))

            # Ignore whitespace
            match = re.match(ws, prog)
            if match:
                print('ws ' + str(match))
                prog = prog[match.end(0):]
                continue

            # Match token patterns
            for (label, pattern) in chain(literals.items(), regexes.items()):
                match = re.match(pattern, prog)
                if match:
                    print('match ' + str(match))
                    tokens.append((label, prog[:match.end(0)]))
                    prog = prog[match.end(0):]
                    break

            # No token patterns matched
            if not match:
                raise SyntaxError('unexpected sequence "%s" ...' % (prog[:5]))

        return tokens

    return tokfun

# Returns a tokenizer for the spec.
def parse_spec(spec):
    literals = dict()
    regexes = dict()
    lines = spec.split('\n')

    # Process lines
    for line in lines:

        # Ignore empty lines and comments
        if not len(line) or line[0] == '#':
            continue

        # Validate line format
        terms = line.split()

        if len(terms) != 3:
            raise SyntaxError('expected format "label [:=] value" but got' +
                ' %d terms in line "%s".' % (len(terms), line))

        # Determine token type
        (label, typ, value) = terms

        if typ == '=':                 # Literal
            literals[label] = re.compile(re.escape(value))
        elif typ == ':':               # Regex
            regexes[label] = re.compile(value)

    # print(literals)
    # print(regexes)

    # Return tokenizer
    return tokenizer(literals, regexes)