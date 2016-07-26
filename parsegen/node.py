# Syntax tree terminal and nonterminal nodes.

# A terminal node.
class terminal(object):

    def __init__(self, sym, value):
        self.sym = sym
        self.value = value

    def __repr__(self):
        return 'terminal({0} -> {1})'.format(self.sym, str(self.value))

# A nonterminal node.
class nonterminal(object):
    
    def __init__(self, sym, children):
        self.sym = sym
        self.children = children

    def __repr__(self):
        return 'nonterminal({0} -> {1})'.format(self.sym, str(self.children))