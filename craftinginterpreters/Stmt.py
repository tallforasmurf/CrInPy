
# Stmt.py defines the class Stmt and its
# subclasses that make up one abstract syntax tree.

# This code is automatically generated (see make_ASTs.py), *DO NOT EDIT*.

#This work is licensed under a
#  Creative Commons Attribution-NonCommercial 4.0 International License
#  see http://creativecommons.org/licenses/by-nc/4.0/

from Token import Token
from typing import List

class Stmt:
	def accept(self,visitor:object):
		raise NotImplementedError("Forgot something?")
import Expr

class Block(Stmt):
	def __init__(self, statements:List[Stmt] ):
		# initialize attributes
		self.statements = statements

	def accept(self, visitor:object):
		return visitor.visitBlock(self)

class Expression(Stmt):
	def __init__(self, expression:Expr ):
		# initialize attributes
		self.expression = expression

	def accept(self, visitor:object):
		return visitor.visitExpression(self)

class Function(Stmt):
	def __init__(self, name:Token,params:List[Token],body:List[Stmt] ):
		# initialize attributes
		self.name = name
		self.params = params
		self.body = body

	def accept(self, visitor:object):
		return visitor.visitFunction(self)

class If(Stmt):
	def __init__(self, condition:Expr,thenBranch:Stmt,elseBranch:Stmt ):
		# initialize attributes
		self.condition = condition
		self.thenBranch = thenBranch
		self.elseBranch = elseBranch

	def accept(self, visitor:object):
		return visitor.visitIf(self)

class Print(Stmt):
	def __init__(self, expression:Expr ):
		# initialize attributes
		self.expression = expression

	def accept(self, visitor:object):
		return visitor.visitPrint(self)

class Return(Stmt):
	def __init__(self, keyword:Token,value:Expr ):
		# initialize attributes
		self.keyword = keyword
		self.value = value

	def accept(self, visitor:object):
		return visitor.visitReturn(self)

class Var(Stmt):
	def __init__(self, name:Token,initializer:Expr ):
		# initialize attributes
		self.name = name
		self.initializer = initializer

	def accept(self, visitor:object):
		return visitor.visitVar(self)

class While(Stmt):
	def __init__(self, condition:Expr,body:Stmt ):
		# initialize attributes
		self.condition = condition
		self.body = body

	def accept(self, visitor:object):
		return visitor.visitWhile(self)

class Class(Stmt):
	def __init__(self, name:Token,methods:List[Function],superclass:Expr.Variable=None ):
		# initialize attributes
		self.name = name
		self.methods = methods
		self.superclass = superclass

	def accept(self, visitor:object):
		return visitor.visitClass(self)
