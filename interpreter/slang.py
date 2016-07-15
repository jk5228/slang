#!/usr/local/bin/python3

# StupidLang (aka Slang)                                     Jason Kim, 7/7/2016
# A stupid Python-interpreted, dynamically-typed, imperative programming
# language, featuring first-class functions, multitype arrays, and horrific
# syntax.

# Language notes:
# - Comments run from # to the end of the line.
# - Only 0, "", and [] are falsy.
# - Functions without a return value return the value of the last statement.
# - Expressions with more than one term must be wrapped by parentheses.
# - For loops work like Python for loops, iterating over an array.
# - Built-in functions include: print, range, size, array.

# TODO:
# - overall goal: make language I would enjoy using and resolves issues in Python
# - better modularize interpreter components
# - write lexer generator that takes token spec as input
# - lexer takes program string and returns list of labelled tokens
# - write parser generator that takes CFG as input (should follow recursive descent parser website algos for normalizing cfg)
# - parser gen: (1) remove cyclic left recursion, (2) factor, (3) substitute, (4) generate rec-des productions
# - rec-des parser takes list of labelled tokens and returns parse tree
# - robust error messages during lexing/parsing
# - optional environment dump at run-time error
# - IR optimizations (contracting a subset of the NTs [allow user to specify this in .syn file])
# - classes
# - lambdas
# - ranges (a la Ruby)
# - built-in, first-class regexes
# - Currying?
# - optional static type-checking?
# - strong typing?
# - "compilation" into condensed format or even bytecode?
# - include other useful built-in functions
# - robust pattern-matching
# - either support or disallow nested functions
# - make parethesization and general syntax more optional/flexible (make arg lists comma-separated, remove parens around program, consider ws?)
# - make operators infix

from collections import deque

# Globals

ws = ' \t\b\n'
digits = '0123456789'
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

global_env = {
    'print': built_in_func(s_print),
    'range': built_in_func(s_range),
    'size': built_in_func(s_size),
    'array': built_in_func(s_array)
}

# Types

# TODO: have every class inherit from object?

class number(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'number(%d)' % (self.value)

class string(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'string("%s")' % (self.value)

class array(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'array(%s)' % (str(self.value))

class func(object):

    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def __repr__(self):
        return 'func(%s)' % (str(self.name))

class built_in_func(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'built_in_func(%s)' % (str(self.value))

# Built-in functions

# Print the given value.
def s_print(value):
    print(str(value))

# Return the array of integers in the interval [lo, hi).
def s_range(lo, hi):
    return array([number(i) for i in range(lo, hi)])

# Return the size of the array.
def s_size(arr):
    return number(len(arr))

# Return an array with the given length, initialized to zeros.
def s_array(n):
    return array([0 for i in range(n)])

# Slang core

# Return the nearest value assigned to the variable name. If the name is
# undefined, throw an error.
def find(envs, name):
    for env in envs[::-1]:
        if name in env:
            return env[name]
    raise NameError('Name "' + str(name) + '" is not defined.')

# Bind the variable name to the given value. If the variable is defined in an
# environment, reassign its value. Otherwise, create a new binding in the local
# environment. Return the value.
def bind(envs, name, value):
    for env in envs[::-1]:
        if name in env:
            env[name] = value
            return
    envs[-1][name] = value
    return value

# Return the unwrapped value in the given primitive.
def unwrap(prim):
    return prim.value

# Return the evaluation of the given function on its arguments.
def call(envs, f, args):
    # print('calling ' + str(f))
    if type(f) == built_in_func:
        # print('built-in')
        # print('args ' + str(args))
        return f.value(*[unwrap(arg) for arg in args])
    elif type(f) != func:
        raise TypeError('Value ' + str(f) + ' is not a function.')
    fenv = { farg: arg for (farg, arg) in zip(f.args, args) }
    # print(fenv)
    envs.append(fenv)
    res = execute(envs, f.body)
    envs.pop()
    return res

# Return a list of tokens for the given program string.
def tokenize(p):
    tokens = []
    i = 0
    while i < len(p):
        c1 = p[i]
        c2 = p[i+1] if i+1 < len(p) else None
        if c1 in ws or c1 == ',':
            i += 1
        elif c1 == '#':
            while p[i] != '\n':
                i += 1
        elif c1 in '()[]}{!><+*/':
            tokens.append(c1)
            i += 1
        elif c1 == '=' and c2 != '=' or c1 == '-' and c2 not in digits:
            tokens.append(c1)
            i += 1
        elif c1+c2 == '&&' or c1+c2 == '||' or c1+c2 == '==':
            tokens.append(c1+c2)
            i += 2
        elif c1 in letters:
            word_start = i
            word_end = i + 1
            while p[word_end] in letters:
                word_end += 1
            tokens.append(p[word_start:word_end])
            i = word_end
        elif c1 == '-' or c1 in digits:
            num_start = i
            num_end = i + 1
            while p[num_end] in digits:
                num_end += 1
            tokens.append(number(int(p[num_start:num_end])))
            i = num_end
        elif c1 == '"':
            str_start = i + 1
            str_end = str_start
            while p[str_end] != '"':
                str_end += 1
            tokens.append(string(p[str_start:str_end]))
            i = str_end + 1
    return tokens

# Return a tree (list) representing the program statements.
def parse(tokens):
    stack = []
    tokens = deque(tokens)
    # print('stack: ' + str(stack))
    # print('tokens: ' + str(tokens))
    while len(tokens) > 0:
        token = tokens.popleft()
        # print('stack: ' + str(stack))
        # print('tokens: ' + str(tokens))
        # print('token: ' + str(token))
        if token == ')':
            lst = deque()
            while stack[-1] != '(':
                item = stack.pop()
                # print('adding ' + str(item) + ' to lst')
                lst.appendleft(item)
            stack.pop()
            stack.append(list(lst))
        elif token == ']':
            lst = deque()
            while stack[-1] != '[':
                item = stack.pop()
                # print('adding ' + str(item) + ' to lst')
                lst.appendleft(item)
            stack.pop()
            stack.append(list(lst))
        elif token == '}':
            lst = deque()
            while stack[-1] != '{':
                item = stack.pop()
                # print('adding ' + str(item) + ' to lst')
                lst.appendleft(item)
            stack.pop()
            stack.append(array(list(lst)))
        else:
            stack.append(token)
    # print(stack)
    return stack.pop()

# Return the value of the expression.
def evaluate(envs, exp):
    # print('evaluating expression ' + str(exp))
    # print(str(type(exp)))
    if type(exp) != list:                   # Primitive
        if type(exp) in [number, string, array]:
            return exp
        else:
            return find(envs, exp)
    elif len(exp) == 1:                     # Primitive
        if type(exp[0]) in [number, string, array]:
            return exp[0]
        else:
            return find(envs, exp[0])
    elif exp[0] == '!':
        return number(int(bool(unwrap(evaluate(envs, exp[1])))))
    elif len(exp) == 2:                     # Function or array access expression
        value = find(envs, exp[0])
        if type(value) == array:
            index = unwrap(evaluate(envs, exp[1]))
            if index < 0 or index >= len(value.value):
                raise IndexError('Cannot access index %d of array "%s".' % (index, exp[0]))
            return value.value[index]
        else:
            args = [evaluate(envs, arg) for arg in exp[1]]
            # print('calling ' + str(exp[0]) + ' on args ' + str(args))
            return call(envs, value, args)
    else:
        if exp[0] == '==':
            return number(int(unwrap(evaluate(envs, exp[1])) == unwrap(evaluate(envs, exp[2]))))
        elif exp[0] == '&&':
            return number(int(unwrap(evaluate(envs, exp[1])) and unwrap(evaluate(envs, exp[2]))))
        elif exp[0] == '||':
            return number(int(unwrap(evaluate(envs, exp[1])) or unwrap(evaluate(envs, exp[2]))))
        elif exp[0] in '><+':
            val1 = evaluate(envs, exp[1])
            val2 = evaluate(envs, exp[2])
            if exp[0] != '+' and type(val1) != type(val2) or type(val1) not in [number, string]:
                raise TypeError('Values ' + str(val1) + ' and ' + str(val2) + ' are not comparable.')
            if exp[0] == '>':
                return number(int(unwrap(val1) > unwrap(val2)))
            elif exp[0] == '<':
                return number(int(unwrap(val1) < unwrap(val2)))
            elif type(val1) == number:
                return number(unwrap(val1) + unwrap(val2))
            else:
                return string(str(unwrap(val1)) + str(unwrap(val2)))
        elif exp[0] in '-*/':
            val1 = evaluate(envs, exp[1])
            val2 = evaluate(envs, exp[2])
            if type(val1) != type(val2) or type(val1) != number:
                raise TypeError('Values ' + str(val1) + ' and ' + str(val2) + ' invalid for arithmetic operator.')
            if exp[0] == '-':
                return number(unwrap(val1) - unwrap(val2))
            elif exp[0] == '*':
                return number(unwrap(val1) * unwrap(val2))
            elif exp[0] == '/' and unwrap(val2) != 0:
                return number(unwrap(val1) / unwrap(val2))
            else:
                raise ArithmeticError('Cannot divide by 0.')
        else:
            raise SyntaxError('Cannot evaluate expression "' + str(exp) + '".')


# Execute the statements in the given list.
def execute(envs, stms):
    res = 0
    for stm in stms:
        if not len(stm):
            continue
        elif stm[0] == 'return':        # Return
            return number(0) if len(stm) == 1 else evaluate(envs, stm[1])
        elif stm[0] == '=':             # Assignment
            if type(stm[1]) != list:
                res = bind(envs, stm[1], evaluate(envs, stm[2]))
            else:
                arr = find(envs, stm[1][0])
                index = unwrap(evaluate(envs, stm[1][1][0]))
                if type(arr) != array:
                    raise TypeError('Cannot index into "%s" of type %s.' % (stm[1][0], type(arr)))
                if index < 0 or index >= len(arr.value):
                    raise IndexError('Cannot access index %d of array "%s".' % (index, stm[1][0]))
                res = arr.value[index] = evaluate(envs, stm[2])
        elif stm[0] == 'if':            # If
            if bool(unwrap(evaluate(envs, stm[1]))):
                res = execute(envs, stm[2])
            else:
                res = execute(envs, stm[3])
        elif stm[0] == 'for':           # For
            index = stm[1][0]
            values = evaluate(envs, stm[1][2])
            envs.append(dict())
            for i in values.value:
                envs[-1][index] = i
                res = execute(envs, stm[2])
            envs.pop()
        elif stm[0] == 'while':         # While
            while bool(unwrap(evaluate(envs, stm[1]))):
                execute(envs, stm[2])
        elif stm[0] == 'def':           # Function definition
            res = bind(envs, stm[1], func(stm[1], stm[2], stm[3]))
        else:                           # Function
            res = evaluate(envs, stm)
    return res

# Interpret the program string.
def interpret(p):
    tokens = tokenize(p)        # Tokenize
    stms = parse(tokens)        # Parse
    envs = [global_env]         # Create environment stack
    # print(stms)
    execute(envs, stms)         # Execute

# Run Slang as a script.
if __name__ == "__main__":
    from sys import argv
    script = open(argv[-1], 'r').read()
    interpret(script)