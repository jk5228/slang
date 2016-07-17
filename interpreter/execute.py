# The Slang executor                                        Jason Kim, 7/15/2016
# The Slang executor takes a list of Slang statements and executes them.

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
    raise NameError('name "' + str(name) + '" is not defined.')

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

# Return the value of the expression.
def evaluate(envs, exp):
    print('eval')
    exit(0)
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
            elif match(stm, 'assign'):      # Assignment
                print('assign')
                if token(sub(stm)) == 'id':
                    var = sub(sub(stm))
                    val = evaluate(envs, subs(stm)[1])
                    bind(envs, var, val)
                else:
                    arr = unwrap(find(envs, sub(sub(sub(stm)))))
                    ind = unwrap(evaluate(envs, subs(sub(stm))[1]))
                    val = evaluate(envs, subs(stm)[1])
                    arr[ind] = val
            elif match(stm, 'exp'):         # Expression
                print('exp')
                res = result.res(evaluate(envs, stm))
        elif match(stm, 'block'):           # Block
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
    return res

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