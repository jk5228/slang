#!/usr/bin/python

# ParseGen                                                  Jason Kim, 7/12/2016
# A parser generator.
# Takes a syntax in the .syn format and returns a parser that follows the spec.
# The parser takes a list of tokens (label-value string pairs) and returns a
# parse "tree" (a list of lists) representing the parsed program.
# 
# The .syn format:
# A production rule has the format
#
#       nonterminal : ["EMPTY"|nonterminal|terminal]+
#                ["|" ["EMPTY"|nonterminal|terminal]+]+
#
# where "nonterminal" is a nonterminal symbol, "EMPTY" generates no production
# (i.e., epsilon), and "terminal" is a terminal symbol. Production rules may
# be written on a single line or on multiple lines, with all lines after the
# first beginning with "|". Whitespace in a .syn file is ignored. Lines in the
# spec beginning with "#" are ignored.

import re
from collections import defaultdict

# Return a dictionary of nonterminals mapped to lists of productions for the
# given spec string.
def parse_spec(spec):
    lines = spec.split('\n')
    rules = defaultdict(list)
    ident = re.compile('\w+')
    i = 0

    # Process lines
    while i < len(lines):

        line = lines[i]
        terms = line.split()

        # print('line %d: "%s"' % (i, line))

        # Ignore empty lines and comments
        if not terms or line[0] == '#':
            i += 1
            continue

        # Validate format
        if not re.match(ident, terms[0]) or len(terms) == 1 or terms[1] != ':':
            raise SyntaxError('expected format "nonterminal : production" or' +
                              ' "| production" but instead got production rule "%s".' % (line))

        nonterm = terms[0]
        prod = []
        i += 1

        # Merge all lines of current production rule
        for line in lines[i:]:
            newterms = line.split()
            if not len(newterms):
                i += 1
                continue
            elif newterms[0] == '|':
                terms += newterms[1:]
                i += 1
            else:
                break

        # Verify that production isn't empty and doesn't end with '|'
        if not len(terms[2:]) or terms[-1] == '|':
            raise SyntaxError('cannot have empty production without explicit "EMPTY"' +
                              ' but got production rule "%s"' % (' '.join(terms)))

        # Process production rule
        for term in terms[2:]:
            if term == '|':
                if len(prod):
                    rules[nonterm].append(prod)
                    prod = []
                else:
                    raise SyntaxError('cannot have empty production without explicit "EMPTY"' +
                                      ' but got production rule "%s"' % (' '.join(terms)))
            else:
                prod.append(term)

        # Add last production
        rules[nonterm].append(prod)

    return rules

# Return the index after adding the new nonterminal to it.
def add(index, nt):
    index[nt] = len(index)
    return index

# Return the syntax after removing cyclic left recursion.
def remove_cyclic_left_rec(rules):
    index = {nt: i for (i, nt) in enumerate(rules)}     # Index of nonterminals
    key = lambda x: index[x]

    for (i, nt, prods) in ((index[nt], nt, rules[nt]) for nt in sorted(rules, key=key)):
        print('%d %s %s' % (i, nt, str(prods)))
        newprods = []
        for prod in prods:
            while rules[prod[0]] and index[prod[0]] < i:
                asd
            if prod[0] == nt:
                remove_left_rec()

# Return the normalized form of the syntax. This is the syntax obtained after
# removing left recursion, removing unreachable nonterminals, factoring, and
# substituting.
def normalize_syntax(rules):

    # Remove left recursion
    rules = remove_cyclic_left_rec(rules)

    # Remove unreachable nonterminals
    # TODO: this

    # Factor
    # TODO: factor

    # Substitute
    # TODO: substitute

    return rules

# # Test code

syn = open('sample.syn', 'r').read()
print(normalize_syntax(parse_spec(syn)))

# # When executed, take filepath fpath and spec filepath sfpath arguments and
# # write a parser program to fpath given the spec at sfpath.
# if __name__ == "__main__":
#     from sys import argv
#     fpath = argv[1]
#     spec = open(argv[2], 'r').read()
#     # TODO: generate parser file