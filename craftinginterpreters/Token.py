'''

Token class for plox. Refer to book section 4.2.3

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

This is the Java class to be replicated.

class Token {
  final TokenType type;
  final String lexeme;
  final Object literal;
  final int line; // [location]

  Token(TokenType type, String lexeme, Object literal, int line) {
    this.type = type;
    this.lexeme = lexeme;
    this.literal = literal;
    this.line = line;
  }

public String toString() { return type + " " + lexeme + " " + literal; } }
First question is, what is the Python equivalent of the Java adjective
"final", which means, "read-only once it has been initialized". The answer
is: the @property decorator with a getter method, see
(https://docs.python.org/3/library/functions.html#property)

Second question: WTF is the type "Object"? It has not been mentioned or
defined in a snippet as of this book section. OK, it's just Java for
"instance of a class". In other words, same as Python's "object". Doh!

A third question is, do we need to implement the toString() method? It would
be more Pythonic to instead implement a __str__() method on the class. I'm
doing both, so I can use str(token), but if I omit to convert a toString()
call in the copied code, it will still work.

===== TODO:

This is the first place (undoubtedly not the last) where Java can refer to
TokenType as a type, where I implemented it as integers. Also, in the __str__
it returns the type, which will just be an int instead of a name like COMMA.
That's not good. Maybe TokenType should be an Enum after all...

'''

class Token:
    def __init__(self, type:int, lexeme:str, literal:object, line:int):
        self._type=type
        self._lexeme = lexeme
        self._literal = literal
        self._line = line
    @property
    def type(self): return self._type
    @property
    def lexeme(self): return self._lexeme
    @property
    def literal(self): return self._literal
    @property
    def line(self): return self._line
    def toString(self):
        return str(self)
    def __str__(self):
        return f"{self._type} {self._lexeme} {self._line} {self._literal}"