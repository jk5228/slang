# Syntax tree terminal and nonterminal nodes.

# A terminal node.
class terminal(object):

    def __init__(self, sym, value, start_line, end_line):
        self.sym = sym
        self.value = value
        self.start_line = start_line
        self.end_line = end_line

    def __repr__(self):
        return '{0} = {1} ({2}-{3})'.format(self.sym, self.value, self.start_line, self.end_line)

# A nonterminal node.
class nonterminal(object):
    
    def __init__(self, sym, children, start_line, end_line):
        self.sym = sym
        self.children = children
        self.start_line = start_line
        self.end_line = end_line

    def __repr__(self):
        children = ', '.join(str(child) for child in self.children)
        return '{0} : [ {1} ]({2}-{3})'.format(self.sym, children, self.start_line, self.end_line)

# Pretty print the tree.
def print_tree(tree):
    def rec(tree, level):
        if type(tree) == terminal:
            print('%s%s : %s (%s-%s)' % ('| '*level, tree.sym, tree.value,\
                tree.start_line, tree.end_line))
            return
        print('%s%s (%s-%s)' % ('| '*level, tree.sym, tree.start_line,\
            tree.end_line))
        for child in tree.children:
            rec(child, level+1)
    rec(tree, 0)