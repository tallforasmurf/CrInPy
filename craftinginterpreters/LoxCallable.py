'''

## Declaration of the LoxCallable meta-class and concrete classes based on it.

Specifically this module declares,

* LoxCallable, meta-class for things that can be called like functions. The
  meta-class (Java: "interface") defines the required attributes of any
  callable object. Refer to book section 10.2.

* LoxFunction, concrete implementation of LoxCallable based on a declared
  function.

* LoxClass, concrete LoxCallable based on a class declaration (because a
  classname is called like a function, to instantiate it).

* LoxInstance, class of an instantiated object based on a class declaration.
  This is the type returned by invoking a classname.

* ReturnUnwinder, an Exception raised by the Interpreter executing a RETURN,
  and caught in LoxFunction.call.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

Note: the call() method references an Interpreter; however this class has to
be imported by Interpreter.py. To import Interpreter here would create a
circular import that Python will not allow. For that reason we do not
actually import Interpreter here and so, do not type-annotate the argument.
It will work at runtime.
'''

from __future__ import annotations # allow forward-reference to classes in classes

#from Interpreter import Interpreter # can't do this
import Stmt
from Token import Token
from Environment import Environment
from typing import List, Mapping

'''
Define our RETURN exception for quick unwinding from a return statement.
See Interpreter.visitReturn() and LoxFunction.call() for use.
'''
class ReturnUnwinder(Exception):
    def __init__(self,return_value:object):
        self.return_value = return_value

'''
Here is the meta-class. All concrete versions must implement these methods.
'''
class LoxCallable():
    def arity(self):
        raise NotImplementedError()
    def call(self, interpreter, params:List[object] ):
        raise NotImplementedError()

'''
Define the properties of a callable function. At runtime, when a FUN
declaration is to be executed, its contents are used to generate
a new instance of this class.
'''
class LoxFunction(LoxCallable):
    def __init__(self,
                 declaration:Stmt.Function,
                 closure:Environment,
                 isInitializer:bool=False ):
        self.declaration = declaration
        self.closure = closure
        self.isInitializer = isInitializer # True when this is class init()

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, args:List[object] ):
        '''
        Create a fresh local symbol table for this call, with a parent of the
        "closure" environment that was frozen-in when the function was
        declared.
        '''
        environment = Environment(self.closure)
        '''
        For each parameter named in the declaration, define that name in the
        environment as having the value given in the call.

        The arity is checked before this call() method is invoked, hence we
        know the arg list and param list are the same length. Use the Python
        builtin function zip() to avoid a boring count loop.
        '''
        for (param,arg) in zip(self.declaration.params,args):
            environment.define( param.lexeme, arg )
        '''
        With all parameters assigned their argument values, execute the body
        of the function. There are four cases: the body does or does not
        execute a return statement, and this is or isn't an initializer.
        In an initializer, return <expr> is not allowed. Otherwise, the
        value of return <expr> is in the Exception raised.
                            No return      return
             Initializer     "this"         "this"
             normal method    None           expr
        '''
        try:
            interpreter.execute_block(self.declaration.body, environment)
            return_value = self.closure.fetch("this") if self.isInitializer else None
        except ReturnUnwinder as RW:
            return_value = self.closure.fetch("this") if self.isInitializer else RW.return_value
        return return_value
    '''
    Create a customized version of this very function but bound to
    a particular instance of a class. To bind is simply to invoke but
    with the name "this" predefined as the object instance.

    I note that this means, the "closure" of this new callable is one
    removed from the closure of the parent. When this function begins
    execution via its call() method, it will be executing with,

    locals {} -> closure {this:LoxInstance} -> closure {as of declaration}

    I wonder if that is going to be a problem...? TBD.
    '''
    def bind(self, instance:LoxInstance)->LoxFunction:
        environment = Environment(self.closure)
        environment.define("this",instance) # I am yours, you are mine...
        return LoxFunction(self.declaration,environment,self.isInitializer)

    def __str__(self)->str:
        return f"fun {self.declaration.name.lexeme}()"

'''
Implement a Class object as a version of LoxCallable. See Chapter 12. I am
coding this based on the final Java code, not the sparse introductory version
in Section 12.1.

An instance of LoxClass is created at runtime during the execution of a
Stmt.Class object.

'''
class LoxClass(LoxCallable):
    '''
    Define the name of the magic initializer method in one place.
    '''
    Init = "init"
    '''
    Initialize a class declaration. Note that for the name, he passes in
    name.lexeme from the Stmt.Class, not the whole name Token. Also passed,
    the LoxClass of an optional super_class, and the class's methods, as a
    dict of LoxCallables (probably LoxFunctions: could it contain a LoxClass
    as a method?). Methods are declared as part of the class, data attributes
    are not but are defined during execution.

    Note: the Java version has the args in the order name, super, methods.
    However this requires specifying super_class=None even when calling
    a class with no super (e.g. while still in Chapter 12), so I am putting
    super_class third. This code is only ever called from the Interpreter
    visitClass method anyway.
    '''
    def __init__(self, name:str,
                 methods:Mapping[str:LoxCallable]=None,
                 super_class:LoxClass=None
                 ):
        self.name = name
        self.super_class = super_class
        self.methods = methods
    '''
    Implement display string: in the book he simply returns the name
    alone, but I am going to emulate python a little bit.
    '''
    def __str__(self):
        return f"class {self.name}"
    '''
    Given a method name, return its callable object. Query the superclass if
    necessary (single inheritance, note), otherwise return None. Up to the
    caller to raise an exception, apparently.

    Note I have made the returned value of findMethod() a LoxFunction, not
    just a LoxCallable. That's because it is used to find the "init" which
    has to be a function. So I assume it will always be that.
    '''
    def findMethod(self,name:str)->LoxFunction:
        if self.methods : # even exist,
            if name in self.methods :
                return self.methods[name]
        if self.super_class : # is not None,
            return self.super_class.findMethod(name)
        return None
    '''
    The "arity" of a Class is the arity of its initialization method. If it
    has been defined, return its arity, otherwise return 0.
    '''
    def arity(self):
        initializer = self.findMethod(LoxClass.Init)
        if initializer : # exists, even
            return initializer.arity() # return its needs
        return 0 # else we take no args, thanks
    '''
    To "call" a Class is to create a new LoxInstance object, then
    invoke the initializer with that object as its "this" arg.
    '''
    def call(self, interpreter, params:List[object] )->LoxInstance:
        instance = LoxInstance(self)
        initializer = self.findMethod(LoxClass.Init)
        if initializer : # has been declared,
            '''
            create version of the initializer bound to the new
            instance, and invoke the initializer to prepare it.
            '''
            initializer.bind(instance).call(interpreter,params)
        return instance
'''
Define the contents of a class instance. It knows its class (see above) and
it holds a dict of its data attributes aka "fields". The fields of a class
are added at runtime via the set() method.
'''
class LoxInstance():
    def __init__(self, klass:LoxClass):
        self.klass = klass
        self.fields = dict() # fields TBS
    '''
    Update our fields dict with what might be a new field name,
    and a new value.
    '''
    def set(self, name:Token, value:object):
        self.fields[name.lexeme] = value
    '''
    Access a named attribute of this instance. If it is a field,
    simply return the value of the field.

    If not a field, look for a method in of this name in this class. If a
    method is found, bind it to this object. See method bind() in
    LoxFunction, above.

    I observe this means a data field could "shadow" a declared method.
    '''
    def get(self, name:Token)->object:
        name_str = name.lexeme
        if name_str in self.fields:
            return self.fields[name_str]
        method = self.klass.findMethod(name_str)
        if method : #was found,
            return method.bind(self)
        raise NameError

    '''
    define our display string
    '''
    def __str__(self):
        return f"{self.klass.name} instance."
