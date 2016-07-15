#!/usr/bin/python

# ParseGen                                                  Jason Kim, 7/12/2016
# A parser generator.
# Takes a grammar in the .syn format and returns a parser that follows the spec.
# The parser takes a list of tokens (label-value string pairs) and returns a
# parse "tree" (a list of lists) representing the parsed program.
# 
# The .syn format:
# A grammar is a list of one or more production rules. A production rule has the
# format
#
#       nonterminal : [ "EMPTY" | nonterminal | terminal ] +
#               [ "|" [ "EMPTY" | nonterminal | terminal ] + ] +
#
# where "nonterminal" is a nonterminal symbol, "EMPTY" generates no production
# (i.e., epsilon), and "terminal" is a terminal symbol. Production rules may
# be written on a single line or on multiple lines, with all lines after the
# first beginning with "|". Whitespace in a .syn file is ignored. Lines in the
# spec beginning with "#" are ignored. The first nonterminal specified is
# considered the root nonterminal of the grammar.

import re
from collections import defaultdict, OrderedDict

# Return a root nonterminal and defaultdict(list) of nonterminals mapped to
# lists of productions for the given spec string.
def parse_spec(spec):
    lines = spec.split('\n')
    rules = defaultdict(list)
    ident = re.compile('\w+')
    root = None
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
        empty = False
        i += 1

        # Get root nonterminal
        if not root:
            root = nonterm

        # Merge all lines of current production rule
        for line in lines[i:]:
            newterms = line.split()
            if not len(newterms):
                i += 1
                continue
            elif newterms[0] == '|':
                terms += newterms
                i += 1
            else:
                break

        # Verify that production isn't empty and doesn't end with '|'
        if not len(terms[2:]) or terms[-1] == '|':
            raise SyntaxError('cannot have empty production without explicit "EMPTY"' +
                              ' but got production rule "%s"' % (' '.join(terms)))

        # print('nt, ts: %s, %s' % (nonterm, str(terms)))

        # Process production rule
        for term in terms[2:]:
            if term == '|':
                if len(prod) or empty:
                    rules[nonterm].append(prod)
                    prod = []
                    empty = False
                else:
                    raise SyntaxError('cannot have empty production without explicit "EMPTY"' +
                                      ' but got production rule "%s"' % (' '.join(terms)))
            elif term == 'EMPTY':
                    empty = True
            else:
                prod.append(term)

        # Add last production (we know we don't have an implicit empty)
        rules[nonterm].append(prod)

    return (root, rules)


# An entry object in an Earley parse chart. Children is the pointer to the
# children entries in the parse tree.
class entry(object):
    def __init__(self, type, nt, prod, origin, dot):
        self.type = type
        self.nt = nt
        self.prod = prod
        self.origin = origin
        self.dot = dot
        self.children = []

    # Return a string id unique for each (nt, prod, origin) triple.
    def id(self):
        return '{0}:{1};{2},{3}'.format(self.nt, self.prod, self.origin, self.dot)

    # Return whether the production is completed.
    def completed(self):
        return self.dot >= len(self.prod)

    # Return the next symbol to process.
    def next(self):
        if not self.completed():
            return self.prod[self.dot]
        else:
            raise IndexError('no next term for completed production "%s".' % str(self.prod))

# Add the entry to the column (OrderedDict) if there isn't already a rule with
# the same id in the column.
def add(col, e):
    if not col.get(e.id()):
        col[e.id()] = e

# Add any predicted entries to the given column.
def predict(rules, i, col, e):
    for prod in rules[e.next()]:
        add(col, entry('pred', e.next(), prod, i, 0))

# Add the scanned entry to the given column if the next token is expected.
def scan(token, i, col, e):
    if e.next() == token[0]:
        scan_ent = entry('scan', e.nt, e.prod, e.origin, e.dot+1)
        scan_ent.children = e.children          # Pass on children
        add(col, scan_ent)

# Add the completed entry to the given column.
def complete(rules, cols, col, e):
    # print(col.values())
    for cand in cols[e.origin].values():
        # print('CAND: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
        # print(cand.id())
        if not cand.completed() and rules[cand.next()] and cand.next() == e.nt:
            print('%s completing %s' % (e.id(), cand.id()))
            print('cand %s children: %s' % (cand.id(), [e.id() for e in cand.children]))
            print('comp %s children: %s' % (e.id(), [e.id() for e in e.children]))
            comp_ent = entry('comp', cand.nt, cand.prod, cand.origin, cand.dot+1)
            comp_ent.children = cand.children[:] # Pass on children
            comp_ent.children.append(e)         # Add child
            add(col, comp_ent)
            # print('COMP: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))

# Return the parse tree (list) for the given root entry of an Earley parse.
def getparse(rules, tokens, root):
    if not root: return
    rhs = []
    children = iter(root.children)
    print('%s: %s' % (root.nt, [e.id() for e in root.children]))
    for (i, term) in enumerate(root.prod):
        if rules[term]:                     # Nonterminal
            try:
                rhs.append(getparse(rules, tokens, next(children)))
            except StopIteration:
                pass
        else:                               # Terminal
            rhs.append(tokens[i+root.origin])
    return (root.nt, rhs)


# Return an Earley parser given a grammar. The parser returns the parse tree of
# a given list of tokens or raises an error if there is more than one valid
# parse of the list of tokens.
def parser(root, rules):

    # The Earley parser function
    def parsefun(tokens):

        # Initialize chart
        cols = [OrderedDict() for i in range(len(tokens)+1)]
        for prod in rules[root]:            # Add all possible root productions
            e = entry('pred', root, prod, 0, 0)
            add(cols[0], e)

        # Fill chart
        for (i, col) in enumerate(cols):
            if not len(col):
                raise SyntaxError('unexpected token "%s"' % tokens[i][1])       # TODO:

            # if i > 30: return
            l, r = tokens[i] if i < len(tokens) else ('','')
            print('=== col %d : %s %s ===' % (i, l, r))

            for e in col.values():
                print('entry: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
                print('children: %s' % [c.id() for c in e.children])
                if not e.completed():       # Uncompleted
                    if rules[e.next()]:     # Nonterminal
                        predict(rules, i, col, e)
                    else:                   # Terminal
                        print('scan')
                        if i+1 < len(cols):
                            scan(tokens[i], i+1, cols[i+1], e)
                else:                       # Completed
                    print('comp')
                    complete(rules, cols, col, e)

        # Verify that there was a valid parse
        roots = [e for e in cols[-1].values() if e.nt == root and e.origin == 0 and e.completed()]
        if len(roots) != 1:
            raise SyntaxError('expected 1 valid parse but got ' + str(len(roots)))
            for rt in roots:              # Print valid parse trees for tokens
                print(getparse(rules, tokens, rt))

        # Return the valid parse tree
        return getparse(rules, tokens, roots[0])

    # Return parser function
    return parsefun

# # Test code

syn = open('slang.syn', 'r').read()
root, rules = parse_spec(syn)
# print(root, rules)
parser = parser(root, rules)

# # When executed, take filepath fpath and spec filepath sfpath arguments and
# # write a parser program to fpath given the spec at sfpath.
# if __name__ == "__main__":
#     from sys import argv
#     fpath = argv[1]
#     spec = open(argv[2], 'r').read()
#     # TODO: generate parser file