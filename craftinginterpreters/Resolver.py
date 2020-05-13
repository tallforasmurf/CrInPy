'''

## Resolver: Pass over the elements of a program and resolve variable references.

Refer to book section 11.1ff

The Resolver is run from the top level, after the Parser, and before the
Interpreter. However, it is given a reference to the Interpreter instance
that *will* be executing this same program, and it "pokes the resolution data
directly into it" (Nystrom's words), thus customizing the Interpreter
instance for this particular program.

Personally I question this design, as it is taking what are properly
attributes of the *program* and storing them in an instance of an
*interpreter*. That just seems wrong, to store semantic, parse- (i.e.
compile-) time properties of the program in a completely different class of
object. IMHO this variable-resolution information should be stored with the
parsed statements, where it could be used along with them, for example as
input to a byte-code or other translator, or for repeated execution. But it
isn't my book...

The Resolver also catches and diagnoses a few errors that the Parser could
not. To do this, it defines its own exception, similar to those of the Parser
and Interpreter, and on catching it, calls an error reporting function
provided by the caller.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''
from GenericVisitor import GenericVisitor
from Interpreter import Interpreter
from typing import List, Mapping, Callable
import Expr
import Stmt
import Token
from TokenType import *
from enum import Enum

'''
Per section 11.5.1, create an enum for the type of function
at this point in the tree walk.
'''
class FunctionType(Enum):
    NOFUN = 0 # not "NONE" -- too many uses of that word
    FUNCTION = 1

class Resolver(GenericVisitor):

    '''
    Define our own error exception class which contains a token from which
    the line number can be gotten, and a specific message. See the error()
    method and the error_report parameter.
    '''
    class ResolutionError(Exception):
        def __init__(self, token:Token.Token, message:str):
            self.token=token
            self.message=message

    '''
    Initialize this resolver.
    '''

    def __init__(self, interpreter:Interpreter, error_report:Callable[[Token.Token,str],None]):
        self.interpreter = interpreter
        self.error_report = error_report
        self.current_function = FunctionType.NOFUN
        self.scopes = list() # List[Mapping[str,bool]]

    '''
    Initiate a scope (a dict mapping names to usage) by pushing a new
    dict on the scopes stack.
    '''
    def beginScope(self):
        self.scopes.append(dict())
    '''
    Exit the current scope, but first, run through it and look for names
    that might not have been referenced in this scope.
    '''
    def endScope(self):
        dying_scope = self.scopes.pop()
        for (name, number) in dying_scope.items():
            if number >= 1 :
                '''
                This name was never referenced. The error reporter expects
                a name Token, not just a string, so re-create one.
                '''
                raise Resolver.ResolutionError(
                    Token.Token(IDENTIFIER,name,None,number),
                    f"Variable {name} never referenced in its scope"
                    )
    '''
    ### Resolve (i.e. visit) each statement in a list of statements.

    This is the top-level entry to the class, called from plox.run_lox after
    parsing and before interpreting. The input is the list of Stmt
    objects returned by the Parser.

    Note that Nystrom also declares overloaded versions of this method
    to resolve (visit) single statements and single expressions. For those
    cases I have elected to just call each target.accept() directly, and
    not have another function to do essentially one line.

    That may turn out to be a mistake, if it turns out that in some
    later chapter he will call those methods from outside the class.
    '''
    def resolve(self, statements:List[Stmt.Stmt]):
        try:
            self.resolve_statements(statements)
        except Resolver.ResolutionError as RE:
            self.error_report(RE.token,RE.message)
            return
    '''
    In order to receive any error exceptions at the top level, the actual
    resolving is delegated here. This is also called below whenever a list
    of statements is to be resolved (block, func declare).
    '''

    def resolve_statements(self, statements:List[Stmt.Stmt]):
        for statement in statements:
            statement.accept(self)

    '''
    ### Utility functions to declare and define a name in our stack of scope
    dictionaries.

    Note in the following we rely on Python's "truthiness" rule that
    an empty list is False.

    Add a name to the top scope on the stack (if any), with value False
    meaning, not initialized yet. Detect multiple declarations of the same
    name.
    '''
    def declare(self,item:Token.Token):
        if self.scopes : # we have an open scope
            scope = self.scopes[-1]
            if item.lexeme in scope:
                raise Resolver.ResolutionError(item,
                "Variable with this name already declared in this scope.")
            scope[item.lexeme]=False
    '''
    Add a name to the top scope on the stack (if any), with a non-False value
    (its name's line number) meaning, initialized and valid to reference, but
    not yet referenced. (Chapter 11 challenge 3)
    '''
    def define(self,item:Token.Token):
        if self.scopes : # we have an open scope
            self.scopes[-1][item.lexeme]=item.line

    '''
    ## Begin the visitations, with visits to statements.

    Visit a block, which contains a list of statements, and when executed,
    establishes a scope. Create a new scope, then visit each statement.
    '''
    def visitBlock(self, client:Stmt.Block):
        self.beginScope()
        self.resolve_statements(client.statements)
        self.endScope()
    '''
    Visit a variable declaration, adding its identifier to the current
    scope. Visit the initializer expression. Then "define" the name as
    legitimate to be referenced. See also visitVariable below.
    '''
    def visitVar(self, client:Stmt.Var):
        self.declare(client.name)
        if client.initializer is not None:
            client.initializer.accept(self)
        self.define(client.name)
    '''
    Visit an assignment expression. First traverse the value expression,
    then note the target's name.
    '''
    def visitAssign(self, client:Expr.Assign):
        client.value.accept(self)
        self.resolveLocal( client, client.name )
    '''
    Resolve a variable's scope-depth and tell the interpreter about it. Note
    that it is not necessary here to check for an empty scopes stack.
    "list(range(len([])))" is an empty list, hence the for loop is null when
    the scopes are empty.

    The expr argument is Expr.Variable when called from visitVariable,
    Expr.Assign when called from visitAssign.

    Set the value of the name in the scope dict to -1, indicating it has
    been referenced or assigned in that scope (Chapter 11 challenge 3)
    '''
    def resolveLocal(self, expr:Expr.Expr, name:Token.Token):
        for index in list(reversed(range(len(self.scopes)))):
            if name.lexeme in self.scopes[index]:
                self.interpreter.resolve(expr, len(self.scopes)-1-index)
                self.scopes[index][name.lexeme] = -1 # not a line number
                return
        # apparently it's a global?
    '''
    Visit a function declaration. Define the function's name immediately.
    Factor out the resolving of params and the body so it can be used for
    class methods later.

    Note Nystrom's Java code does declare(name);define(name); as two
    operations. I don't see why. Both (in his code) use
    <Map>.put(lexeme,value), which I think is identical to
    dict[lexeme]=value, so there's no need to establish the name with
    declare() before setting it to True with define().

    Later: I found out why: he has the check for a duplicate name collision
    in the declare() code. Upside-down pedagogy.
    '''
    def visitFunction(self, client:Stmt.Function):
        self.declare(client.name) # ensure no name clashes
        self.define(client.name) # mark it as legit
        self.resolveFunDecl(client, FunctionType.FUNCTION)
    '''
    Open a new scope and define all the parameter names in it. Then
    recurse to visit the statements of the body. Set the fact that we
    are in a function of some kind, so as to permit return statements.
    '''
    def resolveFunDecl(self, client:Stmt.Function, funtype:FunctionType):
        enclosing_fun_type = self.current_function
        self.current_function = funtype
        self.beginScope()
        for param in client.params:
            self.define(param)
        self.resolve_statements(client.body)
        self.endScope()
        self.current_function = enclosing_fun_type
    '''
    Visit the test-expression and the statements in the branches of an if.
    '''
    def visitIf(self, client:Stmt.If):
        client.condition.accept(self)
        client.thenBranch.accept(self)
        if client.elseBranch:
            client.elseBranch.accept(self)
    '''
    Visit the test-expression and body of a while statement.
    '''
    def visitWhile(self, client:Stmt.While):
        client.condition.accept(self)
        client.body.accept(self)
    '''
    Visit the nodes of the expression in an Expression statement.
    '''
    def visitExpression(self, client:Stmt.Expression):
        client.expression.accept(self)
    '''
    Visit the expressions that are arguments of print and return.
    Diagnose the error of return in top-level code.
    '''
    def visitPrint(self, client:Stmt.Print):
        client.expression.accept(self)

    def visitReturn(self, client:Stmt.Return):
        if self.current_function == FunctionType.NOFUN:
            raise Resolver.ResolutionError(client.keyword,
                    "Cannot return from top-level code.")
        '''
        Note that Nystrom's code checks for client.value==nil.
        However my Parser code always puts an Expr in that field,
        an Expr.Literal(None) by default.
        '''
        client.value.accept(self)
    '''
    ### Expressions:

    Visit a variable expression, whose value is just its name. Verify
    that the named variable has been defined, and document the error
    of referencing a variable in its own initializer.
    '''
    def visitVariable(self, client:Expr.Variable):
        if self.scopes and self.scopes[-1].get(client.name.lexeme) == False :
            raise Resolver.ResolutionError(client.name,
                        "Cannot refer to local variable in its own initializer" )
        self.resolveLocal(client,client.name)
    '''
    Visit the parts of a call expression, first the callee
    (which can be an expression or just an identifier), then the expressions
    of each argument.
    '''
    def visitCall(self,client:Expr.Call):
        client.callee.accept(self)
        for argument in client.arguments:
            argument.accept(self)

    def visitBinary(self,client:Expr.Binary):
        client.left.accept(self)
        client.right.accept(self)

    def visitLogical(self,client:Expr.Logical):
        client.left.accept(self)
        client.right.accept(self)

    def visitUnary(self,client:Expr.Unary):
        client.right.accept(self)

    def visitGrouping(self,client:Expr.Grouping):
        client.expression.accept(self)

    # visitLiteral left to the default parent class "pass"
