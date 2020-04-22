'''

The AstVisitor class for plox. This class defines the skeleton for any
"visitor" that wants to scan the members of a syntax tree.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''
import Expr
class astVisitor:
    # generic astVisitor
    def visitAssign(self, client:Expr.Assign):
        raise NotImplementedError("No visitor defined for Expr.Assign")
    def visitBinary(self, client:Expr.Binary):
        raise NotImplementedError("No visitor defined for Expr.Binary")
    def visitCall(self, client:Expr.Call):
        raise NotImplementedError("No visitor defined for Expr.Call")
    def visitGet(self, client:Expr.Get):
        raise NotImplementedError("No visitor defined for Expr.Get")
    def visitGrouping(self, client:Expr.Grouping):
        raise NotImplementedError("No visitor defined for Expr.Grouping")
    def visitLiteral(self, client:Expr.Literal):
        raise NotImplementedError("No visitor defined for Expr.Literal")
    def visitLogical(self, client:Expr.Logical):
        raise NotImplementedError("No visitor defined for Expr.Logical")
    def visitSet(self, client:Expr.Set):
        raise NotImplementedError("No visitor defined for Expr.Set")
    def visitSuper(self, client:Expr.Super):
        raise NotImplementedError("No visitor defined for Expr.Super")
    def visitThis(self, client:Expr.This):
        raise NotImplementedError("No visitor defined for Expr.Unary")
    def visitUnary(self, client:Expr.Unary):
        raise NotImplementedError("No visitor defined for Expr.Unary")
    def visitVariable(self, client:Expr.Variable):
        raise NotImplementedError("No visitor defined for Expr.Variable")
