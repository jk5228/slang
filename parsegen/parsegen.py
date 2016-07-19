#!/usr/local/bin/python3

# ParseGen                                                  Jason Kim, 7/12/2016
# A parser generator.
# Takes a grammar in the .syn format and returns a parser that follows the spec.
# The parser takes a list of tokens (label-value string pairs) and returns a
# parse "tree" (a list of lists) representing the parsed program.
# 
# The .syn format:
# A grammar is a list of one or more production rules, as well as an optional
# first line listing terminal symbols to preserve in the parse tree. This line
# should have the format
#
#       : [ terminal ] *
#
# where "terminal" is a terminal symbol.
#
# A production rule
# has the format
#
#       nonterminal [ : | < ] [ "EMPTY" | nonterminal | terminal ] +
#                       [ "|" [ "EMPTY" | nonterminal | terminal ] + ] +
#
# where "nonterminal" is a nonterminal symbol, "EMPTY" generates no production
# (i.e., epsilon), and "terminal" is a terminal symbol. Production rules may
# be written on a single line or on multiple lines, with all lines after the
# first beginning with "|".
#
# Whitespace in a .syn file is ignored. Lines in the spec beginning with "#" are
# ignored. The first nonterminal specified is considered the root nonterminal of
# the grammar. The separator ":" denotes a nonterminal that will be kept
# around in the generated parse tree. The other separator "<" denotes a
# nonterminal that will be contracted from the parse tree (i.e., it's children
# become the children of the parent of the contracted nonterminal node).

import re
from collections import defaultdict, OrderedDict

# Parser program
parseprog = '''# A parser generated from parsegen.py.

from collections import defaultdict, OrderedDict
root = '{0}'
tlist = [{1}]
clist = [{2}]
rules = defaultdict(list, {{{3}}})

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
        return '%s:%s:%s:%s' % (self.nt, self.prod, self.origin, self.dot)

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
        scan_ent.children.append(token)         # Add terminal
        add(col, scan_ent)

# Add the completed entry to the given column.
def complete(roots, rules, cols, i, e):
    # print(col.values())
    for cand in list(cols[e.origin].values()):
        # print('CAND: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
        # print(cand.id())
        if not cand.completed() and rules[cand.next()] and cand.next() == e.nt:
            # print('%s completing %s' % (e.id(), cand.id()))
            # print('cand %s children: %s' % (cand.id(), [e.id() for e in cand.children]))
            # print('comp %s children: %s' % (e.id(), [e.id() for e in e.children]))
            comp_ent = entry('comp', cand.nt, cand.prod, cand.origin, cand.dot+1)
            comp_ent.children = cand.children[:] # Pass on children
            comp_ent.children.append(e)         # Add child
            add(cols[i], comp_ent)
            # print('COMP: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
            if i == len(cols)-1 and comp_ent.nt == root and comp_ent.origin == 0 and comp_ent.completed():
                return True
    return False


# Return the parse tree (list) for the given root entry of an Earley parse.
def get_tree(rules, tokens, root):
    if type(root) != entry: return root
    rhs = []
    children = iter(root.children)
    # print(root.children)
    # print('%s: %s' % (root.nt, [e.id() for e in root.children]))
    for child in root.children:
        rhs.append(get_tree(rules, tokens, child))
    return (root.nt, rhs)

# Return the given parse tree after normalization. A normalized tree contains
# none of the nonterminals in clist and all and only the terminals in tlist.
def normalize_tree(tlist, clist, root):
    def rec(root):
        if not root: return []
        lhs, rhs = root
        if type(rhs) == list:       # Nonterminal
            res_rhs = []
            rhs = [rec(t) for t in rhs]
            rhs = [item for sublist in rhs for item in sublist]
            for t in rhs:
                if type(t) == list: res_rhs.extend(t)
                else: res_rhs.append(t)
            if lhs in clist:        # Contracted nonterminal
                return [res_rhs]
            else:                   # Uncontracted nonterminal
                return [(lhs, res_rhs)]
        elif lhs in tlist:          # Preserved terminal
                return [(lhs, rhs)]
        else:                       # Unpreserved terminal
            return []
    return rec(root)[0]

# Pretty print the parse tree, with subsequent levels indented to show nesting.
def print_tree(root):
    def rec(root, level):
        if not root: return
        lhs, rhs = root
        print(('%s%s' % ('| '*level, lhs)), end='')
        if type(rhs) == list:
            print()
            for term in rhs:
                rec(term, level+1)
        else:
            print(' : %s' % rhs)
    rec(root, 0)

# The Earley parser function
def parse(tokens):

    # Initialize chart
    cols = [OrderedDict() for i in range(len(tokens)+1)]
    for prod in rules[root]:            # Add all possible root productions
        e = entry('pred', root, prod, 0, 0)
        add(cols[0], e)

    # Fill chart
    for (i, col) in enumerate(cols):
        if not len(col):
            raise SyntaxError('unexpected token "%s".' % tokens[i][1])       # TODO: line number for errors

        # if i > 30: return
        # l, r = tokens[i] if i < len(tokens) else ('','')
        # print('=== col %d : %s %s ===' % (i, l, r))

        j = 0
        while j < len(col):
            e = list(col.values())[j]
            # print('entry: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
            # print('children: %s' % [c.id() for c in e.children])
            if not e.completed():       # Uncompleted
                if rules[e.next()]:     # Nonterminal
                    # print('pred')
                    predict(rules, i, col, e)
                else:                   # Terminal
                    # print('scan')
                    if i+1 < len(cols):
                        scan(tokens[i], i+1, cols[i+1], e)
            else:                       # Completed
                # print('comp')
                if complete(root, rules, cols, i, e): break
            j += 1

    # Verify that there was a valid parse
    roots = [e for e in cols[-1].values() if e.nt == root and e.origin == 0 and e.completed()]
    if len(roots) != 1:                 # TODO: b/c of OrderedDict is a set, we'll never get multiple valid parses in last col
        raise SyntaxError('expected 1 valid parse but got %s.' % str(len(roots)))
        for rt in roots:              # Print valid parse trees for tokens
            print_tree(get_tree(rules, tokens, rt))

    # Return the valid parse tree
    return normalize_tree(tlist, clist, get_tree(rules, tokens, roots[0]))'''

# Return a root nonterminal and defaultdict(list) of nonterminals mapped to
# lists of productions for the given spec string.
def parse_spec(spec):
    lines = spec.split('\n')
    rules = defaultdict(list)
    tlist = []
    clist = []
    ident = re.compile('\w+')
    root = None
    checked_tlst = False
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

        # Check for terminal list
        if not checked_tlst:
            checked_tlst = True
            if len(terms) and terms[0] == ':':
                tlist = terms[1:]
                i += 1
                continue

        # Validate format
        if not re.match(ident, terms[0]) or len(terms) == 1 or terms[1] not in ':<':
            raise SyntaxError('expected format "nonterminal [:|<] production" or' +
                              ' "| production" but instead got production rule "%s".' % (line))

        nonterm = terms[0]
        prod = []
        empty = False
        i += 1

        # Add any contracted nonterminals to the list
        if terms[1] == '<':
            clist.append(nonterm)

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
                              ' but got production rule "%s".' % (' '.join(terms)))

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
                                      ' but got production rule "%s".' % (' '.join(terms)))
            elif term == 'EMPTY':
                    empty = True
            else:
                prod.append(term)

        # Add last production (we know we don't have an implicit empty)
        rules[nonterm].append(prod)

    return (root, tlist, clist, rules)

# LR(1) Parser generation code

# To build states and edges:

# Data structures:
# List of states
# List of shift edges (state-terminal pairs)
# List of goto edges (state-nonterminal pairs)
# Item object containing nt symbol, prod symbol list, pos, lookahead symbol
# AST node object containing parent symbol, prod symbol list if any (need?), children list, start, end

# Add aux production rule S -> S$
# Build T and E sets (p. 60)

# To make table:

# Data structures:
# Final LR table is dict<state number, dict<lookahead symbol, action>>

# Accept action for each state with S -> S.$ item
# Reduce for each item with dot at end

# To deal with precedence/associativity (left, right, nonassoc):
# Dict of precedences of terminals (map terminal to number [assigned by incrementing cnt as directives processed])
# defaultdict(None) of associativity (left, right, None = nonassoc)
# Whenever shift-reduce conflict between ordered ops, consult prec dict and pick whichever is higher

# To include positions for error messages:
# Extract from underlying token objects

# Allow Python semantic actions for each production in .syn?





# OLD EARLEY PARSER GEN

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
        return '%s:%s:%s:%s' % (self.nt, self.prod, self.origin, self.dot)

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
        scan_ent.children.append(token)         # Add terminal
        add(col, scan_ent)

# Add the completed entry to the given column.
def complete(root, rules, cols, i, e):
    # print(col.values())
    for cand in list(cols[e.origin].values()):
        # print('CAND: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
        # print(cand.id())
        if not cand.completed() and rules[cand.next()] and cand.next() == e.nt:
            # print('%s completing %s' % (e.id(), cand.id()))
            # print('cand %s children: %s' % (cand.id(), [e.id() for e in cand.children]))
            # print('comp %s children: %s' % (e.id(), [e.id() for e in e.children]))
            comp_ent = entry('comp', cand.nt, cand.prod, cand.origin, cand.dot+1)
            comp_ent.children = cand.children[:] # Pass on children
            comp_ent.children.append(e)         # Add child
            add(cols[i], comp_ent)
            # print('COMP: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
            if i == len(cols)-1 and comp_ent.nt == root and comp_ent.origin == 0 and comp_ent.completed():
                return True
    return False

# Return the parse tree (list) for the given root entry of an Earley parse.
def get_tree(rules, tokens, root):
    if type(root) != entry: return root
    rhs = []
    children = iter(root.children)
    # print(root.children)
    # print('%s: %s' % (root.nt, [e.id() for e in root.children]))
    for child in root.children:
        rhs.append(get_tree(rules, tokens, child))
    return (root.nt, rhs)

# Return the given parse tree after normalization. A normalized tree contains
# none of the nonterminals in clist and all and only the terminals in tlist.
def normalize_tree(tlist, clist, root):
    def rec(root):
        if not root: return []
        lhs, rhs = root
        if type(rhs) == list:       # Nonterminal
            res_rhs = []
            rhs = [rec(t) for t in rhs]
            rhs = [item for sublist in rhs for item in sublist]
            for t in rhs:
                if type(t) == list: res_rhs.extend(t)
                else: res_rhs.append(t)
            if lhs in clist:        # Contracted nonterminal
                return [res_rhs]
            else:                   # Uncontracted nonterminal
                return [(lhs, res_rhs)]
        elif lhs in tlist:          # Preserved terminal
                return [(lhs, rhs)]
        else:                       # Unpreserved terminal
            return []
    return rec(root)[0]

# Pretty print the parse tree, with subsequent levels indented to show nesting.
def print_tree(root):
    def rec(root, level):
        if not root: return
        lhs, rhs = root
        print(('%s%s' % ('| '*level, lhs)), end='')
        if type(rhs) == list:
            print()
            for term in rhs:
                rec(term, level+1)
        else:
            print(' : %s' % rhs)
    rec(root, 0)

# Return an Earley parser given a grammar. The parser returns the parse tree of
# a given list of tokens or raises an error if there is more than one valid
# parse of the list of tokens.
def parser(root, rules):

    # The Earley parser function
    def parse(tokens):

        # Initialize chart
        cols = [OrderedDict() for i in range(len(tokens)+1)]
        for prod in rules[root]:            # Add all possible root productions
            e = entry('pred', root, prod, 0, 0)
            add(cols[0], e)

        # Fill chart
        for (i, col) in enumerate(cols):
            if not len(col):
                raise SyntaxError('unexpected token "%s".' % tokens[i][1])       # TODO: line number for errors

            # if i > 30: return
            # l, r = tokens[i] if i < len(tokens) else ('','')
            # print('=== col %d : %s %s ===' % (i, l, r))

            j = 0
            while j < len(col):
                e = list(col.values())[j]
                # print('entry: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
                # print('children: %s' % [c.id() for c in e.children])
                if not e.completed():       # Uncompleted
                    if rules[e.next()]:     # Nonterminal
                        # print('pred')
                        predict(rules, i, col, e)
                    else:                   # Terminal
                        # print('scan')
                        if i+1 < len(cols):
                            scan(tokens[i], i+1, cols[i+1], e)
                else:                       # Completed
                    # print('comp')
                    if complete(root, rules, cols, i, e): break
                j += 1

        # Verify that there was a valid parse
        roots = [e for e in cols[-1].values() if e.nt == root and e.origin == 0 and e.completed()]
        if len(roots) != 1:                 # TODO: b/c of OrderedDict is a set, we'll never get multiple valid parses in last col
            raise SyntaxError('expected 1 valid parse but got %d.' % str(len(roots)))
            for rt in roots:              # Print valid parse trees for tokens
                print_tree(get_tree(rules, tokens, rt))

        # Return the valid parse tree
        return normalize_tree(tlist, clist, get_tree(rules, tokens, roots[0]))

    # Return parser function
    return parse

# Create a parser Python program file at the given path, based on the given spec
# string.
def parse_file(path, spec):
    root, tlist, clist, rules = parse_spec(spec)
    tlist = ['\'%s\'' % t for t in tlist]
    clist = ['\'%s\'' % c for c in clist]
    rule_lst = []

    # Convert rules dict to strings
    for (lhs, rhs) in rules.items():
        prods = []
        for lst in rhs:
            prods.append('[{0}]'.format(','.join('\'{0}\''.format(t) for t in lst)))
        rule = '\'{0}\':[{1}]'.format(lhs, ','.join(prods))
        rule_lst.append(rule)

    # Write file
    f = open(path, 'w')
    f.write(parseprog.format(root, ','.join(tlist), ','.join(clist), ','.join(rule_lst)))
    f.close()

# # Test code

# syn = open('slang.syn', 'r').read()
# root, rules = parse_spec(syn)
# # print(root, rules)
# parser = parser(root, rules)

# When executed, take filepath fpath and spec filepath sfpath arguments and
# write a parser program to fpath given the spec at sfpath.
if __name__ == "__main__":
    from sys import argv
    fpath = argv[1]
    spec = open(argv[2], 'r').read()
    parse_file(fpath, spec)