# The Slang executor                                        Jason Kim, 7/15/2016
# The Slang executor takes a list of Slang statements and executes them.

import env

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

# Slang core

# Return the nearest value assigned to the variable name. If the name is
# undefined, throw an error.
def find(envs, name):
    for env in envs[::-1]:
        if name in env:
            return env[name]
    raise NameError('name "%s" is not defined.' % str(name))

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

# Return the unwrapped value in the given object.
def unwrap(obj):
    return obj.value

# Return the evaluation of the given function on its arguments.
def call(envs, fname, args):
    print('-> call')
    f = find(envs, fname)
    # print('calling ' + str(f))
    if type(f) == built_in_func:
        # print('built-in')
        # print('args ' + str(args))
        return f.value(*[unwrap(arg) for arg in args])
    elif type(f) != func:
        raise TypeError('value %s : %s is not a function.' % (fname, type(f)))
    if len(f.args) != len(args):
        raise SyntaxError('function %s expected %d arguments but got %s.' % (fname, len(f.args), len(args)))
    fenv = { farg: arg for (farg, arg) in zip(f.args, args) }
    # print(fenv)
    envs.append(fenv)
    res = execute(envs, f.body)
    envs.pop()
    return res.res

# # Return the value of the expression.
# def evaluate(envs, exp):
#     print('eval')
#     exit(0)
#     # print('evaluating expression ' + str(exp))
#     # print(str(type(exp)))
#     if type(exp) != list:                   # Primitive
#         if type(exp) in [number, string, array]:
#             return exp
#         else:
#             return find(envs, exp)
#     elif len(exp) == 1:                     # Primitive
#         if type(exp[0]) in [number, string, array]:
#             return exp[0]
#         else:
#             return find(envs, exp[0])
#     elif exp[0] == '!':
#         return number(int(bool(unwrap(evaluate(envs, exp[1])))))
#     elif len(exp) == 2:                     # Function or array access expression
#         value = find(envs, exp[0])
#         if type(value) == array:
#             index = unwrap(evaluate(envs, exp[1]))
#             if index < 0 or index >= len(value.value):
#                 raise IndexError('Cannot access index %d of array "%s".' % (index, exp[0]))
#             return value.value[index]
#         else:
#             args = [evaluate(envs, arg) for arg in exp[1]]
#             # print('calling ' + str(exp[0]) + ' on args ' + str(args))
#             return call(envs, value, args)
#     else:
#         if exp[0] == '==':
#             return number(int(unwrap(evaluate(envs, exp[1])) == unwrap(evaluate(envs, exp[2]))))
#         elif exp[0] == '&&':
#             return number(int(unwrap(evaluate(envs, exp[1])) and unwrap(evaluate(envs, exp[2]))))
#         elif exp[0] == '||':
#             return number(int(unwrap(evaluate(envs, exp[1])) or unwrap(evaluate(envs, exp[2]))))
#         elif exp[0] in '><+':
#             val1 = evaluate(envs, exp[1])
#             val2 = evaluate(envs, exp[2])
#             if exp[0] != '+' and type(val1) != type(val2) or type(val1) not in [number, string]:
#                 raise TypeError('Values ' + str(val1) + ' and ' + str(val2) + ' are not comparable.')
#             if exp[0] == '>':
#                 return number(int(unwrap(val1) > unwrap(val2)))
#             elif exp[0] == '<':
#                 return number(int(unwrap(val1) < unwrap(val2)))
#             elif type(val1) == number:
#                 return number(unwrap(val1) + unwrap(val2))
#             else:
#                 return string(str(unwrap(val1)) + str(unwrap(val2)))
#         elif exp[0] in '-*/':
#             val1 = evaluate(envs, exp[1])
#             val2 = evaluate(envs, exp[2])
#             if type(val1) != type(val2) or type(val1) != number:
#                 raise TypeError('Values ' + str(val1) + ' and ' + str(val2) + ' invalid for arithmetic operator.')
#             if exp[0] == '-':
#                 return number(unwrap(val1) - unwrap(val2))
#             elif exp[0] == '*':
#                 return number(unwrap(val1) * unwrap(val2))
#             elif exp[0] == '/' and unwrap(val2) != 0:
#                 return number(unwrap(val1) / unwrap(val2))
#             else:
#                 raise ArithmeticError('Cannot divide by 0.')
#         else:
#             raise SyntaxError('Cannot evaluate expression "' + str(exp) + '".')

# Return the root token of the parse tree.
def token(tree):
    return tree[0]

# Return if the root of the tree is the given token.
def match(tree, tok):
    return token(tree) == tok

# Return the leftmost subtree of the parse tree.
def sub(tree):
    if type(tree[1]) == list:
        return tree[1][0]
    return tree[1]

# Return the list of children of the given tree.
def subs(tree):
    if type(tree[1]) == list:
        return tree[1]
    return [tree[1]]

# Return the number (int or float) in the given string.
def get_num(num):
    try:
        return int(num)
    except ValueError:
        return float(num)

# Return the value of the expression.
def evaluate(envs, exp):
    print('evaluating expression ' + str(exp))
    exp = sub(exp)
    if match(exp, 'exp'):                   # Subexpression
        print('-> exp')
        return evaluate(envs, exp)
    elif match(exp, 'prim'):                # Primitive
        print('-> prim')
        prim = sub(exp)
        if match(prim, 'num'):              # Number
            return number(get_num(sub(prim)))
        elif match(prim, 'str'):            # String
            return string(sub(prim))
        else:                               # Variable
            return find(envs, sub(prim))
    elif match(exp, 'assign'):              # Assignment
        print('-> assign')
        if token(sub(exp)) == 'id':
            print('-> id')
            var = sub(sub(exp))
            val = evaluate(envs, subs(exp)[1])
            bind(envs, var, val)
            return val
        else:
            print('-> arrAcc')
            arr = unwrap(find(envs, sub(sub(sub(exp)))))
            ind = unwrap(evaluate(envs, subs(sub(exp))[1]))
            val = evaluate(envs, subs(exp)[1])
            arr[ind] = val
            return val
    elif match(exp, 'arrAcc'):              # Array access
        print('-> arrAcc')
        arr = unwrap(find(envs, sub(sub(exp))))
        if type(arr) != list:
            raise TypeError('cannot index into %s : %s.' % (sub(sub(exp)), type(arr)))
        ind = unwrap(evaluate(envs, subs(exp)[1]))
        if ind < 0 or ind >= len(arr):
            raise IndexError('cannot access index %d of array "%s".' % (ind, sub(sub(exp))))
        return arr[ind]
    elif match(exp, 'funExp'):              # Function call
        print('-> funExp')
        fname = sub(sub(exp))
        args = [evaluate(envs, arg) for arg in subs(subs(exp)[1])]
        return call(envs, fname, args)
    elif match(exp, 'arrExp'):              # Array expression
        print('-> arrExp')
        expLst = subs(sub(exp))
        exps = [evaluate(envs, exp) for exp in expLst]
        return array(exps)
    elif match(exp, 'arithExp'):            # Arithmetic expression
        print('-> arithExp')
        terms = subs(exp)
        left = evaluate(envs, terms[0])
        op = sub(terms[1])
        right = evaluate(envs, terms[2])
        print(right)
        if match(op, '+'):                  # Add
            print('-> +')
            if string in (type(left), type(right)):
                return string(str(unwrap(left)) + str(unwrap(right)))
            elif type(left) == number and type(right) == number:
                return number(unwrap(left) + unwrap(right))
            elif type(left) == array and type(right) == array:
                return array(unwrap(left) + unwrap(right))
            else:
                raise TypeError('cannot perform operation %s + %s' % (type(left), type(right)))
        elif match(op, '-'):                # Subtract
            print('-> -')
            if type(left) == number and type(right) == number:
                return number(unwrap(left) - unwrap(right))
            else:
                raise TypeError('cannot perform operation %s - %s' % (type(left), type(right)))
        elif match(op, '/'):                # Divide
            print('-> /')
            if type(left) == number and type(right) == number:
                if unwrap(right) != 0:
                    return number(unwrap(left) / unwrap(right))
                else:
                    raise ArithmeticError('cannot divide by 0.')
            else:
                raise TypeError('cannot perform operation %s / %s' % (type(left), type(right)))
        elif match(op, '*'):                # Multiply
            print('-> *')
            if type(left) == number and type(right) == number:
                return number(unwrap(left) * unwrap(right))
            else:
                raise TypeError('cannot perform operation %s * %s' % (type(left), type(right)))
        else:                               # Modulo
            print('-> %')
            if type(left) == number and type(right) == number:
                return number(unwrap(left) % unwrap(right))
            else:
                raise TypeError('cannot perform operation %s %% %s' % (type(left), type(right)))
    else:                                   # Logical expression
        print('-> logExp')



    return
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

# A result object.
class result(object):
    def __init__(self, res, ret, brk):
        self.res = res
        self.ret = ret
        self.brk = brk

    def __repr__(self):
        return 'result(res=%s, ret=%s, brk=%s)' %\
                (self.res, self.ret, self.brk)

    @staticmethod
    def res(res):
        return result(res, False, False)

    @staticmethod
    def ret(res):
        return result(res, True, False)

    @staticmethod
    def brk(res):
        return result(res, False, True)

# Execute a list of statements.
def execute_stms(envs, iscall, isloop, stms):
    print('execute: %s' % (stms))
    res = result.res(number(0))
    for stm in stms:
        if not len(stm): continue
        elif match(stm, 'line'):            # Line
            stm = sub(stm)
            if match(stm, 'retStm'):        # Return
                print('return')
                if not iscall: raise SyntaxError('cannot return outside of a function call.')
                elif stm[1]:   return result.ret(evaluate(stm[1]))
                else:          return result.ret(number(0))
            elif match(stm, 'break'):       # Break
                print('break')
                if not isloop: raise SyntaxError('cannot break outside of a loop.')
                else:          return result.brk(number(0))
            elif match(stm, 'exp'):         # Expression
                print('exp')
                res = evaluate(envs, stm)
        else:                               # Block
            stm = sub(stm)
            if match(stm, 'funBlk'):        # Function declaration
                print('funBlk')
                pass
            elif match(stm, 'ifBlk'):       # If-else block
                print('ifBlk')
                pass
            elif match(stm, 'whileBlk'):    # While block
                print('whileBlk')
                pass
            else:                           # For block
                print('forBlk')
                pass
    return result.res(res)

# Execute the program.
def execute(envs, stms):
    return execute_stms(envs, False, False, stms)

# # Execute the statements in the given list.
# def execute(envs, stms):
#     res = 0
#     for stm in stms:
#         if not len(stm):
#             continue
#         elif stm[0] == 'return':        # Return
#             return number(0) if len(stm) == 1 else evaluate(envs, stm[1])
#         elif stm[0] == '=':             # Assignment
#             if type(stm[1]) != list:
#                 res = bind(envs, stm[1], evaluate(envs, stm[2]))
#             else:
#                 arr = find(envs, stm[1][0])
#                 index = unwrap(evaluate(envs, stm[1][1][0]))
#                 if type(arr) != array:
#                     raise TypeError('Cannot index into "%s" of type %s.' % (stm[1][0], type(arr)))
#                 if index < 0 or index >= len(arr.value):
#                     raise IndexError('Cannot access index %d of array "%s".' % (index, stm[1][0]))
#                 res = arr.value[index] = evaluate(envs, stm[2])
#         elif stm[0] == 'if':            # If
#             if bool(unwrap(evaluate(envs, stm[1]))):
#                 res = execute(envs, stm[2])
#             else:
#                 res = execute(envs, stm[3])
#         elif stm[0] == 'for':           # For
#             index = stm[1][0]
#             values = evaluate(envs, stm[1][2])
#             envs.append(dict())
#             for i in values.value:
#                 envs[-1][index] = i
#                 res = execute(envs, stm[2])
#             envs.pop()
#         elif stm[0] == 'while':         # While
#             while bool(unwrap(evaluate(envs, stm[1]))):
#                 execute(envs, stm[2])
#         elif stm[0] == 'def':           # Function definition
#             res = bind(envs, stm[1], func(stm[1], stm[2], stm[3]))
#         else:                           # Function
#             res = evaluate(envs, stm)
#     return res