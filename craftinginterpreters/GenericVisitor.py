'''

The GenericVisitor class: define a merged base for a "visitor"
"visitor" that wants to traverse all the members of a program,
statements and expressions alike. Used in Resolver.py among others.

See also: StmtVisitorClass, ExprVisitorClass.

The base classes raise NotImplementedError in any method not overridden.
These methods simply do nothing (pass) and return None.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''
from ExprVisitorClass import ExprVisitor
from StmtVisitorClass import StmtVisitor

class GenericVisitor(ExprVisitor,StmtVisitor):
    '''
    Initializer as required.
    '''
    def __init__(self):
        pass
    '''
    Expression visitors.
    '''
    def visitAssign(self, client:Expr.Assign)->object:
        pass
    def visitBinary(self, client:Expr.Binary)->object:
        pass
    def visitCall(self, client:Expr.Call)->object:
        pass
    def visitGet(self, client:Expr.Get)->object:
        pass
    def visitGrouping(self, client:Expr.Grouping)->object:
        pass
    def visitLiteral(self, client:Expr.Literal)->object:
        pass
    def visitLogical(self, client:Expr.Logical)->object:
        pass
    def visitSet(self, client:Expr.Set)->object:
        pass
    def visitSuper(self, client:Expr.Super)->object:
        pass
    def visitThis(self, client:Expr.This)->object:
        pass
    def visitUnary(self, client:Expr.Unary)->object:
        pass
    def visitVariable(self, client:Expr.Variable)->object:
        pass
    '''
    Statement visitors.
    '''
    def visitBlock(self, client:Stmt.Block):
        pass
    def visitClass(self, client:Stmt.Class):
        pass
    def visitExpression(self, client:Stmt.Expression):
        pass
    def visitFunction(self, client:Stmt.Function):
        pass
    def visitIf(self, client:Stmt.If):
        pass
    def visitPrint(self, client:Stmt.Print):
        pass
    def visitReturn(self, client:Stmt.Return):
        pass
    def visitVar(self, client:Stmt.Var):
        pass
    def visitBreak(self, client:Stmt.Break): # Ch 9 challenge
        pass
    def visitWhile(self, client:Stmt.While):
        pass
