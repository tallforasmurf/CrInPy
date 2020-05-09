'''

## Declaration of the LoxCallable meta-class.

Defines the required attributes of any callable object.
Refer to book section 10.2

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

Note: the call() method references an Interpreter, however this class
is imported by Interpreter.py, which creates a circular import that
Python refuses to allow. For that reason we do not actually import
Interpreter here and do not type-annotate the argument. It will work
at runtime.
'''
#from Interpreter import Interpreter
import Stmt
import Environment

'''
Define our RETURN exception for quick unwinding from a return statement.
See Interpreter.visitReturn() and LoxFunction.call() for use.
'''
class ReturnUnwinder(Exception):
    def __init__(self,return_value:object):
        self.return_value = return_value

class LoxCallable():
    def arity(self):
        raise NotImplementedError()
    def call(self, interpreter, params:[object] ):
        raise NotImplementedError()

'''
Implement a callable function based on a function statement.

When an instance of LoxCallable is created (during execution of
a "fun" declaration), the then
'''

class LoxFunction(LoxCallable):
    def __init__(self, declaration:Stmt.Function, closure:Environment ):
        self.declaration = declaration
        self.closure = closure

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, args:[object] ):
        environment = Environment.Environment(self.closure)
        '''
        For each parameter name in the declaration, define that name
        in the environment as having the value from the call.

        The arity is checked before the call() method is invoked, hence we
        know the arg list and param list are the same length. Use the Python
        builtin function zip() to avoid a boring count loop.
        '''
        for (param,arg) in zip(self.declaration.params,args):
            environment.define( param.lexeme, arg )
        '''
        With all parameters assigned their argument values, execute
        the body of the function. If it executes a return statement,
        catch the value from the exception; otherwise, use None.
        '''
        try:
            interpreter.execute_block(self.declaration.body, environment)
            return_value = None
        except ReturnUnwinder as RW:
            return_value = RW.return_value
        return return_value


    def __str__(self)->str:
        return f"fun {self.declaration.name.lexeme}()"
