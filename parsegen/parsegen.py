#!/usr/local/bin/python3

# ParseGen                                                  Jason Kim, 7/12/2016
# A parser generator.
# Takes a grammar in the .syn format and returns a parser that follows the spec.
# The parser takes a list of tokens (label-value string pairs) and returns a
# parse "tree" (a list of lists) representing the parsed program.
# 
# The .syn format:
# A grammar is a list of one or more production rules, as well as an optional
# first line listing terminal symbols to preserve in the parse tree and zero or
# more directives. This line of terminals should have the format
#
#       : [ terminal ] *
#
# where "terminal" is a terminal symbol. A directive has the format
# 
#       %directive [ terminal ] *
#
# where "directive" is "left", "right", or "nonassoc" (for left-, right-, and
# non-associative, respectively) and "terminal" is a terminal operator symbol.
# Terminals listed in a directive line are assigned a precedence number and that
# number is lower (higher precedence) than all precedence numbers assigned to
# terminals on later lines. Operator in the same line are assigned the same
# precedence number. A production rule has the format
#
#       nonterminal [ : | < ] [ "EMPTY" | nonterminal | terminal ] +
#                       [ "|" [ "EMPTY" | nonterminal | terminal ] + ] +
#
# where "nonterminal" is a nonterminal symbol, "EMPTY" generates no production
# (i.e., epsilon), and "terminal" is a terminal symbol. Production rules may
# be written on a single line or on multiple lines, with all lines after the
# first beginning with "|". The names "EMPTY", "START_SYM", "END_SYM", and "|"
# are reserved and cannot be used for any terminal or nonterminal symbol in the
# grammar.
#
# Whitespace in a .syn file is ignored. Lines in the spec beginning with "#" are
# ignored. The first nonterminal specified is considered the root nonterminal of
# the grammar. The separator ":" denotes a nonterminal that will be kept
# around in the generated parse tree. The other separator "<" denotes a
# nonterminal that will be contracted from the parse tree (i.e., it's children
# become the children of the parent of the contracted nonterminal node).

import re, time
from collections import defaultdict, OrderedDict

# Parser program
parseprog = ''

# The grammar object.
class grammar(object):

    def __init__(self, root, tlist, clist, rules, prec, assoc):
        self.root = root                    # Root symbol string
        self.tlist = tlist                  # List of terminals to keep in AST
        self.clist = clist                  # List of nonterminals to omit from AST
        self.rules = rules                  # Dictionary of production rules
        self.prec = prec                    # Dictionary of precedence numbers
        self.assoc = assoc                  # Dictionary of associativities
        self.first = defaultdict(set)       # Dictionary of first sets
        self.nullable = defaultdict(bool)   # Dictionary of nullabilities
        self.start_sym = 'START_SYM'        # Start symbol
        self.end_sym = 'END_SYM'            # End symbol

# Return a root nonterminal and defaultdict(list) of nonterminals mapped to
# lists of productions for the given spec string.
def parse_spec(spec):
    lines = spec.split('\n')
    root = None
    tlist = []
    clist = []
    rules = defaultdict(list)
    prec = defaultdict(None)
    assoc = defaultdict(None)
    ident = re.compile('\w+')
    checked_tlst = False
    i = 0
    prec_ind = 0

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

        # Parse directive
        if terms[0][0] == '%':

            direction = None

            if terms[0][1:] == 'left':
                direction = 'left'
            elif terms[0][1:] == 'right':
                direction = 'right'
            elif terms[0][1:] != 'nonassoc':
                raise SyntaxError('undefined directive %s.' % terms[0])

            for term in terms[2:]:
                prec[term] = prec_ind
                assoc[term] = direction

            prec_ind += 1
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

    return grammar(root, tlist, clist, rules, prec, assoc)

# LR(1) Parser generation code

# To build states and edges:

# Data structures:
# List of states
# List of shift edges (state-terminal pairs)
# List of goto edges (state-nonterminal pairs)
# Item object containing nt symbol, prod symbol list, pos, lookahead symbol
# AST node object containing parent symbol, prod symbol list if any (need?), children list, start, end

# An LR(1) parse table item.
class item(object):

    def __init__(self, nt, prod, dot, la):
        self.nt = nt            # Nonterminal symbol
        self.prod = prod        # Production symbol list
        self.dot = dot          # Dot position
        self.la = la            # Lookahead symbol

    def __repr__(self):
        rhs = self.prod[:]
        rhs.insert(self.dot, '.')
        rhs = ' '.join(rhs)
        return 'item(%s -> %s, %s)' % (self.nt, rhs, self.la)

    def __eq__(self, other):
        return other and self.nt == other.nt\
                     and self.prod == other.prod\
                     and self.dot == other.dot\
                     and self.la == other.la

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.nt, str(self.prod), self.dot, self.la))

    # Return whether the item is completed (i.e., the dot is at the end).
    def completed(self):
        return self.dot >= len(self.prod)

    # Return the next symbol (i.e., the one on the dot) or None.
    def next(self):
        return None if self.completed() else self.prod[self.dot]

    # Return a copy of the item with the dot advanced and the specified
    # lookahead symbol (defaults to the current lookahead symbol). If the item
    # is already completed, raise an error. Note: The "copy" will still point to
    # the same nt and prod (since these shouldn't ever change). Only the dot and
    # la will be updated.
    def advance(self, la=None):
        if self.completed():
            raise ValueError('cannot advance completed item %s.' % str(self))
        return item(self.nt, self.prod, self.dot+1, la if la else self.la)

# Compute the first and nullable properties for each symbol in the given
# grammar.
def compute_props(grammar):

    # Initialize all terminal first sets to contain just that terminal
    for prods in grammar.rules.values():
        for prod in prods:
            for sym in prod:
                if not grammar.rules.get(sym):
                    grammar.first[sym] = set([sym])

    changed = True

    # Compute nonterminal first sets iteratively until fixpoint
    while changed:
        # print('changed')

        changed = False

        for (nt, prods) in grammar.rules.items():
            # print(nt)
            for prod in prods:
                # print(prod)

                # Set nullable
                if not prod or all(grammar.nullable[sym] for sym in prod):
                    old_val = grammar.nullable[nt]
                    grammar.nullable[nt] = True
                    changed = changed or not old_val

                # Extend first sets
                for i in range(len(prod)):

                    if i == 0 or all(grammar.nullable[sym] for sym in prod[:i]):

                        # print('%s: %s' % (nt, grammar.first[nt]))
                        # print('%s: %s' % (prod[i], grammar.first[prod[i]]))
                        old_len = len(grammar.first[nt])
                        grammar.first[nt] |= grammar.first[prod[i]]
                        # print('%s: %s' % (nt, grammar.first[nt]))
                        changed = changed or old_len != len(grammar.first[nt])

    # Compute props for entire production rule
    for prods in grammar.rules.values():
        for prod in prods:
            grammar.first[str(prod)] = first(grammar, prod)
            grammar.nullable[str(prod)] = nullable(grammar, prod)

# Return the first set for a given rhs of a production.
def first(grammar, prod):
    res = set()
    for sym in prod:
        res |= grammar.first[sym]
        if not grammar.nullable[sym]: break
    return res

# Return whether the given rhs of a production is nullable.
def nullable(grammar, prod):
    return all(grammar.nullable[sym] for sym in prod)

# Return the closure set given a set of items.
def closure(grammar, items):

    changed = True

    while changed:

        changed = False

        for it in list(items):

            for prod in grammar.rules[it.next()]:

                first_set = grammar.first[str(prod)]

                if grammar.nullable[str(prod)]:
                    first_set.add(it.la)

                for sym in first_set:

                    old_len = len(items)
                    items.add(item(it.next(), prod, 0, sym))
                    changed = changed or len(items) != old_len

    return items

# Return the goto set of items given a state and symbol.
def goto(grammar, state, sym):
    j = set(it.advance() for it in state if it.next() == sym)
    return closure(grammar, j)

# Return the state or an equivalent state in the given state list and add the
# state if it is not in the state list. Note: This function assumes that states
# are disjoint.
def add_state(states, new):
    # equiv = [state for state in states if next(iter(new)) in state] # <- !!!!!! probably the culprit
    for state in states:
        if state == new:
            return state
    # exit(1)
    states.append(new)
    return new

# Return the list of states and the set of (goto and shift) edges between states
# given a grammar and start state.
def generate_graph(grammar, start):

    states = [start]
    edges = set()
    changed = True
    checked = defaultdict(lambda: defaultdict(bool))

    # Generate states and goto edges
    while changed:

        changed = False

        for (i, state) in enumerate(states):

            for sym in set(it.next() for it in state if it.next() and not checked[i][it.next()]):

                checked[i][sym] = True
                new_state = goto(grammar, state, sym)
                old_state_len = len(states)
                new_state = add_state(states, new_state)
                j = states.index(new_state)
                old_edge_len = len(edges)
                edges.add((i, sym, j))
                changed = changed or (len(states), len(edges)) != (old_state_len, old_edge_len)

    return (states, edges)

# Return the parse table given a grammar and state graph.
def generate_table(grammar, states, edges):

    table = [defaultdict(list) for state in states]

    # Fill in goto and shift actions
    for edge in edges:

        i, x, j = edge

        if grammar.rules[x]:                        # Nonterminal -> goto
            table[i][x].append(('goto', j))
        else:                                       # Terminal -> shift
            if x == grammar.end_sym:
                table[i][x].append(('accept'))
            else:
                table[i][x].append(('shift', j))

    # Fill in reduce actions
    for (i, state) in enumerate(states):

        for it in (it for it in state if it.prod and it.la):

            if it.nt == grammar.start_sym and it.next() == grammar.end_sym and it.la == grammar.end_sym:
                table[i][it.la].append(('accept'))

            elif it.completed():                    # Reduce
                table[i][it.la].append(('reduce', it.nt, it.prod))

    return table

# Return a generated LR(1) parse table (dict<state number, dict<lookahead
# symbol, action>>) given a grammar object.
def get_table(grammar):

    # Start item
    start_prod = [grammar.root, grammar.end_sym]
    start_item = item(grammar.start_sym, start_prod, 0, None)
    start_set = set([start_item])

    # Add auxiliary root production rule
    grammar.rules[grammar.start_sym] = [start_prod]

    # Compute first set and nullability for each symbol in the grammar
    compute_props(grammar)

    # print(grammar.first)
    # print(grammar.nullable)

    # Initialize the graph
    start_state = closure(grammar, start_set)

    # print(start_state)

    # Construct rest of states
    states, edges = generate_graph(grammar, start_state)

    # for (i, state) in enumerate(states):
    #     print('state %s:' % i)
    #     print(state)
    # print(edges)

    # Construct table
    conflicts = []
    table = generate_table(grammar, states, edges)
    for (i, state) in enumerate(table):
        print('State %d:' % i)
        print('  Items:')
        for it in states[i]:
            print('    %s' % it)
        print('  Actions:')
        for (la, action) in state.items():
            print('    %s%s->  %s%s' % (la, ' '*(9-len(la)), action, '\t[CONFLICT]' if len(action) > 1 else ''))
            if len(action) > 1:
                conflicts.append('State %s: %s -> %s' % (i, la, action))
        input()

    print('Conflicts:')
    for conflict in conflicts:
        print(conflict)


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

# Create a parser Python program file at the given path, based on the given spec
# string.
def parse_file(path, spec):
    grammar = parse_spec(spec)
    tlist = ['\'%s\'' % t for t in grammar.tlist]
    clist = ['\'%s\'' % c for c in grammar.clist]
    rule_lst = []

    # print(grammar.prec)
    # print(grammar.assoc)

    table = get_table(grammar)

    # # Convert rules dict to strings
    # for (lhs, rhs) in rules.items():
    #     prods = []
    #     for lst in rhs:
    #         prods.append('[{0}]'.format(','.join('\'{0}\''.format(t) for t in lst)))
    #     rule = '\'{0}\':[{1}]'.format(lhs, ','.join(prods))
    #     rule_lst.append(rule)

    # # Write file
    # f = open(path, 'w')
    # f.write(parseprog.format(root, ','.join(tlist), ','.join(clist), ','.join(rule_lst)))
    # f.close()

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