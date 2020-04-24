'''

Evaluate Expression trees.

Refer to book section 7.2 and forward.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

As of chapter 7, this is called Interpreter, but I suspect in a later
class it will be more appropriately called Evaluator... TBS

'''
import Expr
from ExprVisitorClass import ExprVisitor
from Token import Token
from TokenType import *
from typing import Callable

class Interpreter(ExprVisitor):

    '''
    Create a switch lambda for the binary ops. Make it a class variable, so
    it is only initialized once. Used in visitBinary().
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
    Define our own exception class which will contain a token, from which
    the line number can be gotten, and a specific message.
    '''
    class EvaluationError(Exception):
        def __init__(self, token:Token, message:str):
            self.token=token
            self.message=message

    '''
    Nystrom's version of this class is unlike his Scanner class, which is
    initialized with the text to scan. In his code, Interpreter receives the
    Expr to evaluate at its interpret() method. This is presumably because he
    anticipates instantiating one Interpreter object and using it repeatedly?

    As with the Scanner class, he expects to report errors by calling
    directly to an error printer in the Lox main class. As with our Scanner,
    that isn't pythonic (or even possible) so again, I'm having an error
    handler passed in to __init__.
    '''
    def __init__(self, error_report:Callable[[int,str],None]):
        self.error_report = error_report

    '''
    The only entry point is the following, where the syntax tree
    is delivered. The value of the tree *as a string* is returned.

    Note Nystrom's interpret() method actually prints the value. I don't
    think that is appropriate! An interpreter should interpret, and its
    return value should be the value of the interpreted expression. If all it
    does is call system.out.println, how can it be integrated into a larger
    system where the value of an expression is only one step in the value of
    a statement or a program?

    I expect he will correct this later; I'm correcting it now.

    The only exception that should be raised here is our EvaluationError.
    That is because the only places where a Python built-in exception could
    be raised, are in try statements that convert it to EvaluationError and
    re-raise it.
    '''
    def interpret(self, expr:Expr.Expr)->str:
        try:
            result = self.evaluate(expr)
        except Interpreter.EvaluationError as EVE:
            self.error_report(EVE.token, EVE.message)
            result = ''
        display = str(result)
        if display.endswith('.0'): display = display[0:-2]
        return display

    '''
    To evaluate any expression is simply to visit it with this class.
    '''
    def evaluate(self, client:Expr.Expr)->object:
        return client.accept(self)

    '''
    Specify what's a truthy Lox value. (Can we get a shout-out to Steven
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
    Specify the meaning of equality in Lox. nil (None) is equal only to itself.
    Python ensures that None is not equal to anything else including False.
    '''
    def isEqual(self, lhs, rhs)->bool:
        if (lhs is None) and (rhs is None) : return True
        return lhs == rhs
    '''
    Evaluate a literal.
    '''
    def visitLiteral(self, client:Expr.Literal)->object:
        return client.value
    '''
    Evaluate a (grouping).
    '''
    def visitGrouping(self, client:Expr.Grouping)->object:
        return self.evaluate(client.expression)
    '''
    Evaluate a Unary expression, -x or !x.
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
    Evaluate a Binary expression. Get the left and right values, then do the
    thing. A special case is that + is overloaded to be a string
    concatenator.

    Another point worth noting: Lox restricts <,> comparisons to numbers.

    Again as with unary minus, we attempt float conversion which might raise
    a ValueError exception. Also SLASH could cause a ZeroDivisionError. Convert both
    to our EvaluationError.

    '''
    def visitBinary(self, client:Expr.Binary)->object:
        lhs = self.evaluate(client.left)
        rhs = self.evaluate(client.right)
        op = client.operator.type # save a few calls

        '''
        Handle equality comparisons first. Rules of equality in isEqual().
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
        numeric and if you can, do numeric addition. Now, "convert to numeric
        if you can" is a trickier thing to do. For example, "3.5".isdecimal()
        yields False! And there's "4e5" which is a valid numeric in Python.
        So the only simple test is to do float(thing) in a try, which is a
        bore. Generally I don't think it is a good idea, in any language
        described as "simple", to get into the game of coercing types at all.
        '''
        if op == PLUS:
            if isinstance(lhs,str) and isinstance(rhs,str):
                return lhs+rhs
            if type(lhs) != type(rhs) :
                raise Interpreter.EvaluationError(client.operator,'Both operands must have the same type')
            # for PLUS, both operands are numbers. Fall through.
        '''
        All the remaining operations require numeric values.

        I *think* the only possible exceptions from simple arithmetic ops are
        ValueError from float conversion, and ZeroDivisionError from divide.
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