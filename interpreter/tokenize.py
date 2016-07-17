# A tokenizer generated from tokgen.py.

import re
from itertools import chain

ws = re.compile('\s+')
pairs = [('}', re.compile(re.escape('}'))),('||', re.compile(re.escape('||'))),('{', re.compile(re.escape('{'))),('while', re.compile(re.escape('while'))),('return', re.compile(re.escape('return'))),('in', re.compile(re.escape('in'))),('if', re.compile(re.escape('if'))),('for', re.compile(re.escape('for'))),('else', re.compile(re.escape('else'))),('def', re.compile(re.escape('def'))),('break', re.compile(re.escape('break'))),(']', re.compile(re.escape(']'))),('[', re.compile(re.escape('['))),('>', re.compile(re.escape('>'))),('==', re.compile(re.escape('=='))),('=', re.compile(re.escape('='))),('<', re.compile(re.escape('<'))),(';', re.compile(re.escape(';'))),('/', re.compile(re.escape('/'))),('-', re.compile(re.escape('-'))),(',', re.compile(re.escape(','))),('+', re.compile(re.escape('+'))),('*', re.compile(re.escape('*'))),(')', re.compile(re.escape(')'))),('(', re.compile(re.escape('('))),('&&', re.compile(re.escape('&&'))),('%', re.compile(re.escape('%'))),('!', re.compile(re.escape('!'))),('id', re.compile('[A-Za-z]+')),('str', re.compile('(?:")(?P<val>[^"]*)(?:")')),('num', re.compile('-?\d+'))]

# Return a list of label-token pairs given a program string.
def tokenize(prog):
    tokens = []
    linecount = 1

    while len(prog):
        # print('prog: ' + prog)
        # print('tokens: ' + str(tokens))

        # Ignore whitespace
        match = re.match(ws, prog)
        if match:
            # print('ws ' + str(match))
            prog = prog[match.end(0):]
            linecount += match.group(0).count('\n')
            continue

        # Match token patterns
        for (label, pattern) in pairs:
            match = re.match(pattern, prog)
            if match:
                # print('match ' + str(match))
                if match.groups('val'):
                    tokens.append((label, match.group('val')))
                else:
                    tokens.append((label, prog[:match.end(0)]))
                prog = prog[match.end(0):]
                break

        # No token patterns matched
        if not match:
            linefrag = ''
            try:
                linefrag = prog[:prog.index('\n')]
            except ValueError:
                linefrag = prog
            raise SyntaxError('line %d: unexpected sequence "%s".'
                              % (linecount, linefrag))

    return tokens