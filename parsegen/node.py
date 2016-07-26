# An abstract syntax tree node.

class node(object):
    
    def __init__(self, nt, children):
        self.nt = nt
        self.children = children

    def __repr__(self):
        return 'node({0} -> {1})'.format(self.nt, str(self.children))