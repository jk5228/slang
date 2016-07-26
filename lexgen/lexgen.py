#!/usr/local/bin/python3

# LexGen                                                    Jason Kim, 7/12/2016
# A lexer generator.
# Takes a token spec in the .tok format and returns a lexer that follows the
# spec. The lexer takes a program string and returns a list of pairs in the
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
# Patterns are matched using the re.DOTALL and re.MULTILINE flags. Lines in the
# spec beginning with "#" are ignored. Literals are matched before patterns. The
# separator ":" denotes a pattern that should be included in the token list and
# the separator "<" denotes a pattern that should be omitted from the token
# list. To use only a particular group of a matched pattern as the value of the
# token, name that group "val" according to the Python re module convention
#
#       ...(?P<val>pattern)...
#
# where "pattern" is the pattern to match and use, and "..." is a (possibly
# empty) pattern to match and discard.

import re

# Configuration variables

template_path = 'lexer_template.py'         # Filepath of the template lexer
lexer_suffix = '.py'                        # File suffix for lexer

# Return a list of label-type-value triples for the spec file.
def parse_spec(spec):
    triples = []
    literals = []
    patterns = []

    # Process lines
    for (i, line) in enumerate(spec.readlines()):

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

# Create a lexer Python program file at the given path, given a spec file.
def lexer_file(path, spec):
    triples = parse_spec(spec)
    triple_strs = []

    for (label, typ, value) in triples:
        if typ == '=':
            triple_strs.append('(\'%s\', \'%s\', re.compile(re.escape(\'%s\')))' % (label, typ, value))
        else:
            triple_strs.append('(\'%s\', \'%s\', re.compile(\'%s\', re.DOTALL|re.MULTILINE))' % (label, typ, value))

    # Write file
    temp_str = open(template_path, 'r').read()
    f = open(path+lexer_suffix, 'w')
    f.write(temp_str.format(','.join(triple_strs)))
    f.close()

# When executed, take filepath fpath and spec filepath sfpath arguments and
# write a lexer program to fpath given the spec at sfpath.
if __name__ == "__main__":
    from sys import argv
    fpath = argv[1]
    spec = open(argv[2], 'r')
    lexer_file(fpath, spec)