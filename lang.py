# StupidLang (aka Slang): a stupid Python-interpreted programming language.

# Language specification:
# prog ::= ( stms )
# stms ::= LAMBDA
#		 | ( stm ) stms
# stm  ::= var ( exp )
#		 | def var ( arr ) ( stms )
#		 | return ( exp )
#		 | if ( lExp ) ( stms ) ( stms )
#		 | while ( lExp ) ( stms )
#		 | for ( var in arr ) ( stms )
#		 | for ( var in var ) ( stms )
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

# Return a list of tokens for the given program string.
def tokenize(p):
	words = p.split()
	tokens = []
	for word in words:
		try:
			tokens.append(int(word))
		except ValueError:
			tokens.append(word)
	return tokens

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