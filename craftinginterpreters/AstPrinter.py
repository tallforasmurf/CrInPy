'''

The AstPrinter class for plox. Refer to book section 6.2ff.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

This is not a direct line-by-line translation of AstPrinter.java, more a free
interpretation of it.

'''
import Expr
import Stmt
from Token import Token
# import Stmt -- sooner or later

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

class PrintVisitor(astVisitor):
    '''
    Make a string from a list of exprs, within parens. Used for Binary,
    Grouping, Literal, Unary.
    '''
    def parenthesize(self, name:str, *exprs:Expr.Expr)->str:
        parts = ['('] # list of substrings to be joined later
        parts.append(name)
        for expr in exprs:
            parts.append( expr.accept(self) ) # down the rabbit hole
        parts.append(')')
        return ' '.join(parts) # so pythonic...
    '''
    Print a list of items that can include Expr's, strings, and other things,
    here only for Assign.
    '''
    def parenthesize2(self, name:str, *items:object)->str:
        parts = ['(']
        parts.append(name)
        for item in items:
            if isinstance(item, Expr.Expr):
                parts.append(item.accept(self) )
            elif isinstance(item, Stmt.Stmt):
                raise NotImplementedError("Papa, I'm lost!")
            elif isinstance(item,Token):
                parts.append(item.lexeme)
            elif isinstance(item,str): # I am NOT going to assume str as a default!
                parts.append(item)
            else:
                raise TypeError("unknown argument to parenthesize2")
        parts.append(')')
        return ' '.join(parts)
    '''
    Print the expression nodes, mostly using parenthesize() above
    '''
    def visitAssign(self,client:Expr.Assign)->str:
        return self.parenthesize2('=', client.name.lexeme, client.value)

    def visitBinary(self,client:Expr.Binary)->str:
        return self.parenthesize(client.operator.lexeme,client.left,client.right)

    def visitGrouping(self,client:Expr.Grouping)->str:
        return self.parenthesize('group',client.expression) # why 'group' not blank?

    def visitLiteral(self, client:Expr.Literal)->str:
        if client.value is None:
            return 'nil'
        return str(client.value)

    def visitUnary(self,client:Expr.Unary)->str:
        return self.parenthesize(client.operator.lexeme,client.right)

def AstPrinter(top_token:Expr.Expr):
    display = top_token.accept(PrintVisitor())
    print(display)