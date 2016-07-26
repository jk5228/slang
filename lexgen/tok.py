# A token object.

class token(object):

    def __init__(self, label, value, start_line, end_line):
        self.label = label
        self.value = value
        self.start_line = start_line
        self.end_line = end_line

    def __repr__(self):
        return 'token(\'{0}\', \'{1}\', {2}-{3})'.format(self.label, self.value, self.start_line, self.end_line)