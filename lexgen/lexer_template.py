# A lexer generated by lexgen.py. This file is automatically generated.
# Do not edit.

import re, tok

ws = re.compile('\s+')
triples = [{0}]


# Return the number of newlines in the match object.
def countlines(match):
    return match.group(0).count('\n')

# A lexer object.
class lexer(object):

    def __init__(self, prog_file=None):
        self.prog_file = prog_file      # The program file
        self.prog_str = self.prog_file.read() if self.prog_file else None
        self.tokens = None

    # Set the program file.
    def set_file(self, prog_file):
        self.prog_file = prog_file
        self.prog_str = self.prog_file.read()

    # Return the next token. Raises an exception if there is no set
    # program file.
    def next(self):
        if not self.prog_file: raise Exception('no program file set.')
        if not self.tokens: self.tokens = self.lex(self.prog_str)
        return next(self.tokens)

    # Reset the token generator. Raises an exception if there is no set
    # program file.
    def reset(self):
        if not self.prog_file: raise Exception('no program file set.')
        self.tokens = self.lex(self.prog_str)

    # Return a string containing the section of up to k lines surrounding and
    # including line n, given a program string.
    def vicinity(self, n, k, string):
        n = n-1                     # Switch back to zero-indexing
        lines = string.split('\n')
        lo = max(n - k//2, 0)
        hi = min(n + k//2, len(lines)-1)
        print(lo)
        print(hi)
        width = len(str(hi))
        res = []
        for (i, line) in enumerate(lines[lo:hi+1]):
            num = str(i+1+lo).rjust(width, ' ')
            res.append(num + ': ' + line)
        return '\n'.join(res)

    # Generate tokens given a program string.
    def lex(self, prog_str):
        linecount = 1

        while len(prog_str):

            match = None

            # Match token patterns
            for (label, typ, pattern) in triples:

                match = re.match(pattern, prog_str)

                if match:

                    if typ == '<': pass
                    elif match.groups('val'):
                        val = match.group('val')
                        end = val.count('\n')
                        yield tok.token(label, val, linecount, linecount+end)
                    else:
                        val = prog_str[:match.end(0)]
                        end = val.count('\n')
                        yield tok.token(label, val, linecount, linecount+end)
                    linecount += countlines(match)
                    prog_str = prog_str[match.end(0):]
                    # print('linecount: %s' % linecount)
                    break

            # No token patterns matched
            if not match:
                linefrag = ''
                try:
                    linefrag = prog_str[:prog_str.index('\n')]
                except ValueError:
                    linefrag = prog_str
                print(orig_str)
                raise SyntaxError('line %d: unexpected sequence "%s".\n%s'\
                    % (linecount, linefrag, self.vicinity(linecount, 3, self.prog_str)))