'''

Environment class for plox. Refer to book section 8.3

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

Summarizing the Environment API:

    ancestor(distance:int) -> Environment
        Return the nth enclosing (more global) Environment, 0 being
        this one. No check of distance, will return None if one-over,
        or cause an error "Nonetype has no method ancestor".

    assignAt( distance:int, name:Token, value:object)
        Assign value to Token.lexeme in the nth more global environment.
        Uses ancestor().

    getAt( distance:int, name:Token ) -> object
        Return value of Token.lexeme from the nth more global environment.
        Uses ancestor().

    define(self, name:str, value:object):
        Set name to value in this environment. Name need not exist.

    assign(self, name:Token, value:object)
        Set name.lexeme to value in the nearest environment where it is defined.
        Raise NameError if it is not known.

    get(self, name:Token)->object
        Return value of name.lexeme from its closest (most local) definition.
        Raise NameError if not found. Uses fetch().

    fetch(self, name:str)->object
        Return the value of name from its closest (most local) definition.
        Raise NameError if not found.

Apparently mappings are a big deal in Java, where they are basic to the
language in Python.

Anyway, the Lox Environment is a set of nested dictionaries. Each dict has a
member 'enclosing' which is the dictionary that represents its enclosing
(more global) syntactic scope at runtime. The Java implementation overloads
the instantiation call to pass or not pass an enclosing dict; here we use
an optional parameter to __init__.

To implement the Lox operations get() and assign() we just call on the dict
class operations __contains__, __getitem__ and __setitem__.

A remaining puzzle, presumably explained later in the book. At the end of the
Java version of this module, there is the following code:

    @Override
    public String toString() {
        String result = values.toString();
        if (enclosing != null) {
            result += " -> " + enclosing.toString();
        }
    return result;
    }

It appears to be overriding  the toString method of the Environment class?
So that when called in an inner scope, it will return a recursive series of
strings from most local to most global, separated by ->. But what is the string
being returned? In Python the equivalent (I think) is str(the_dict) which returns
a display of the whole dict,

    >>> str(d)
        "{'f': 'foo', 'g': 'goo'}"

That can't be what this toString is returning, but then what? The Environment is
not given an identifier it could be displaying...

'''
from __future__ import annotations # allow forward-reference to this class

from Token import Token
from typing import Optional

class Environment(dict):
    def __init__(self, enclosing=None):
        self.enclosing = enclosing # Optional[Environment]

    '''
    Return the value of a name, if it exists at this or an enclosing scope,
    otherwise raise NameError (not KeyError as a dict would normally do).

    This is broken into two levels. Code executing an expression comes to
    get() with a Token for the name. Internal code, esp. visitWhile, comes
    to fetch() with a string name. Also saves a few .lexeme de-references
    when a definition is nested.
    '''
    def get(self, name:Token)->object:
        return self.fetch(name.lexeme)

    def fetch(self, name:str)->object:
        if self.__contains__(name):
            return self.__getitem__(name)
        if self.enclosing : # is not None,
            return self.enclosing.fetch(name)
        # we are the global scope and we don't have this name.
        # Put the name string in the "args" of the NameError exception.
        raise NameError(name)

    '''
    Assign a value (any object) to a name, if the name is defined in this or
    an enclosing scope, otherwise NameError.
    '''
    def assign(self, name:Token, value:object):
        if self.__contains__(name.lexeme):
            self.__setitem__(name.lexeme,value)
        elif self.enclosing: # is not None,
            self.enclosing.assign(name,value)
        else:
            # we are the global scope and we don't have it
            raise NameError(name.lexeme)
    '''
    Define (as in "var = expr") a value at this scope level.

    Note that while get() and assign() receive the name in the form of a
    Token (presumably an IDENTIFIER one), this method gets the name as a
    string. Note also that we do not check whether the name has already
    been defined, see book section 8.3 for discussion.
    '''
    def define(self, name:str, value:object):
        self.__setitem__(name,value)
    '''
    Return our enclosing scope at a certain integer remove. As of this
    writing I have not got to the discussion for this feature.

    This is the code I am translating, it appears to allow distance==0
    and to not check for over-run.

        Environment ancestor(int distance) {
        Environment environment = this;
        for (int i = 0; i < distance; i++) {
          environment = environment.enclosing; // [coupled]
        }
        return environment;

    How about a recursive one-line solution:
        def ancestor(distance):
            return self.enclosing.ancestor(distance-1) if distance>0 else self

    Coding note: this method returns the self-class Environment. Prior to
    Python 3.7 that was not possible as that name has not been defined until
    this class definition is closed. "from __future__ import annotations"
    fixes this, and in 3.9 it will be fixed permanently.
    '''
    def ancestor(distance:int)->Environment:
        env = self
        while distance > 0 :
            env = env.enclosing
            distance -= 1
        return env
    '''
    The following functions get/set a value in an enclosing scope given its
    distance. Here is the Java,
        Object getAt(int distance, String name) {
            return ancestor(distance).values.get(name);
        }
        void assignAt(int distance, Token name, Object value) {
            ancestor(distance).values.put(name.lexeme, value);
        }

    Thing to note is that it assumes an Environment *contains* a values
    attribute which is a map. As I'm doing it, the Environment *is* the map.
    Thus, one less level of function indirection.

    '''
    def getAt( distance:int, name:Token ) -> object:
        return self.ancestor(distance).get(name)

    def assignAt( distance:int, name:Token, value:object):
        self.ancestor(distance).assign(name.lexeme, value)

