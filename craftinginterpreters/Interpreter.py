'''

# Interpret Lox

Interpret and execute Lox code, working on a syntax tree of Stmt objects, as
prepared by Parser.py. Refer to book section 8.1 and forward.

The interpreter is implemented as a "visitor" for the tree composed of Stmt
objects. When interpreting an Expression, it "visits" the tree of Expr
objects. As such it has methods that correspond to (eventually) all of the
methods defined in the StmtVisitor and ExprVisitor classes.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''

from __future__ import annotations # allow forward-reference to this class

import Expr
from ExprVisitorClass import ExprVisitor
import Stmt
from StmtVisitorClass import StmtVisitor
from Token import Token
from TokenType import *
from Environment import Environment
from LoxCallable import LoxCallable, LoxFunction, LoxClass, LoxInstance, ReturnUnwinder
from typing import Callable, List, Mapping

'''
This global is the variable name string used by WHILE, BLOCK and BREAK to
implement break statements. See Chapter 9, challenge 1.
'''

CONTINUE = "¿seguir?" # out of band variable name

class Interpreter(ExprVisitor,StmtVisitor):

    '''
    Create a switch lambda for the binary expression ops. Used in
    visitBinary(). Make it a class variable, so it is only initialized once.
    '''
    lambdic = {
        PLUS:  lambda x,y: x + y,
        MINUS: lambda x,y: x - y,
        STAR:  lambda x,y: x * y,
        SLASH: lambda x,y: x / y,
        GREATER: lambda x,y: x > y,
        GREATER_EQUAL: lambda x,y: x >= y,
        LESS:  lambda x,y: x < y,
        LESS_EQUAL: lambda x,y: x <= y
        }

    '''
    Define our own error exception class which contains a token from which
    the line number can be gotten, and a specific message.
    '''
    class EvaluationError(Exception):
        def __init__(self, token:Token, message:str):
            self.token=token
            self.message=message

    '''
    Define the builtin clock() function as a class implementing LoxCallable.
    '''
    class builtinClock(LoxCallable):
        def arity(self): return 0
        def call(self, interpreter:Interpreter, args:[object] )->float:
            import time
            return time.time()
        def __str__(self): return "native function 'time'"

    '''
    ## Initialize a new Interpreter instance.

    As with the Scanner and Parser classes, Nystrom expects to report errors
    by calling directly to an error display function in the Lox main class.
    That isn't convenient (or even possible) in Python module structure, so
    again, I'm having an error handler passed in to __init__.
    '''
    def __init__(self, error_report:Callable[[int,str],None]):
        self.error_report = error_report
        '''
        Create the global environment for this run. Personally I don't like
        calling it "environment". It's wordy and repetitive and also
        confusing given the number of "[eE]nvironments" we have. I'd prefer
        "globals" since that's what this level is.

        Section 10.2.1, preparing to add built-in functions, he changes this
        to store a reference to the most global environment, and reasonably,
        but unfortunately, calls it "globals". That's the name of a Python
        built-in. Well we are already using Token.type, what's one more.

        Create the globals environment and initialize it with an instance of
        the clock function.
        '''
        self.globals = Environment() # Environment
        self.globals.define(CONTINUE,True) # initialize magic loop variable
        self.globals.define('clock',Interpreter.builtinClock())
        self.environment = self.globals # initialize nested environments
        '''
        Define the "locals" as a dict. This is initialized by the Resolver so
        that each variable reference is associated with its access-depth: how many
        levels up the chain of enclosing environments to look for it. Refer
        to Chapter 11 and Resolver.py, and see the resolve() method below.

        The keys of the dict are not simple identifiers, but Expr instances.
        Each separate reference to an identifier is represented in the parsed
        program by an Expr.Variable or Expr.Assign which is a unique object.
        Thus there is no fear of name-collisions in the mapping; and each
        reference is related to its access-depth at the syntactic point it
        was found.
        '''
        self.locals = dict() # Mapping[Expr,int]

    '''
    Entry point called from the Resolver to store an item in the locals.
    '''
    def resolve(self, reference:Expr.Expr, depth:int):
        self.locals[reference]=depth

    '''
    The entry point for program execution is the following, which receives a
    list of Stmt objects as produced by Parser.parse.

    It returns nothing; the value of a Lox program is all in its
    side-effects, i.e. printed or file output.
    '''
    def interpret(self, program:List[Stmt.Stmt]):
        try:
            for a_statement in program:
                self.execute(a_statement)
        except Interpreter.EvaluationError as EVE:
            self.error_report(EVE.token, EVE.message)

    '''
    Optional entry point for Challenge 8#1, permit "desk calculator mode".
    The program is known to be a single Stmt.Expression instance. Return the
    value of the expression.
    '''
    def one_line_program(self, program:List[Stmt.Stmt])->object:
        try:
            value = self.evaluate(program[0].expression)
            return value
        except Interpreter.EvaluationError as EVE:
            self.error_report(EVE.token, EVE.message)

    '''
    Utility functions
    -----------------

    U1. Specify what's a truthy Lox value. (Can we get a shout-out to Steven
    Colbert here?) Nystrom specifies Lox to use Ruby's rule, by which only
    false and nil are false -- unlike C and Python, where 0 is also False;
    and unlike Python where a null string or empty collection is False.

    Note in this Python implementation, a Lox nil is represented as None, and
    Lox true and false literals are Python True and False. See Parser.py,
    primary().
    '''
    def isTruthy(self,value)->bool:
        if value is None : return False
        if isinstance(value,bool): return value
        return True
    '''
    U2. Specify the meaning of equality in Lox. nil (None) is equal only to
    itself. I think that Python's rules are the same: (None==None)->True,
    None is not equal to anything else. So I'm just going with the built-in.
    '''
    def isEqual(self, lhs, rhs)->bool:
        return lhs == rhs

    '''
    Statement execution!
    --------------------

    S0. To execute a statement is to visit it with this class.

    Note in 8.1.3 Nystrom makes the point that "Unlike expressions,
    statements produce no values, so the return type of the visit methods is
    Void, not Object." And all his visitXxx methods have an explicit "return
    null". In Python, the default for any method that doesn't execute
    "return" is to return None, so I am not reproducing those "return null"s
    '''
    def execute(self, a_statement:Stmt.Stmt):
        a_statement.accept(self)

    '''
    S1. Execute an expression statement. An expression STATEMENT does not
    return a value. Hence to be useful it must have a side-effect, e.g. a
    function call. (But see one_line_program(), above.)
    '''
    def visitExpression(self, client:Stmt.Expression):
        self.evaluate(client.expression)

    '''
    S2. Execute a print statement
    Note the gimmick of dropping ".0" at the end of integral numbers.
    '''
    def visitPrint(self, client:Stmt.Print):
        value = self.evaluate(client.expression)
        str_value = str(value)
        if str_value.endswith('.0') : str_value = str_value[0:-2]
        print(str_value)
    '''
    S3. Var statement.
    '''
    def visitVar(self, client:Stmt.Var):
        value = None
        if client.initializer: # is not None,
            value = self.evaluate(client.initializer)
        self.environment.define( client.name.lexeme, value )
    '''
    Sc. Class statement. As parsed, Stmt.Class has a name and a list
        of methods as Stmt.Function objects. To "execute" the declaration
        we create a new LoxClass instance and bind the name to it.

    Note the two-step definition. Nystrom notes, this allows the class
    definition to reference its own name.
    '''
    def visitClass(self, client:Stmt.Class):
        superclass = None
        if client.superclass: # is given
            superclass = self.evaluate(client.superclass)
            if not isinstance(superclass, LoxClass):
                raise Interpreter.EvaluationError(
                    client.superclass.name,
                    "Superclass must be a class.")
        name_str = client.name.lexeme
        self.environment.define(name_str, None)
        if client.superclass : # is given,
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass) # push a super context
        meth_dict = dict()
        for method in client.methods:
            meth_fun = LoxFunction(method,self.environment,
                                   method.name.lexeme == LoxClass.Init)
            meth_dict[method.name.lexeme]=meth_fun
        klass = LoxClass(name_str,meth_dict,superclass)
        if client.superclass : # was given,
            self.environment = self.environment.enclosing # pop the super context
        self.environment.assign(name_str,klass)

    '''
    SF. Function statement. To "execute" a function declaration is to create
    a LoxCallable and bind its name it in the current environment. A
    reference to the current environment is also stored in the callable as
    its "closure".
    '''
    def visitFunction(self, client:Stmt.Function):
        callable = LoxFunction(client, self.environment)
        self.environment.define(client.name.lexeme, callable)
    '''
    Sr. Execute a return statement. Get the value of its return expression
        if it has one. Then raise the exception.
    '''
    def visitReturn(self, client:Stmt.Return)->object:
        return_value = None
        if client.value : # is an expr not just None
            return_value = self.evaluate(client.value)
        raise ReturnUnwinder(return_value)
    '''
    Sq. Execute a while statement. Set the CONTINUE flag True on entry.
        Stop executing if it becomes False (because a BREAK was executed).
        Force it to True before exit, so a BREAK in this loop won't break
        a containing loop.
    '''
    def visitWhile(self, client:Stmt.While):
        self.environment.define(CONTINUE,True)
        while self.isTruthy( self.evaluate(client.condition ) ) \
              and self.environment.fetch(CONTINUE) :
            self.execute(client.body)
        # if there was a break in this loop, it has done its job.
        self.environment.define(CONTINUE,True)
    '''
    Sbb. Break statement. Set the magic CONTINUE variable False. That's it.
         The Parser ensures this statement can only exist in the scope
         of a loop. Thus we are sure that CONTINUE has been defined in
         some enclosing scope.
    '''
    def visitBreak(self, client:Stmt.Break):
        self.environment.define(CONTINUE,False)
    '''
    S4. Block statement. At visitBlock we create the local scope, but then
    pass execution to a subroutine. Why is not clear as of 8.5.2. Can a block
    be executed from another statement type? Maybe fun?

    In a note, Nystrom observes (correctly IMO) that the handling of the
    environment here is inelegant, but that the alternative is verbose.

    Note on the break statement. When a break is within a block, the block
    should stop processing its list of statements immediately. However a
    break could be nested, for example { if (p) { if (q) { break } } }. A
    break executed at any level within the block should cause the block to
    exit. For this we use the CONTINUE flag set by the break statement.
    '''
    def visitBlock(self, client:Stmt.Block):
        context = Environment(self.environment)
        self.execute_block( client.statements, context )

    def execute_block(self, stmts:List[Stmt.Stmt], context:Environment ):
        save_context = self.environment # need to restore this before return
        '''
        Note on try/except/finally: as (apparently) in Java, if self.execute()
        raises an exception, our finally: section will be executed as Python
        unwinds the stack looking for an except: clause to handle the exception.
        This ensures restoration of the enclosing context even after an error.
        '''
        try:
            self.environment = context # establish local scope
            for statement in stmts:
                self.execute(statement) # any kind of statement, maybe break?
                if not self.environment.fetch(CONTINUE):
                    break # oops, that was a BREAK, exit
        finally:
            self.environment = save_context
    '''
    S5. If statement.
    '''
    def visitIf(self, client:Stmt.If):
        if self.isTruthy( self.evaluate( client.condition ) ):
            self.execute( client.thenBranch )
        elif client.elseBranch : # is not None,
            self.execute( client.elseBranch )

    '''
    Expression evaluation!
    ----------------------

    E0. To evaluate any expression is simply to visit it with this class.
    '''
    def evaluate(self, client:Expr.Expr)->object:
        return client.accept(self)
    '''
    E1. Evaluate a literal.
    '''
    def visitLiteral(self, client:Expr.Literal)->object:
        return client.value
    '''
    EL. Handle logical operators AND and OR
    '''
    def visitLogical(self, client:Expr.Logical)->object:
        lvalue = self.evaluate(client.left)
        if client.operator.type == OR :
            if self.isTruthy(lvalue) :
                return lvalue # short-circuit (discard) everything after OR
        else: # operator is AND
            if not self.isTruthy(lvalue):
                return lvalue # again, short-circuit everything following AND
        '''
        At this point, for OR, the lvalue was false; for AND it was true.
        In either case, the value of the expression is whatever comes next.
        '''
        return self.evaluate(client.right)
    '''
    E2. Evaluate a (grouping).
    '''
    def visitGrouping(self, client:Expr.Grouping)->object:
        return self.evaluate(client.expression)
    '''
    E3. Evaluate a variable reference.

        First, get its depth from the locals map. If that returns None, the
        reference is not to a local; ergo it is a global, so try to fetch it.
        That might result in a name error, which we trap and convert into an
        EvaluationError.

        When it is a local being referenced, use the environment getAt()
        method to fetch its value from the appropriate depth. Since it must
        be defined or the Resolver would not have put it in the locals map,
        that fetch should always work.

        Nystrom breaks the guts of this out to a separate method. I didn't;
        should I have? Yes, so it could be shared with visitThis().
    '''
    def visitVariable(self, client:Expr.Variable)->object:
        # find this Expr as a key in locals
        return self.lookUpVariable(client.name, client)

    def lookUpVariable(self,name:Token, client):
        depth = self.locals.get(client)
        if depth is None:
            try:
                return self.globals.get(name.lexeme)
            except NameError as NE:
                # the value in BaseException.args is a tuple, (namestring,None)
                # for the message, extract the string alone.
                raise Interpreter.EvaluationError(client.name,f"Undefined name {NE.args[0]}")
        # it is local, can't be undefined, so fetch it at its proper depth.
        return self.environment.getAt(depth, name.lexeme)

    '''
    E4. Evaluate an assignment expression, foo=bar. Name resolution as in the above.
    '''
    def visitAssign(self, client:Expr.Assign)->object:
        value = self.evaluate(client.value)
        depth = self.locals.get(client)
        if depth is None:
            try:
                self.globals.assign(client.name.lexeme,value)
                return value
            except NameError as NE:
                raise Interpreter.EvaluationError(client.name,f"Undefined name {NE.args[0]}")
        # it is known as a local, so assignment should work.
        return self.environment.assignAt(depth,client.name.lexeme,value)
    '''
    E5. Evaluate a Unary expression, -x or !x.
    '''
    def visitUnary(self, client:Expr.Unary)->object:
        rhs = self.evaluate(client.right)
        if client.operator.type == MINUS:
            try:
                return -float(rhs)
            except ValueError: # rhs is not a number
                raise Interpreter.EvaluationError(client.operator,'A numeric value is required')
        # operator is !, logical not.
        return not self.isTruthy(rhs)
    '''
    E6. Evaluate a call, callee_expression([args])
        callee can be anything even parenthesized expression or another call
    '''
    def visitCall(self, client:Expr.Call)->object:
        '''
        Evaluate the expression for the callee. That should be an identifier
        whose value in the current environment is a callable -- but it could
        be anything. The Parser is not able to rule out things like 7(5) and
        "hello"(mom). We have to do that here.
        '''
        callee = self.evaluate(client.callee)
        if not isinstance(callee, LoxCallable) :
            raise Interpreter.EvaluationError(client.paren,
                            "Only functions and classes can be called.")
        ''' Evaluate the argument expressions left to right and save them '''
        params = []
        for argument in client.arguments:
            params.append( self.evaluate(argument) )
        '''
        Check that there is an equal number of args and params.
        '''
        if callee.arity() != len(params):
            raise Interpreter.EvaluationError(client.paren,
                    f"Expected {callee.arity()} arguments but got {len(params)}." )
        return callee.call(self,params)
    '''
    Eg1. Evaluate a property reference, <something>.identifier.
        The <something> had better evaluate to a LoxInstance.
        If so, return the result of its get() method for the name.

        Problem: LoxInstance can't raise our EvaluationError. It can only
        raise the standard NameError. We don't want the user to see that;
        we want to show our custom error reporting. So the following does
        a little dance: in except we set a flag that the NameError happened.
        The try/except always completes; then we can raise the right
        exception if necessary.
    '''
    def visitGet(self, client:Expr.Get)->object:
        source = self.evaluate(client.object)
        if isinstance(source,LoxInstance):
            name_found = True
            value = None # keep lint happy
            try:
                value = source.get(client.name)
            except NameError:
                name_found = False
            if name_found :
                return value
            raise Interpreter.EvaluationError(
                    client.name, f"Undefined property '{client.name.lexeme}'.")
        else:
            raise Interpreter.EvaluationError(
                client.name, "Only instances have properties")
    '''
    Eg2. Evaluate a property assignment, which must be to a LoxInstance.
        Return the assigned value.
    '''
    def visitSet(self, client:Expr.Set)->object:
        target = self.evaluate(client.object)
        if not isinstance(target,LoxInstance):
            raise Interpreter.EvaluationError(
                    client.name, f"Only instances may have fields" )
        value = self.evaluate(client.value)
        target.set(client.name,value)
        return value

    '''
    E?. Evaluate "this", which means, finding it at whatever depth in
        the environment chain the Resolver put it at.
    '''
    def visitThis(self, client:Expr.This)->LoxClass:
        return self.lookUpVariable(client.keyword, client)
    '''
    E?. Evaluate "super.methname". An Expr.Super has two fields, the keyword
        "super" and the name token of a method. In order to resolve it we
        need first to find the class corresponding to "super" in the current
        context. The Resolver will have noted how many environment hops away
        it is, so get that depth first.

        Then, using the self-admitted hack (see Chapter 13.3) that the "this"
        class corresponding to the super will be one environment earlier (shallower?)
        we retrieve its class object. Use that to look up the method name.
        Bind that method to that (super) class and return it.
    '''
    def visitSuper(self, client:Expr.Super)->LoxFunction:
        depth = self.locals[client]
        superclass = self.environment.getAt(depth, "super") # type: LoxClass
        that = self.environment.getAt( depth-1, "this" ) # type: LoxClass
        method = superclass.findMethod(client.method.lexeme) # type: LoxFunction
        if method : # was found, is not None,
            return method.bind(that)
        raise Interpreter.EvaluationError(client.method,
                            f"Undefined property '{client.method.lexeme}'." )

    '''
    E7. Evaluate a Binary expression.

    Get the left and right values, then do the thing. A special case is that
    + is overloaded to be a string concatenator.

    Another point worth noting: Lox restricts <,> comparisons to numbers.

    As with unary minus, we attempt float conversion which might raise a
    ValueError exception. Also SLASH could cause a ZeroDivisionError. Convert
    both to our EvaluationError.

    '''
    def visitBinary(self, client:Expr.Binary)->object:
        lhs = self.evaluate(client.left)
        rhs = self.evaluate(client.right)
        op = client.operator.type # factor out a few calls
        '''
        Handle equality comparisons first. Rules of equality are defined in
        isEqual().
        '''
        if op == EQUAL_EQUAL:
            return self.isEqual(lhs,rhs)
        if op == BANG_EQUAL:
            return not self.isEqual(lhs,rhs)
        '''
        Handle the overloading of PLUS. The initial Lox spec requires both
        operands to be of the same type. Challenge #1 at end of chapter asks,
        how about if either operand is a string, make both strings, so
        "scone"+4 -> "scone4".

        But by that rule, "3"+4 -> "34". I can see equal justification for
        saying, if either operand is numeric, try to convert the other to
        numeric and do numeric addition. Whichever you do, some user will
        find you being "inconsistent". Generally I don't think it is a good
        idea, in a language described as "simple", to get into the game of
        coercing types at all.
        '''
        if op == PLUS:
            if isinstance(lhs,str) and isinstance(rhs,str):
                return lhs+rhs
            if type(lhs) != type(rhs) :
                raise Interpreter.EvaluationError(client.operator,'Both operands must have the same type')
            # at this point we know both PLUS operands are numbers. Fall through.
        '''
        All the remaining binops require numeric values.

        I *think* the only possible exceptions from these arithmetic ops are
        ValueError from float conversion, and ZeroDivisionError from divide.
        Use the dict of lambdas declared above for quick lookup and execution.
        '''
        if op in Interpreter.lambdic :
            try:
                return Interpreter.lambdic[op](float(lhs),float(rhs))
            except ValueError:
                raise Interpreter.EvaluationError(client.operator,'Numeric operands required')
            except ZeroDivisionError:
                # note it turns out that this, which I did almost automatically,
                # is actually "challenge #3" in the chapter.
                raise Interpreter.EvaluationError(client.operator,'Cannot divide by zero')

        raise NotImplementedError # because I done screwed up sumpin.