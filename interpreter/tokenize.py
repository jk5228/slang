# A tokenizer generated from tokgen.py.

import re
from itertools import chain

ws = re.compile('\s+')
pairs = [('and', re.compile(re.escape('&&'))), ('gt', re.compile(re.escape('>'))), ('rbrace', re.compile(re.escape('['))), ('scolon', re.compile(re.escape(';'))), ('comma', re.compile(re.escape(','))), ('in', re.compile(re.escape('in'))), ('star', re.compile(re.escape('*'))), ('if', re.compile(re.escape('if'))), ('for', re.compile(re.escape('for'))), ('lt', re.compile(re.escape('<'))), ('slash', re.compile(re.escape('/'))), ('assign', re.compile(re.escape('='))), ('return', re.compile(re.escape('return'))), ('equals', re.compile(re.escape('=='))), ('lbracket', re.compile(re.escape('}'))), ('lparen', re.compile(re.escape(')'))), ('not', re.compile(re.escape('!'))), ('lbrace', re.compile(re.escape(']'))), ('rparen', re.compile(re.escape('('))), ('minus', re.compile(re.escape('-'))), ('while', re.compile(re.escape('while'))), ('plus', re.compile(re.escape('+'))), ('rbracket', re.compile(re.escape('{'))), ('or', re.compile(re.escape('||'))), ('def', re.compile(re.escape('def'))), ('num', re.compile('-?\d+')), ('id', re.compile('[A-Za-z]+')), ('str', re.compile('"[^"]*"'))]

# Return a list of label-token pairs given a program string.
def tokfun(prog):
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
            raise SyntaxError('line %%d: unexpected sequence "%%s"'
                              %% (linecount, linefrag))

    return tokens