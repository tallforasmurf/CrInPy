'''

The StmtVisitor class: define the skeleton for any
"visitor" that wants to scan the members of a syntax tree.
See also: ExprVisitorClass, GenericVisitor.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''
import Stmt
class StmtVisitor:
    def visitBlock(self, client:Stmt.Block):
        raise NotImplementedError("No visitor defined for Stmt.Block")
    def visitClass(self, client:Stmt.Class):
        raise NotImplementedError("No visitor defined for Stmt.Class")
    def visitExpression(self, client:Stmt.Expression):
        raise NotImplementedError("No visitor defined for Stmt.Expression")
    def visitFunction(self, client:Stmt.Function):
        raise NotImplementedError("No visitor defined for Stmt.Function")
    def visitIf(self, client:Stmt.If):
        raise NotImplementedError("No visitor defined for Stmt.If")
    def visitPrint(self, client:Stmt.Print):
        raise NotImplementedError("No visitor defined for Stmt.Print")
    def visitReturn(self, client:Stmt.Return):
        raise NotImplementedError("No visitor defined for Stmt.Return")
    def visitVar(self, client:Stmt.Var):
        raise NotImplementedError("No visitor defined for Stmt.Var")
    def visitBreak(self, client:Stmt.Break): # Ch 9 challenge
        raise NotImplementedError("No visitor defined for Stmt.Break")
    def visitWhile(self, client:Stmt.While):
        raise NotImplementedError("No visitor defined for Stmt.While")
