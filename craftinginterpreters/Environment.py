'''

# Environment

Environment ("symbol table") class for plox. Refer to book section 8.3

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

## Overview

The Lox Environment is a set of nested dictionaries. Each dict has a member
'enclosing' which is the dictionary that represents its enclosing (more
global) scope at runtime. The Java implementation overloads the instantiation
call to pass or not pass an enclosing dict; here we use an optional parameter
to __init__.

Where in Java, a dictionary (aka "mapping") is a library, in Python it is a
built-in class. So unlike the Java version, here we make Environment a
subclass of Python "dict". To implement the Lox operations get() and assign()
we just call on the dict class operations __contains__, __getitem__, and
__setitem__. That should make the Environment methods quite performant.

To implement the BREAK statement, both WHILE and BLOCK support set and query
a named variable in the local scope. To simplify their operations, the
fetch() and store() methods are factored out of the methods assign() and
get() from the Java implementation.

## The Environment API:

    Environment(enclosing=None)

        Create an empty environment. If no enclosing, this is the global
        scope. Otherwise this environment is a relatively local scope to the
        enclosing one.

    define(name:str, value:object):

        Set name to value in this environment. Name need not exist. Name
        will shadow any equal name in an enclosing environment.

    fetch(name:str)->object

        Return the value of name from its closest (most local) definition.
        Raise NameError if not found.

    get(name:Token)->object

        Return value of name.lexeme from its closest (most local) definition.
        Raise NameError if not found. Uses fetch().

    store(name:str, value:object)

        Set name to value in the nearest environment where it is defined.
        Raise NameError if name is not known.

    assign(name:Token, value:object)

        Set name.lexeme to value in the nearest environment where it is
        defined. Raise NameError if it is not known. Uses store().

    ancestor(distance:int) -> Environment

        Return the nth enclosing (more global) Environment, 0 being this one.
        No check of valid distance. If distance too high by 1, will return
        None. If too high by >1, causes an error "'Nonetype' object has no
        attribute 'ancestor'".

    assignAt( distance:int, name:Token, value:object)

        Assign value to Token.lexeme in the nth more global environment. Uses
        ancestor() and assign().

    getAt( distance:int, name:Token ) -> object

        Return value of Token.lexeme from the nth more global environment.
        Uses ancestor() and get().

## Errors

In a normal Python dict, fetching a key that doesn't exist raises KeyError.
But here when a name is not found, it is an undefined Lox variable, so we
raise NameError instead, as Python would for an undefined var.

##A Puzzle

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
strings from most local to most global, separated by ->. But what are the strings
assigned to "result" and punctuated with '->'?

In Python the equivalent (I think) is str(the_dict) which returns
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
    otherwise raise NameError.

    Code executing an expression comes to get() with a Token for the name.
    Internal code, esp. visitWhile, comes to fetch() with a string name. Note
    also that the recursion to the more global scope is done via fetch(),
    saving a few .lexeme de-references when fetching a more global name.
    '''
    def get(self, name:Token)->object:
        return self.fetch(name.lexeme)

    def fetch(self, name:str)->object:
        if self.__contains__(name):
            return self.__getitem__(name)
        if self.enclosing is not None: # note an empty dict is falsey
            return self.enclosing.fetch(name)
        # We are the global scope and we don't have this name.
        # Raise a NameError exception with the name string in the "args".
        raise NameError(name)

    '''
    Assign a value (any object) to a name, if the name is defined in this or
    an enclosing scope, otherwise NameError. As with assign, we have two
    levels, assign() to extract Token.lexeme, and store() to do the work.
    '''
    def assign(self, name:Token, value:object):
        self.store(name.lexeme, value)

    def store(self, name:str, value:object):
        if self.__contains__(name):
            self.__setitem__(name,value)
        elif self.enclosing is not None:
            self.enclosing.store(name,value)
        else:
            # we are the global scope and we don't have it
            raise NameError(name)
    '''
    Define (as in "var name = expr;") a value at this scope level.

    Note that while get() and assign() receive the name in the form of a
    Token, this method gets the name as a string. Note also that we do not
    check whether the name has already been defined; see book section 8.3 for
    that discussion.
    '''
    def define(self, name:str, value:object):
        self.__setitem__(name,value)

    '''
    Return our enclosing scope at a certain integer remove. As of this
    writing I have not got to the book's discussion for this feature.

    This is the code I am translating, it appears to allow distance==0
    and to not check for over-run.

        Environment ancestor(int distance) {
        Environment environment = this;
        for (int i = 0; i < distance; i++) {
          environment = environment.enclosing; // [coupled]
        }
        return environment;

    I went for the recursive one-line solution below. Possibly I will have
    to change that later in the book.

    Coding note: this method is annotated as returning the self-class
    Environment. Prior to Python 3.7 that was not possible as that name has
    not been defined until this class definition is closed. "from __future__
    import annotations" fixes this in 3.7 and 3.8; in Python 3.9 it will be
    fixed permanently.
    '''

    def ancestor(self, distance:int)->Environment:
        return self.enclosing.ancestor(distance-1) if distance>0 else self

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
    def getAt(self, distance:int, name:Token ) -> object:
        return self.ancestor(distance).get(name)

    def assignAt(self, distance:int, name:Token, value:object):
        self.ancestor(distance).assign(name, value)

