# The Slang executor                                        Jason Kim, 7/15/2016
# The Slang executor takes a list of Slang statements and executes them.

from . import env

# Types

# TODO: have every class inherit from object?
# TODO: move these classes to another module

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
    # print('-> call')
    f = find(envs, fname)
    if type(f) == built_in_func:            # Built-in function
        return f.value(*[unwrap(arg) for arg in args])
    elif type(f) != func:
        raise TypeError('value %s : %s is not a function.' % (fname, type(f)))
    if len(f.args) != len(args):            # Function
        raise SyntaxError('function "%s" expected %d arguments but got %s.' % (fname, len(f.args), len(args)))
    fenv = { farg: arg for (farg, arg) in zip(f.args, args) }
    # print(fenv)
    envs.append(fenv)
    res = execute_stms(envs, True, False, f.body)
    envs.pop()
    return res.res

# Return the root token of the parse tree.
def token(tree):
    return tree.sym

# Return if the root token of the tree is the given token.
def match(tree, tok):
    return tree.sym == tok

# Return the leftmost subtree of the parse tree.
def sub(tree):
    return tree.children[0]

# Return the children of the parse tree.
def subs(tree):
    return tree.children

# Return the number (int or float) in the given string.
def get_num(num):
    try:
        return int(num)
    except ValueError:
        return float(num)

# Return the value of the expression.
def evaluate(envs, exp):

    # print('evaluating expression ' + str(exp))
    exp = sub(exp)

    if match(exp, 'exp'):                   # Subexpression

        # print('-> exp')
        return evaluate(envs, exp)

    elif match(exp, 'prim'):                # Primitive

        # print('-> prim')
        prim = sub(exp)
        if match(prim, 'num'):              # Number
            return number(get_num(prim.value))
        elif match(prim, 'str'):            # String
            return string(prim.value)
        else:                               # Variable
            return find(envs, prim.value)

    elif match(exp, 'assign'):              # Assignment

        # print('-> assign')

        if token(sub(exp)) == 'id':
            # print('-> id')
            var = sub(exp).value
            val = evaluate(envs, subs(exp)[1])
            bind(envs, var, val)
            return val
        else:
            # print('-> arrAcc')
            arr = unwrap(find(envs, sub(sub(exp)).value))
            ind = unwrap(evaluate(envs, subs(sub(exp))[1]))
            val = evaluate(envs, subs(exp)[1])
            arr[ind] = val
            return val

    elif match(exp, 'arrAcc'):              # Array access

        # print('-> arrAcc')
        arr = unwrap(find(envs, sub(exp).value))
        if type(arr) != list:
            raise TypeError('cannot index into %s : %s.' % (sub(exp).value, type(arr)))
        ind = unwrap(evaluate(envs, subs(exp)[1]))
        if ind < 0 or ind >= len(arr):
            raise IndexError('cannot access index %d of array "%s".' % (ind, sub(exp).value))
        return arr[ind]

    elif match(exp, 'funExp'):              # Function call

        # print('-> funExp')
        fname = sub(exp).value
        args = [evaluate(envs, arg) for arg in subs(subs(exp)[1])]
        return call(envs, fname, args)

    elif match(exp, 'arrExp'):              # Array expression

        # print('-> arrExp')
        expLst = subs(sub(exp))
        exps = [evaluate(envs, exp) for exp in expLst]
        return array(exps)

    elif match(exp, 'rngExp'):              # Range expression

        # print('-> rngExp')
        terms = subs(exp)
        lo = evaluate(envs, terms[0])
        # print(lo)
        hi = evaluate(envs, terms[2])
        # print(hi)
        op = terms[1].value
        # print(op)

        if type(lo) == type(hi) and type(lo) == number:
            if op == '..':
                return array([number(i) for i in range(unwrap(lo), unwrap(hi)+1)])
            else:
                return array([number(i) for i in range(unwrap(lo), unwrap(hi))])
        else:
            raise IndexError('cannot have range %s%s%s.' % (type(lo), op, type(hi)))

    elif match(exp, 'arrComp'):             # Array comprehension

        # print('-> arrComp')
        terms = subs(exp)
        # print(terms)
        ind = terms[0].value
        # print(ind)
        arr = unwrap(evaluate(envs, terms[1]))
        # print(arr)
        cond = terms[2]
        # print(cond)
        filter_exp = None
        if len(terms) == 4:
            filter_exp = terms[3]

        if type(arr) != list:
            raise TypeError('cannot index into type %s.' % type(arr))

        res_arr = []
        envs.append({})

        for val in arr:
            envs[-1][ind] = val
            if unwrap(evaluate(envs, cond)):
                if filter_exp:
                    val = evaluate(envs, filter_exp)
                res_arr.append(val)

        envs.pop()
        return array(res_arr)

    elif match(exp, 'arithExp'):            # Arithmetic expression

        # print('-> arithExp')
        terms = subs(exp)
        left = evaluate(envs, terms[0])
        right = evaluate(envs, terms[2])
        op = terms[1]

        if match(op, '+'):                  # Add
            # print('-> +')
            if type(left) == string and type(right) == string:
                return string(unwrap(left) + unwrap(right))
            elif string in (type(left), type(right)) and number in (type(left), type(right)):
                return string(str(unwrap(left)) + str(unwrap(right)))
            elif type(left) == number and type(right) == number:
                return number(unwrap(left) + unwrap(right))
            elif type(left) == array and type(right) == array:
                return array(unwrap(left) + unwrap(right))
            else:
                raise TypeError('cannot perform operation %s + %s' % (type(left), type(right)))
        elif match(op, '-'):                # Subtract
            # print('-> -')
            if type(left) == number and type(right) == number:
                return number(unwrap(left) - unwrap(right))
            else:
                raise TypeError('cannot perform operation %s - %s' % (type(left), type(right)))
        elif match(op, '/'):                # Divide
            # print('-> /')
            if type(left) == number and type(right) == number:
                if unwrap(right) != 0:
                    return number(unwrap(left) / unwrap(right))
                else:
                    raise ArithmeticError('cannot divide by 0.')
            else:
                raise TypeError('cannot perform operation %s / %s' % (type(left), type(right)))
        elif match(op, '*'):                # Multiply
            # print('-> *')
            if type(left) == number and type(right) == number:
                return number(unwrap(left) * unwrap(right))
            else:
                raise TypeError('cannot perform operation %s * %s' % (type(left), type(right)))
        else:                               # Modulo
            # print('-> %')
            if type(left) == number and type(right) == number:
                return number(unwrap(left) % unwrap(right))
            else:
                raise TypeError('cannot perform operation %s %% %s' % (type(left), type(right)))
    else:                                   # Logical expression
        # print('-> logExp')
        terms = subs(exp)

        if len(terms) == 3:                 # Binary expression
            left = evaluate(envs, terms[0])
            right = evaluate(envs, terms[2])
            op = terms[1]

            if match(op, '&&'):             # And
                # print('-> &&')
                return number(unwrap(left) and unwrap(right))
            elif match(op, '||'):           # Or
                # print('-> ||')
                return number(unwrap(left) or unwrap(right))
            elif match(op, '=='):           # Equals
                # print('-> ==')
                return number(unwrap(left) == unwrap(right))
            elif match(op, '<='):           # Less than or equal to
                # print('-> <=')
                return number(unwrap(left) <= unwrap(right))
            elif match(op, '>='):           # Greater than or equal to
                # print('-> >=')
                return number(unwrap(left) >= unwrap(right))
            elif match(op, '<'):            # Less than
                # print('-> <')
                return number(unwrap(left) < unwrap(right))
            else:                           # Greater than
                # print('-> >')
                return number(unwrap(left) > unwrap(right))
        else:                               # Unary expression (not)
            # print('-> !')
            operand = evaluate(envs, terms[1])
            return number(not unwrap(operand))

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
def execute_stms(envs, incall, inloop, stms):
    # print('execute: %s' % (stms))
    res = result.res(number(0))
    for stm in stms:
        if match(stm, 'line'):              # Line
            stm = sub(stm)
            terms = subs(stm)
            if match(stm, 'retStm'):        # Return
                # print('-> retStm')
                if not incall:          raise SyntaxError('cannot return outside of a function call.')
                elif len(terms) > 1:    return result.ret(evaluate(envs, terms[1]))
                else:                   return result.ret(number(0))
            elif match(stm, 'break'):       # Break
                # print('-> break')
                if not inloop:          raise SyntaxError('cannot break outside of a loop.')
                else:                   return result.brk(number(0))
            elif match(stm, 'exp'):         # Expression
                # print('-> exp')
                res = evaluate(envs, stm)
        else:                               # Block
            stm = sub(stm)
            if match(stm, 'funBlk'):        # Function declaration
                # print('-> funBlk')
                terms = subs(stm)
                fname = terms[0].value
                args = [t.value for t in subs(terms[1])]
                body = subs(terms[2])
                res = bind(envs, fname, func(fname, args, body))
            elif match(stm, 'ifBlk'):       # If-else block
                # print('-> ifBlk')
                terms = subs(stm)
                cond = unwrap(evaluate(envs, terms[0]))
                stms1 = subs(terms[1])
                stms2 = subs(terms[2])
                envs.append({})
                if cond:        res = execute_stms(envs, incall, inloop, stms1)
                else:           res = execute_stms(envs, incall, inloop, stms2)
                envs.pop()
                if res.brk or res.ret:
                    return res
                else:
                    res = res.res
            elif match(stm, 'whileBlk'):    # While block
                # print('-> whileBlk')
                terms = subs(stm)
                stms = subs(terms[1])
                cond = unwrap(evaluate(envs, terms[0]))
                while cond:
                    envs.append({})
                    res = execute_stms(envs, incall, True, stms)
                    envs.pop()
                    if res.ret:
                        return res
                    elif res.brk:
                        res.brk = False
                        return res
                    cond = unwrap(evaluate(envs, terms[0]))
            else:                           # For block
                # print('-> forBlk')
                terms = subs(stm)
                ind = terms[0].value
                arr = unwrap(evaluate(envs, terms[1]))
                stms = subs(terms[2])
                for val in arr:
                    envs.append({ ind: val })
                    res = execute_stms(envs, incall, True, stms)
                    envs.pop()
                    if res.ret:
                        return res
                    elif res.brk:
                        res.brk = False
                        return res
                    res = res.res
    return result.res(res)

# Execute the program.
def execute(envs, stms):
    return execute_stms(envs, False, False, stms)