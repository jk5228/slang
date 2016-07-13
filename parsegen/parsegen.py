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

from collections import defaultdict

# Return a dictionary of nonterminals mapped to lists of productions for the
# given spec string.
def parse_spec(spec):
    lines = spec.split('\n')
    rules = defaultdict(list)
    ident = re.compile('\w+')

    # Process lines
    while i < len(lines):

        line = lines[i]

        # Ignore empty lines and comments
        if not line.split() or line[0] == '#':
            i += 1
            continue

        # Validate line format
        terms = line.split()

        if re.match(ident, terms[0]) and terms[1] == ':':   # New production rule
            nonterm = terms[0]
            prod = []
            i += 1

            # Join all lines of current production rule
            for line in lines[i+1:]:
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
            if len(terms[2:]) or terms[-1] == '|':
                raise SyntaxError('cannot have empty production without explicit "EMPTY"')

            # Process production rule
            for term in terms[2:]:
                if term == '|':
                    if len(prod):
                        rules[nonterm].append(prod)
                        prod = []
                    else:
                        raise SyntaxError('cannot have empty' +
                                          ' production with explicit "EMPTY"' % (i))
                else:
                    prod.append(term)

            # Add last production
            rules[nonterm].append(prod)

        else:
            raise SyntaxError('line %d: expected format "nonterminal : production" or' +
                ' "| production" but instead got line "%s".' % (i, line))

    return rules

# When executed, take filepath fpath and spec filepath sfpath arguments and
# write a parser program to fpath given the spec at sfpath.
if __name__ == "__main__":
    from sys import argv
    fpath = argv[1]
    spec = open(argv[2], 'r').read()
    # TODO: generate parser file