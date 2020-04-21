
# Expr.py defines the class Expr and its
# subclasses that make up one abstract syntax tree.

# This code is automatically generated (see make_ASTs.py), *DO NOT EDIT*.

#This work is licensed under a
#  Creative Commons Attribution-NonCommercial 4.0 International License
#  see http://creativecommons.org/licenses/by-nc/4.0/

from Token import Token
from typing import List

class Expr:
	def accept(self,visitor:object):
		raise NotImplementedError("Forgot something?")

class Assign(Expr):
	def __init__(self, name:Token,value:Expr ):
		# initialize attributes
		self.name = name
		self.value = value

	def accept(self, visitor:object):
		return visitor.visitAssign(self)

class Binary(Expr):
	def __init__(self, left:Expr,operator:Token,right:Expr ):
		# initialize attributes
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor:object):
		return visitor.visitBinary(self)

class Call(Expr):
	def __init__(self, callee:Expr,paren:Token,arguments:List[Expr] ):
		# initialize attributes
		self.callee = callee
		self.paren = paren
		self.arguments = arguments

	def accept(self, visitor:object):
		return visitor.visitCall(self)

class Get(Expr):
	def __init__(self, object:Expr,name:Token ):
		# initialize attributes
		self.object = object
		self.name = name

	def accept(self, visitor:object):
		return visitor.visitGet(self)

class Grouping(Expr):
	def __init__(self, expression:Expr ):
		# initialize attributes
		self.expression = expression

	def accept(self, visitor:object):
		return visitor.visitGrouping(self)

class Literal(Expr):
	def __init__(self, value:object ):
		# initialize attributes
		self.value = value

	def accept(self, visitor:object):
		return visitor.visitLiteral(self)

class Logical(Expr):
	def __init__(self, left:Expr,operator:Token,right:Expr ):
		# initialize attributes
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor:object):
		return visitor.visitLogical(self)

class Set(Expr):
	def __init__(self, object:Expr,name:Token,value:Expr ):
		# initialize attributes
		self.object = object
		self.name = name
		self.value = value

	def accept(self, visitor:object):
		return visitor.visitSet(self)

class Super(Expr):
	def __init__(self, keyword:Token,method:Token ):
		# initialize attributes
		self.keyword = keyword
		self.method = method

	def accept(self, visitor:object):
		return visitor.visitSuper(self)

class This(Expr):
	def __init__(self, keyword:Token ):
		# initialize attributes
		self.keyword = keyword

	def accept(self, visitor:object):
		return visitor.visitThis(self)

class Unary(Expr):
	def __init__(self, operator:Token,right:Expr ):
		# initialize attributes
		self.operator = operator
		self.right = right

	def accept(self, visitor:object):
		return visitor.visitUnary(self)

class Variable(Expr):
	def __init__(self, name:Token ):
		# initialize attributes
		self.name = name

	def accept(self, visitor:object):
		return visitor.visitVariable(self)
