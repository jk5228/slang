# An LR(1) parser generated by parsegen.py. This file is automatically
# generated. Do not edit.

import pickle
from os import path
from collections import defaultdict
from . import node, action

# Return a parse table usable in a parser given a table object loaded from a
# parse table dump.
def usable(dump_table):
    table = [defaultdict(lambda: None) for state in dump_table]

    for (i, state) in enumerate(dump_table):

        for (sym, act_tup) in state:
            act = None
            if act_tup[0] == 'SHIFT':
                act = action.SHIFT(*act_tup[1:])
            elif act_tup[0] == 'GOTO':
                act = action.GOTO(*act_tup[1:])
            elif act_tup[0] == 'REDUCE':
                act = action.REDUCE(*act_tup[1:])
            else:
                act = action.ACCEPT()
            table[i][sym] = act

    return table

end_sym = 'END_SYM'
tlist = ['num', 'str', 'id', '..', '...', ':', '->', '+', '-', '*', '/', '%', '^', '!', '&&', '||', '==', '<=', '>=', '<', '>', 'break']
clist = ['stm*', 'stm', 'id*', 'exp*']
table = usable(pickle.load(open(path.dirname(__file__)+'/parse_table.dump', 'rb')))

# Return the abstract syntax tree given a concrete syntax tree. If the root of
# the concrete syntax tree is contracted, then the resulting abstract syntax
# tree will be a list of trees.
def ast(cst):
    def rec(cst):
        if type(cst) == node.nonterminal:       # Nonterminal
            children = []
            for child in cst.children:
                children.extend(rec(child))
            if cst.sym in clist:                # Contract nonterminal
                return children
            else:                               # Keep nonterminal
                cst.children = children
                return [cst]
        elif cst.sym in tlist:                  # Keep terminal
            return [cst]
        else:                                   # Discard terminal
            return []

    res = rec(cst)
    if len(res) > 1: return res                 # top-level contraction
    return res[0]

# Return an abstract syntax tree given a lexer object.
def parse(lexer):

    state_stk = [0]
    stack = []
    prev = None
    token = None
    act = None

    while True:

        # print('stack: %s' % str(stack))
        # print('state stack: %s' % str(state_stk))

        # Get next token and action
        if not token:
            try:
                token = lexer.next()
                act = table[state_stk[-1]][token.label]
            except StopIteration:
                token = end_sym
                act = table[state_stk[-1]][end_sym]
        elif type(token) != str:
            act = table[state_stk[-1]][token.label]
        else:
            act = table[state_stk[-1]][end_sym]

        # print('token: %s' % str(token))
        # print('action: %s' % act)

        if not act:                         # ERROR

            val = None

            if type(token) == str:
                token = prev
                val = 'EOF'
            else:
                val = token.value

            frag = lexer.excerpt(token.start_line, 3, lexer.prog_str)
            raise SyntaxError('line %d: unexpected token "%s".\n%s'\
                % (token.start_line, val, frag))

        elif type(act) == action.SHIFT:     # SHIFT

            t = node.terminal(token.label, token.value, token.start_line, token.end_line)
            # print('t.sym: %s' % t.sym)
            # print('t.value: %s' % t.value)
            stack.append(t)
            state_stk.append(act.state_num)
            prev = token
            token = None

        elif type(act) == action.REDUCE:    # REDUCE

            children = stack[len(stack)-act.pop_num:]
            for i in range(act.pop_num):
                stack.pop()
                state_stk.pop()
            if len(children):
                start = children[0].start_line
                for child in reversed(children):
                    end = child.end_line
                    if end != None: break
            else:
                start = None
                end = None
            t = node.nonterminal(act.nt, children, start, end)
            # print('t.sym: %s' % t.sym)
            # print('t.children: %s' % t.children)
            stack.append(t)
            act = table[state_stk[-1]][act.nt]
            state_stk.append(act.state_num)
            # print('action: %s' % act)

        elif type(act) == action.ACCEPT:    # ACCEPT

            return ast(stack[-1])