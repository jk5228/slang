# The action classes used by parsegen.py.

# An LR(1) parse table action.
class action(object):
    pass

# An accept action.
class ACCEPT(action):
    
    def __repr__(self):
        return 'ACCEPT'

# A goto action.
class GOTO(action):
    
    def __init__(self, state_num, sym):
        self.state_num = state_num
        self.sym = sym

    def __repr__(self):
        return 'GOTO %d\t[ %s ]' % (self.state_num, self.sym)

# A shift action.
class SHIFT(action):
    
    def __init__(self, state_num, sym):
        self.state_num = state_num
        self.sym = sym

    def __repr__(self):
        return 'SHIFT %d\t[ %s ]' % (self.state_num, self.sym)

# A reduce action.
class REDUCE(action):
    
    def __init__(self, sym, nt, prod):
        self.sym = sym
        self.nt = nt
        self.prod = prod
        self.pop_num = len(prod)

    def __repr__(self):
        return 'REDUCE %d\t[ %s -> %s ]' % (self.pop_num, self.nt, ' '.join(self.prod))