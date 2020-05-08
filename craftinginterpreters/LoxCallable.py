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

class LoxCallable():
    def arity(self):
        raise NotImplementedError()
    def call(self, interpreter, params:[object] ):
        raise NotImplementedError()

'''
Implement a callable function based on a function statement.

The arity is checked before the call() method is invoked, hence
we know the arg list and param list are the same length. Use the
Python builtin function zip() to avoid a boring count loop.
'''

class LoxFunction(LoxCallable):
    def __init__(self, declaration:Stmt.Function):
        self.declaration = declaration

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, args:[object] ):
        environment = Environment.Environment(interpreter.globals)
        for (param,arg) in zip(self.declaration.params,args):
            environment.define( param.lexeme, arg )
        interpreter.execute_block(self.declaration.body, environment)

    def __str__(self)->str:
        return f"fun {self.declaration.name.lexeme}()"
