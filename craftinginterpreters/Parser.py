'''

The Parser class for plox. Refer to book section 6.2ff.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''
from TokenType import * # all the names of lexemes e.g. COMMA, WHILE, etc.
from Token import Token
from typing import Callable, List, Union
import Expr # refer to subclasses as Expr.Binary, etc.

'''
The Parser class implements a recursive descent parser, section 6.2.2

Note that as with the Scanner class, I am having the error reporting function
passed in. This is mainly because Python cross-module references are not as
convenient as Java inter-package-file references. (But also good practice
IMHO.) For the challenge of the error functions, see plox.py line 100ff.

It processes a list of Tokens as produced by Scanner.py, converting it
to a tree of Expressions

TODO: wherefore statements?
TODO: what is the return type, if any, and from which method?


For reference, this is the expression grammar to be parsed:

    expression     → equality ;
    equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    comparison     → addition ( ( ">" | ">=" | "<" | "<=" ) addition )* ;
    addition       → multiplication ( ( "-" | "+" ) multiplication )* ;
    multiplication → unary ( ( "/" | "*" ) unary )* ;
    unary          → ( "!" | "-" ) unary
                   | primary ;
    primary        → NUMBER | STRING | "false" | "true" | "nil"
                   | "(" expression ")" ;

'''

class Parser:

    '''
    Define a parser error class based on the standard SyntaxError.
    See Parser.error()
    '''
    class ParseError(SyntaxError):
        pass

    def __init__(self, tokens:List[Token],error_report:Callable[[Token,str],None]):
        # save the list of tokens
        self.tokens = tokens
        # save the error reporter
        self.error_report = error_report
        # initialize our index to the next Token to eat
        self.current = 0
    '''
    Utility functions for parsing.
    1. peek: current token without advancing
    '''
    def peek(self) -> Token:
        return self.tokens[self.current]
    '''
    2. previous: last-consumed token; obvs. not to be called before advance()
    '''
    def previous(self) -> Token:
        return self.tokens[self.current-1]
    '''
    3. isAtEnd: are we on the final token, which must be an EOF?
    '''
    def isAtEnd(self) -> bool:
        return EOF == self.peek()
    '''
    4. check: return truth of current token has a given type.
       n.b. "type" is reserved, well actually not reserved but
       unwise to override it.
    '''
    def check(self, ttype:TokenType) -> bool :
        if self.isAtEnd(): return False
        return ttype == self.peek().type()
    '''
    5. advance: return the current token and advance the pointer.
    '''
    def advance(self) -> Token:
        if not self.isAtEnd() :
            self.current += 1
        return self.previous()
    '''
    6. Check current for possible matches. Consume a matched token and return
    True, or False if none match.
    '''
    def match(self, *types:TokenType)->bool:
        for ttype in types:
            if (self.check(ttype)):
                self.advance()
                return True
        return False
    '''
    7. Require a particular token type, consume it if found, if not, report
    an error. At this point the flow of control in the case of an error is
    very unclear. TBA.
    '''
    def consume(ttype:TokenType, message:str) -> Token:
        if self.check(ttype):
            return self.advance()
        self.error(self.peek,message)
    '''
    8. Actually report an error. Should this
    '''
    def error(token:Token, message:str) -> ParseError:
        self.error_report(Token, message)
        return ParseError(message)
    '''
    Actual parsing! See grammar above.
    1. Process the expression by deferring to equality
    '''
    def expression(self)->Expr:
        return self.equality
    '''
    2. Process the equables: comparable (op comparable)*
    '''
    def equality(self)->Expr:
        result = self.comparison()
        while self.match(BANG_EQUAL,EQUAL_EQUAL):
            # capture the != or == that successful match stepped over
            operator = self.previous()
            rhs = self.comparison()
            result =  Expr.Binary(result, operator, rhs)
        return result
    '''
    3. process the comparables: addable (op addable)*
    '''
    def comparison(self)->Expr:
        result = self.addition()
        while self.match(GREATER,GREATER_EQUAL,LESS,LESS_EQUAL):
            # capture the one of those, that match stepped over
            operator = self.previous()
            rhs = self.addition()
            result =  Expr.Binary(result, operator, rhs)
        return result
    '''
    4. process the multables: multable (op multable)*
    '''
    def addition(self)->Expr:
        result = self.multiplication()
        while self.match(MINUS,PLUS):
            # capture the -/+ that a successful match stepped over
            operator = self.previous()
            rhs = self.multiplication()
            result =  Expr.Binary(result, operator, rhs)
        return result
    '''
    5. process the unaries: unary (op unary)*
    '''
    def multiplication(self)->Expr:
        result = self.unary()
        while self.match(SLASH,STAR):
            # capture the / or * that a successful match stepped over
            operator = self.previous()
            rhs = self.unary()
            result =  Expr.Binary(result, operator, rhs)
        return result
    '''
    6. process the primaries: ([!-]primary)*primary
    '''
    def unary(self)->Expr:
        if self.match(BANG,MINUS):
            operator = self.previous() # capture the !/-
            rhs = self.unary()
            return Expr.Unary(operater, rhs)
        return self.primary()
    '''
    7. pick up the pieces: literals and groups.

    Note that literal() is a property of the Token type, the getter for the
    value passed in as the literal parameter when it was made.

    Note also that this is the basement of the recursive ladder. It only
    returns a value when there is a match to one of the ttypes it checks for.
    Ergo all possible Expression token types must be checked-for here, or
    above here. A token type not mentioned will simply be ignored,
    self.current will not advance.

    Those possibilities include: LEFT_BRACE, FUN, RETURN and etc. Presumably
    such token types will be dealt with at a higher level, as part of parsing
    statements.

    Note 3: here, as also in Scanner.py, I am substituting Python None for
    the Java literal null -- to represent the Lox literal nil.
    '''
    def primary(self)->Expr:
        if self.match(FALSE): return Expr.Literal(False)
        if self.match(TRUE):  return Expr.Literal(True)
        if self.match(NIL):   return Expr.Literal(None)
        if self.match(NUMBER,STRING):
            return Expr.Literal(self.previous().literal)
        '''
        And finally: we must be seeing a left paren, which will contain an
        expression and must be followed by a right paren.

        What will this code do, one asks, given input of "()". It will
        receive a token list of [LEFT_PAREN,RIGHT_PAREN]; thus it will call
        self.expression to process the list RIGHT_PAREN. That will pass
        through this code like shit through a goose, and return the Python
        default of None.

        That will result in Expr.Grouping(None), creating a Grouping instance
        G in which "G.expression is None". So that is a possibility that any
        code that processes Groupings will have to handle.
        '''
        if self.match(LEFT_PAREN):
            grouped_expr = self.expression()
            self.consume(RIGHT_PAREN,
                         "Expected ')' after expression"
                         )
            return Expr.Grouping(grouped_expr)
