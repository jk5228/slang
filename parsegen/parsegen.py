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
from collections import defaultdict

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

    # Return whether the production is completed.
    def completed(self):
        return self.dot >= len(self.prod)

    # Return the next symbol to process
    def next(self):
        return self.prod[self.dot]

# Add any predicted entries to the given state.
def predict(rules, i, state, e):
    for prod in rules[e.next()]:
        state.append(entry('pred', e.next(), prod, i, 0))

# Add the scanned entry to the given state if the next token is expected.
def scan(tokens, i, state, e):
    if e.next() == tokens[i]:
        scan = entry('scan', e.next(), e.prod, e.origin, i+1)
        scan.children = e.Children          # Pass on children
        state.append(scan)

# Add the completed entry.
def complete(rules, i, state, e):
    for cand in state[e.origin]:
        if rules[cand.next()] and cand.next() == cand.nt:
            comp = entry('comp', cand.nt, cand.prod, cand.origin, i)
            comp.children.append(e)         # Add child
            state.append(comp)

# Return the parse tree (list) for the given root entry of an Earley parse.
def getparse(rules, tokens, root):
    if not root: return
    rhs = []
    children = iter(root.children)
    for (i, term) in enumerate(root.prod):
        if rules[term]:                     # Nonterminal
            rhs.append(getparse(rules, tokens, next(children)))
        else:                               # Terminal
            rhs.append(tokens[i+root.origin])
    return (root.nt, children)


# Return an Earley parser given a grammar. The parser returns the parse tree of
# a given list of tokens or raises an error if there is more than one valid
# parse of the list of tokens.
def parser(root, rules):
    def parsefun(tokens):

        # Initialize chart
        states = [[] for i in range(len(tokens)+1)]
        start = entry('pred', root, rules[root][0], 0, 0)
        states[0].append(start)

        # Fill chart
        for (i, state) in enumerate(states):
            for e in state:
                if not e.completed():       # Uncompleted
                    if rules[e.next()]:     # Nonterminal
                        predict(rules, i, state, e)
                    else:                   # Terminal
                        scan(tokens, i, state, e)
                else:                       # Completed
                    complete(rules, i, state, e)

        # Verify that there was a valid parse
        roots = [e for e in states[-1] if e.nt = root and e.origin = 0 and e.completed()]
        if len(roots) != 1:
            raise SyntaxError('expected 1 valid parse but got ' + str(len(roots)))
            for root in roots:              # Print valid parse trees for tokens
                print(getparse(rules, tokens, root))

        # Return the valid parse tree
        return getparse(rules, tokens, roots[0])

    # Return parser function
    return parsefun

# function EARLEY-PARSE(words, grammar)
#     INIT(words)
#     ADD-TO-SET((γ → •S, 0), S[0])
#     for k ← from 0 to LENGTH(words) do
#         for each state in S[k] do
#             if not FINISHED(state) then
#                 if NEXT-ELEMENT-OF(state) is a nonterminal then
#                     PREDICTOR(state, k, grammar)         // non-terminal
#                 else do
#                     SCANNER(state, k, words)             // terminal
#             else do
#                 COMPLETER(state, k)
#         end
#     end
#     return chart
# 
# procedure PREDICTOR((A → α•Bβ, j), k, grammar)
#     for each (B → γ) in GRAMMAR-RULES-FOR(B, grammar) do
#         ADD-TO-SET((B → •γ, k), S[k])
#     end
# 
# procedure SCANNER((A → α•aβ, j), k, words)
#     if a ⊂ PARTS-OF-SPEECH(words[k]) then
#         ADD-TO-SET((A → αa•β, j), S[k+1])
#     end
# 
# procedure COMPLETER((B → γ•, x), k)
#     for each (A → α•Bβ, j) in S[x] do
#         ADD-TO-SET((A → αB•β, j), S[k])
#     end

        # Each item in a state is a tuple consisting of (type, nt, prod, origin, dot, down, back)
        # On or scan completion, point new item back to (1) the root of its subtree (the
        # scanned/completed item) and (2) the item whose dot advanced to get the
        # new item (the item that has a pointer to other subtrees)

# TODO: You can't normalize the syntax automatically because then the resulting parse tree
# may not make any sense to the interpreter (new nts, new productions, etc.). You have to
# manually normalize the grammar, which may not even be LL(k). If you can't normalize, then
# it's just not LL(k). You'd then need to make an LALR (or stronger) parser generator.

# # Return the index after adding the new nonterminal to it.
# def add(index, nt):
#     index[nt] = len(index)
#     return index

# # Return the syntax after removing cyclic left recursion.
# def remove_cyclic_left_rec(rules):
#     index = {nt: i for (i, nt) in enumerate(rules)}     # Index of nonterminals
#     key = lambda x: index[x]

#     # Must iterate through rules for nonterminals produced in previous iterations, so must be while loop
#     # Must iterate through productions for given nt produced in previous iterations, so must be nested while loop
#     for (i, nt, prods) in ((index[nt], nt, rules[nt]) for nt in sorted(rules, key=key)):
#         print('%d %s %s' % (i, nt, str(prods)))
#         newprods = []
#         for prod in prods:
#             while rules[prod[0]] and index[prod[0]] < i:
#                 # Substitute A_k out of production (only generates new A_i -> ... rules)
#             if prod[0] == nt:
#                 remove_left_rec() # Generates A_i -> ? and A_j -> ? rules for i < j, none left-rec

# # Return the normalized form of the syntax. This is the syntax obtained after
# # removing left recursion, removing unreachable nonterminals, factoring, and
# # substituting.
# def normalize_syntax(rules):

#     # Remove left recursion
#     rules = remove_cyclic_left_rec(rules)

#     # Remove unreachable nonterminals
#     # TODO: this

#     # Factor
#     # TODO: factor

#     # Substitute
#     # TODO: substitute

#     return rules

# # Test code

syn = open('sample.syn', 'r').read()
print(parse_spec(syn))

# # When executed, take filepath fpath and spec filepath sfpath arguments and
# # write a parser program to fpath given the spec at sfpath.
# if __name__ == "__main__":
#     from sys import argv
#     fpath = argv[1]
#     spec = open(argv[2], 'r').read()
#     # TODO: generate parser file