'''

The Parser class for plox. Refer to book section 6.2ff.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''

'''
Import the TokenType lexeme names, e.g. COMMA, WHILE, etc..
This is probably not the last time the choice not to use an Enum for those names
will byte me: when type-annotating methods that take one of these, I can't write
blah(self, ttype:TokenType) but have to write blah(self,ttype:int).
'''
from TokenType import * # all the names of lexemes

from Token import Token
from typing import Callable, List, Union, Optional
import Expr # refer to Expr.Expr, Expr.Binary, etc.

'''
The Parser class implements a recursive descent parser, section 6.2.2, with
error handling as sketched in 6.3.3.

Note that as with the Scanner class, I am having the error reporting function
passed in. This is mainly because Python cross-module references are not as
convenient as Java inter-package-file references. (But also good practice
IMHO.) For the challenge of the error functions, see plox.py line 100ff.

The Parser class code processes a list of Tokens as produced by Scanner.py,
converting it to a tree of Expressions

TBS: wherefore statements?
TBS: how is error handling actually done, in Java and in Python?


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
    Initiate parsing of the list of tokens given us at initialization.
    This is the single input to the Parser (as of 6.3.3).
    '''
    def parse(self) -> Optional[Expr.Expr]:
        try:
            return self.expression()
        except Parser.ParseError:
            return None
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
    def check(self, ttype:int) -> bool :
        if self.isAtEnd(): return False
        return ttype == self.peek().type
    '''
    5. advance: return the current token and advance the pointer.
    '''
    def advance(self) -> Token:
        if not self.isAtEnd() :
            self.current += 1
        return self.previous()
    '''
    6. Check current token against possible matches. Consume a matched token
    and return True; return False if none match.
    '''
    def match(self, *types:int)->bool:
        for ttype in types:
            if (self.check(ttype)):
                self.advance()
                return True
        return False
    '''
    7. Require a particular token type, consume it if found, if not, report
    an error. Currently this is the only method that calls self.error().
    '''
    def consume(self, ttype:int, message:str) -> Token:
        if self.check(ttype):
            return self.advance()
        self.error(self.peek(),message)
    '''
    8. Actually report an error. In the book this method RETURNS the exception
       instead of raising ("throwing") it. Maybe in a later chapter that will
       be made clear. One hopes.
    '''
    def error(self, a_token:Token, message:str) -> ParseError:
        self.error_report(a_token, message)
        raise Parser.ParseError(message)
    '''
    9. Discard tokens until the next token is a likely statement beginning.
       Where this is called and when, TBS.
    '''
    def synchronize(self):
        # begin by stepping over the token that caused the parser to choke
        self.advance()
        while not self.isAtEnd() :
            # Stop skipping if we are at end of statement (semicolon)...
            if self.previous().type == SEMICOLON:
                return;
            # ... or if at a token that starts a new block or statement,
            if self.peek().type in (CLASS,FUN,VAR,FOR,IF,WHILE,PRINT,RETURN) :
                return;
            # otherwise, keep swallowing...
            advance();

    '''
    Actual parsing! See grammar above.
    1. Process the expression by deferring to equality
    '''
    def expression(self)->Optional[Expr.Expr]:
        return self.equality()
    '''
    2. Process the equables: comparable (op comparable)*
    '''
    def equality(self)->Expr.Expr:
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
    def comparison(self)->Expr.Expr:
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
    def addition(self)->Expr.Expr:
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
    def multiplication(self)->Expr.Expr:
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
    def unary(self)->Expr.Expr:
        if self.match(BANG,MINUS):
            operator = self.previous() # capture the !/-
            rhs = self.unary()
            return Expr.Unary(operator, rhs)
        return self.primary()
    '''
    7. pick up the pieces: literals and groups.

    Note that literal() is a property of the Token type, the getter for the
    value passed in as the "literal" parameter when the Token was made.

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
    def primary(self)->Expr.Expr:
        if self.match(FALSE): return Expr.Literal(False)
        if self.match(TRUE):  return Expr.Literal(True)
        if self.match(NIL):   return Expr.Literal(None)
        if self.match(NUMBER,STRING):
            return Expr.Literal(self.previous().literal)
        '''
        And finally: we must be seeing a left paren, which will contain an
        expression and must be followed by a right paren. What happens if it
        isn't? Hah, then we are into error reporting hell, because the whole
        error handling situation is a ball of arcane Java-specific TBS.

        What will this code do, one asks, given input of "()"? It will
        receive a token list of [LEFT_PAREN,RIGHT_PAREN,...]; thus it will
        call self.expression to process the list [RIGHT_PAREN,...]. That will
        fail the match(LEFT_PAREN) test resulting in an error. So the null
        grouping is not supported by Lox.

        '''
        if self.match(LEFT_PAREN):
            grouped_expr = self.expression()
            self.consume(RIGHT_PAREN,
                         "Expected ')' after expression"
                         )
            return Expr.Grouping(grouped_expr)
        '''
        Currently no support for identifiers.
        '''
        '''
        This is where we end up if there is a binary operator without a
        left argument, e.g. /5 or (!=3). Per challenge 3, detect that.
        Note that BANG and MINUS have been dealt with in unary() above.
        If one of those is not followed by a valid rhs, it is the following
        character that drops through to here.
        '''
        bad_token = self.peek()
        if bad_token.type in (PLUS,SLASH,STAR,EQUAL,GREATER,LESS) :
            self.error(bad_token,'operator requires a left operand')
        '''
        Control should never reach here.
        '''
        self.error(bad_token,'Unanticipated input')
