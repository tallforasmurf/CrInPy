'''

The StmtVisitor class: define the skeleton for any
"visitor" that wants to scan the members of a syntax tree.
See also: StmtVisitor.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''
import Stmt
class StmtVisitor:
    def visitBlockStmt(self, client:Stmt.Block):
	raise NotImplementedError("No visitor defined for Stmt.Block")
    def visitClassStmt(self, client:Stmt.Class):
	raise NotImplementedError("No visitor defined for Stmt.Class")
    def visitExpressionStmt(self, client:Stmt.Expression):
	raise NotImplementedError("No visitor defined for Stmt.Expression")
    def visitFunctionStmt(self, client:Stmt.Function):
	raise NotImplementedError("No visitor defined for Stmt.Function")
    def visitIfStmt(self, client:Stmt.If):
	raise NotImplementedError("No visitor defined for Stmt.If")
    def visitPrintStmt(self, client:Stmt.Print):
	raise NotImplementedError("No visitor defined for Stmt.Print")
    def visitReturnStmt(self, client:Stmt.Return):
	raise NotImplementedError("No visitor defined for Stmt.Return")
    def visitVarStmt(self, client:Stmt.Var):
	raise NotImplementedError("No visitor defined for Stmt.Var")
    def visitWhileStmt(self, client:Stmt.While):
	raise NotImplementedError("No visitor defined for Stmt.While")
