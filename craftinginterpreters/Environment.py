'''

Environment class for plox. Refer to book section 8.3

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

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

from Token import Token

class Environment(dict, enclosing=None:Environment):
    def __init__(self):
        self.enclosing = enclosing # None if we are the global dict

    '''
    Return the value of a name, if it exists at this or an enclosing scope,
    otherwise raise NameError (not KeyError as a dict would normally do).
    '''
    def get(self, name:Token)->object:
        if self.__contains__(name.lexeme):
            return self.__getitem__(name.lexeme)
        if self.enclosing : # is not None,
            return self.enclosing.get(name)
        # we are the global scope and we don't have it
        raise NameError(f"Undefined variable: {name.lexeme}")

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
            raise NameError(f"Undefined variable: {name.lexeme}")
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
    def getAt( distance:int, name:str ) -> object:
        return self.ancestor(distance).get(name)

    def assignAt( distance:int, name:Token, value:object):
        self.ancestor(distance).put(name.lexeme, value)

