# StupidLang (aka Slang): a stupid Python-interpreted programming language.

# Language specification:
# prog ::= ( stms )
# stms ::= LAMBDA
#		 | ( stm ) stms
# stm  ::= fExp
#		 | def var ( farr ) ( stms )
#		 | return
#		 | return ( exp )
#		 | if ( lExp ) ( stms ) ( stms )
#		 | while ( lExp ) ( stms )
#		 | for ( var in [ arr ] ) ( stms )
#		 | for ( var in var ) ( stms )
#		 | for ( var in fExp ) ( stms )
# farr ::= LAMBDA
#		 | var , farr
#		 | var farr
# exp  ::= prim
#		 | fExp
#		 | aExp
#		 | lExp
# prim ::= num
#		 | str
#		 | var
#		 | [ arr ]
# num  ::= -?\d+
# str  ::= "[^"]*"
# var  ::= [A-Za-z]+
# arr  ::= LAMBDA
#		 | ( exp ) , arr
#		 | ( exp ) arr
# fExp ::= var ( parr )
# parr ::= LAMBDA
#		 | ( exp ) , parr
#		 | ( exp ) parr
# aExp ::= aOp2 ( exp ) ( exp )
# aOp2 ::= +
#		 | -
#		 | *
#		 | /
# lExp ::= lOp1 ( exp )
#		 | lOp2 ( exp ) ( exp )
# lOp1 ::= !
# lOp2 ::= &&
#		 | ||
#		 | ==
#		 | >
#		 | <

# Language notes:
# - Only 0, "", and [] are falsy.
# - Functions without a return value return the value of the last statement.
# - For loops work like Python for loops, iterating over an array.
# - Built-in functions include: print, range.

# To-do:
# - arithmetic
# - strings
# - run-time type-checking
# - functions
# - for
# - while
# - local environments
# - arrays (assignment, access)
# - other useful built-in functions
# - functional features?
# - load programs from files

from collections import deque

# Test code

prog1 = '( ( = x ( 5 ) )\
		   ( = y ( 3 ) )\
		   ( if ( > ( x ) ( y ) )\
		     ( ( print ( ( x ) ) ) )\
		     ( ( print ( ( y ) ) ) ) ) )'

prog2 = '( ( print ( == ( ! ( 2 ) ) ( ! ( 1 ) ) ) ) )'

prog3 = '((def fn(x,y,z) ((=var "this is a tokenizing stress test!!!\
		 					123 ABC !@#$%^&*()=")\
		 				  (print var)\
		 				  (=arr[1, 2, 3]))))'

# Globals

ws = ' \t\b\n'
digits = '0123456789'
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

# Types

class number:

	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return 'number(%d)' % (self.value)

class string:

	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return 'string("%s")' % (self.value)

class array:

	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return 'array(%s)' % (str(self.value))

class func:

	def __init__(self, name, args, body):
		self.name = name
		self.args = args
		self.body = body

	def __repr__(self):
		return 'func(%s)' % (str(self.name))

class built_in_func:

	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return 'built_in_func(%s)' % (str(self.value))

# Built-in functions

# Print the given value.
def s_print(value):
	if type(value) == number or type(value) == string or type(value) == array:
		print(str(value.value))
	else:
		print(str(value))

# Return the array of integers in the interval [lo, hi).
def s_range(lo, hi):
	return array(list(range(lo, hi)))

# Return the size of the array.
def s_size(arr):
	return len(arr.value)

# Slang core

# Return the nearest value assigned to the variable name. If the name is
# undefined, throw an error.
def find(envs, name):
	for env in envs[::-1]:
		if name in env:
			return env[name]
	raise NameError('Name "' + name + '" is not defined.')

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
def call(f, args):
	print('calling ' + str(f))
	if type(f) == built_in_func:
		print('built-in')
		return f.value(*[unwrap(arg) for arg in args])
	elif type(f) != func:
		raise TypeError('Value ' + str(f) + ' is not a function.')
	fenv = { farg: arg for (farg, arg) in zip(f.args, args) }
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
		elif c1 in '()[]!><+*/':
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
			# print('close paren')
			lst = deque()
			while stack[-1] != '(':
				item = stack.pop()
				# print('adding ' + str(item) + ' to lst')
				lst.appendleft(item)
			stack.pop()
			stack.append(lst)
		elif token == ']':
			# print('close paren')
			lst = deque()
			while stack[-1] != '[':
				item = stack.pop()
				# print('adding ' + str(item) + ' to lst')
				lst.appendleft(item)
			stack.pop()
			stack.append(array(lst))
		else:
			stack.append(token)
	return stack.pop()

# Return the value of the expression.
def evaluate(envs, exp):
	if len(exp) == 1:			# Primitive
		if type(exp[0]) in [number, string, array]:
			return exp[0]
		else:
			return find(envs, exp[0])
	elif len(exp) == 2:			# Function expression
		print('function call')
		args = [evaluate(envs, arg) for arg in exp[1]]
		return call(find(envs, exp[0]), args)
	else:
		if exp[0] == '!':
			return 0 if unwrap(evaluate(envs, exp[1])) else 1
		elif exp[0] == '==':
			int(unwrap(evaluate(envs, exp[1])) == unwrap(evaluate(envs, exp[2])))
		elif exp[0] == '&&':
			int(unwrap(evaluate(envs, exp[1])) and unwrap(evaluate(envs, exp[2])))
		elif exp[0] == '||':
			int(unwrap(evaluate(envs, exp[1])) or unwrap(evaluate(envs, exp[2])))
		elif exp[0] in '><':
			val1 = evaluate(envs, exp[1])
			val2 = evaluate(envs, exp[2])
			if type(val1) != type(val2) or type(val1) not in [number, string]:
				raise TypeError('Values ' + str(val1) + ' and ' + str(val2) + ' are not comparable.')
			if exp[0] == '>':
				return unwrap(val1) > unwrap(val2)
			else:
				return unwrap(val1) < unwrap(val2)

# Execute the statements in the given list.
def execute(envs, stms):
	res = 0
	for stm in stms:
		if not len(stm):
			continue
		if stm[0] == '=':		# Assignment
			res = bind(envs, stm[1], evaluate(envs, stm[2]))
		elif stm[0] == 'if':	# If
			print('if')
			if bool(evaluate(envs, stm[1])):
				print('if true')
				res = execute(envs, stm[2])
			else:
				print('if false')
				res = execute(envs, stm[3])
		elif stm[0] == 'def':	# Function definition
			print('function definition')
			res = bind(envs, stm[1], func(stm[1], stm[2], stm[3]))
		else:					# Function
			print('function expression')
			print(stm)
			res = evaluate(envs, stm)
	return res

# Interpret the program string.
def interpret(p):
	tokens = tokenize(p)		# Tokenize
	stms = parse(tokens)		# Parse
	global_env = {				# Global environment
		'print': built_in_func(s_print),
		'range': built_in_func(s_range)
	}
	envs = [global_env]			# Create environment stack
	execute(envs, stms)			# Execute