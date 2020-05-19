'''

The ExprVisitor class: define the skeleton for any
"visitor" that wants to scan the members of a syntax tree.
See also: StmtVisitorClass, GenericVisitor.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''
import Expr
class ExprVisitor:
    # generic astVisitor
    def visitAssign(self, client:Expr.Assign)->object:
        raise NotImplementedError("No visitor defined for Expr.Assign")
    def visitBinary(self, client:Expr.Binary)->object:
        raise NotImplementedError("No visitor defined for Expr.Binary")
    def visitCall(self, client:Expr.Call)->object:
        raise NotImplementedError("No visitor defined for Expr.Call")
    def visitGet(self, client:Expr.Get)->object:
        raise NotImplementedError("No visitor defined for Expr.Get")
    def visitGrouping(self, client:Expr.Grouping)->object:
        raise NotImplementedError("No visitor defined for Expr.Grouping")
    def visitLiteral(self, client:Expr.Literal)->object:
        raise NotImplementedError("No visitor defined for Expr.Literal")
    def visitLogical(self, client:Expr.Logical)->object:
        raise NotImplementedError("No visitor defined for Expr.Logical")
    def visitSet(self, client:Expr.Set)->object:
        raise NotImplementedError("No visitor defined for Expr.Set")
    def visitSuper(self, client:Expr.Super)->object:
        raise NotImplementedError("No visitor defined for Expr.Super")
    def visitThis(self, client:Expr.This)->object:
        raise NotImplementedError("No visitor defined for Expr.This")
    def visitUnary(self, client:Expr.Unary)->object:
        raise NotImplementedError("No visitor defined for Expr.Unary")
    def visitVariable(self, client:Expr.Variable)->object:
        raise NotImplementedError("No visitor defined for Expr.Variable")
