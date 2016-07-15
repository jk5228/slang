# A parser generated from parsegen.py.

from collections import defaultdict, OrderedDict
root = 'prog'
rules = {'funExp':[['id','(','exp*',')']],'forBlk':[['for','(','id','in','exp',')','{','stm*','}']],'assign':[['id','=','exp'],['arrAcc','=','exp']],'line':[['funExp'],['assign'],['break'],['return'],['return','exp']],'exp*':[[],['exp+']],'funBlk':[['def','id','(','id*',')','{','stm*','}']],'arrExp':[['{','exp*','}']],'lOp1':[['!']],'whileBlk':[['while','(','exp',')','{','stm*','}']],'stm':[['line',';'],['block']],'lOp2':[['&&'],['||'],['=='],['>'],['<']],'arrAcc':[['id','[','exp',']']],'prog':[['stm*']],'aOp2':[['+'],['-'],['*'],['/']],'stm*':[[],['stm+']],'logExp':[['lOp1','exp'],['(','exp',')','l2op','exp']],'block':[['funBlk'],['ifBlk'],['whileBlk'],['forBlk']],'exp+':[['exp'],['exp',',','exp+']],'exp':[['(','exp',')'],['prim'],['arrAcc'],['funExp'],['arrExp'],['arithExp'],['logExp']],'ifBlk':[['if','(','exp',')','{','stm*','}','else','{','stm*','}']],'arithExp':[['(','exp',')','aOp2','exp']],'prim':[['num'],['str'],['id']],'id+':[['id'],['id',',','id+']],'id*':[[],['id+']],'stm+':[['stm'],['stm','stm*']]}

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
        return '%s:%s:%s:%s'.format(self.nt, self.prod, self.origin, self.dot)

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
def complete(rules, cols, col, e):
    # print(col.values())
    for cand in cols[e.origin].values():
        # print('CAND: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
        # print(cand.id())
        if not cand.completed() and rules[cand.next()] and cand.next() == e.nt:
            # print('%s completing %s' % (e.id(), cand.id()))
            # print('cand %s children: %s' % (cand.id(), [e.id() for e in cand.children]))
            # print('comp %s children: %s' % (e.id(), [e.id() for e in e.children]))
            comp_ent = entry('comp', cand.nt, cand.prod, cand.origin, cand.dot+1)
            comp_ent.children = cand.children[:] # Pass on children
            comp_ent.children.append(e)         # Add child
            add(col, comp_ent)
            # print('COMP: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))

# Return the parse tree (list) for the given root entry of an Earley parse.
def get_tree(rules, tokens, root):
    if type(root) != entry: return root
    rhs = []
    children = iter(root.children)
    print(root.children)
    # print('%s: %s' % (root.nt, [e.id() for e in root.children]))
    for child in root.children:
        rhs.append(get_tree(rules, tokens, child))
    return (root.nt, rhs)

# Pretty print the parse tree, with subsequent levels indented to show nesting.
def print_tree(root):
    def rec(root, level):
        if not root: return
        lhs, rhs = root
        print('%s%s' % ('| '*level, lhs), end='')
        if type(rhs) == list:
            print()
            for term in rhs:
                rec(term, level+1)
        else:
            print(' : %s' % rhs)
    rec(root, 0)

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
            raise SyntaxError('unexpected token "%s"' % tokens[i][1])       # TODO: line number for errors

        # if i > 30: return
        l, r = tokens[i] if i < len(tokens) else ('','')
        # print('=== col %d : %s %s ===' % (i, l, r))

        for e in col.values():
            # print('entry: [%s] %s -> %s (%d, %d)' % (e.type, e.nt, e.prod, e.origin, e.dot))
            # print('children: %s' % [c.id() for c in e.children])
            if not e.completed():       # Uncompleted
                if rules[e.next()]:     # Nonterminal
                    predict(rules, i, col, e)
                else:                   # Terminal
                    # print('scan')
                    if i+1 < len(cols):
                        scan(tokens[i], i+1, cols[i+1], e)
            else:                       # Completed
                # print('comp')
                complete(rules, cols, col, e)

    # Verify that there was a valid parse
    roots = [e for e in cols[-1].values() if e.nt == root and e.origin == 0 and e.completed()]
    if len(roots) != 1:                 # TODO: b/c of OrderedDict is a set, we'll never get multiple valid parses in last col
        raise SyntaxError('expected 1 valid parse but got ' + str(len(roots)))
        for rt in roots:              # Print valid parse trees for tokens
            print_tree(get_tree(rules, tokens, rt))

    # Return the valid parse tree
    return get_tree(rules, tokens, roots[0])