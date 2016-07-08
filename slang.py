# StupidLang (aka Slang): a stupid Python-interpreted programming language.

# Language specification:
# prog ::= ( stms )
# stms ::= LAMBDA
#		 | ( stm ) stms
# stm  ::= var ( exp )
#		 | def var ( farr ) ( stms )
#		 | return ( exp )
#		 | if ( lExp ) ( stms ) ( stms )
#		 | while ( lExp ) ( stms )
#		 | for ( var in arr ) ( stms )
#		 | for ( var in var ) ( stms )
# farr ::= LAMBDA
#		 | var farr
# exp  ::= prim
#		 | fExp
#		 | aExp
#		 | lExp
# prim ::= num
#		 | str
#		 | var
#		 | ( arr )
# num  ::= -?\d+
# str  ::= "[^"]*"
# var  ::= [A-Za-z]+
# arr  ::= LAMBDA
#		 | ( exp ) arr
# fExp ::= var ( arr )
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
# - Only 0, "", and (()) are falsy.
# - Functions without a return expression return 0.
# - For loops work like Python for loops.
# - Built-in functions include: print, range.

# To-do:
# - arithmetic
# - strings
# - run-time type-checking
# - functions
# - for
# - while
# - local environments
# - arrays
# - other useful built-in functions
# - functional features?
# - load programs from files

from collections import deque

# Test code
prog1 = '( ( = x ( 5 ) )\
		   ( = y ( 3 ) )\
		   ( if ( > ( x ) ( y ) )\
		     ( ( print ( x ) ) )\
		     ( ( print ( y ) ) ) ) )'

prog2 = '( ( print ( == ( ! ( 2 ) ) ( ! ( 1 ) ) ) ) )'

prog3 = '((def fn(x y z) ((=var "this is a tokenizing stress test!!!\
		 					123 ABC !@#$%^&*()=")\
		 					(print var))))'

# Globals
ws = ' \t\b\n'
digits = '0123456789'
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

# Return a list of tokens for the given program string.
def tokenize(p):
	tokens = []
	i = 0
	while i < len(p):
		c1 = p[i]
		c2 = p[i+1] if i+1 < len(p) else None
		if c1 in ws:
			i += 1
		elif c1 in '()!><+*/':
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
			tokens.append(int(p[num_start:num_end]))
			i = num_end
		elif c1 == '"':
			str_start = i + 1
			str_end = str_start
			while p[str_end] != '"':
				str_end += 1
			# TODO: somehow denote string type
			tokens.append(p[str_start:str_end])
			i = str_end + 1
	return tokens

	# words = p.split()
	# tokens = []
	# for word in words:
	# 	try:
	# 		tokens.append(int(word))
	# 	except ValueError:
	# 		tokens.append(word)
	# return tokens

# Return a list representing the program statements.
def lex(tokens):
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
		else:
			stack.append(token)
	return stack.pop()

# Return the evaluation of the expression.
def evaluate(env, exp):
	if len(exp) == 1:
		if type(exp[0]) == int:
			return exp[0]
		elif exp[0] in env:
			return env[exp[0]]
		else:
			raise NameError('Variable "' + exp[0] + '" is undefined.')
	else:
		if exp[0] == '!':
			return 0 if evaluate(env, exp[1]) else 1
		elif exp[0] == '==':
			return 1 if evaluate(env, exp[1]) == evaluate(env, exp[2]) else 0
		elif exp[0] == '&&':
			return 1 if evaluate(env, exp[1]) and evaluate(env, exp[2]) else 0
		elif exp[0] == '||':
			return 1 if evaluate(env, exp[1]) or evaluate(env, exp[2]) else 0
		elif exp[0] == '>':
			return 1 if evaluate(env, exp[1]) > evaluate(env, exp[2]) else 0
		elif exp[0] == '<':
			return 1 if evaluate(env, exp[1]) < evaluate(env, exp[2]) else 0

# Execute the statements in the given list.
def execute(env, stms):
	for stm in stms:
		if not len(stm):
			continue
		if stm[0] == 'print':	# Print
			print(evaluate(env, stm[1]))
		elif stm[0] == '=':		# Assignment
			env[stm[1]] = evaluate(env, stm[2])
		else:					# If
			if bool(evaluate(env, stm[1])):
				execute(env, stm[2])
			else:
				execute(env, stm[3])

# Interpret the program string.
def interpret(p):
	tokens = tokenize(p)		# Tokenize
	stms = lex(tokens)			# Lex
	env = dict()				# Create environment
	execute(env, stms)			# Execute