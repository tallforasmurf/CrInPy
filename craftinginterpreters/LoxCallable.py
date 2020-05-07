'''

## Declaration of the LoxCallable meta-class.

Defines the required attributes of any callable object.
Refer to book section 10.2

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''
import Interpreter

class LoxCallable():
    def arity(self):
        raise NotImplementedError()
    def call(self, interpreter:Interpreter, params:[object] ):
        raise NotImplementedError()
