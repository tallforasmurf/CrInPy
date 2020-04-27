'''

The Parser class for plox. Refer to book section 6.2ff.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''

from TokenType import * # all the names of lexemes
from Token import Token
import Expr # refer to Expr.Expr, Expr.Binary, etc.
import Stmt # refer to Stmt.Stmt, Stmt.Function, Stmt.Block, etc.
from typing import Callable, List, Union, Optional

'''
The Parser class implements a recursive descent parser, section 6.2.2, with
error handling as sketched in 6.3.3.

Note that as with the Scanner class, I am having the error reporting function
passed in. This is mainly because Python cross-module references are not as
convenient as Java inter-package-file references. (But also good practice
IMHO.) For the challenge of the error functions, see plox.py line 100ff.

This version is now modified to handle Statements, see Chapter 8.2ff.

'''

class Parser:

    '''
    Define a parser error class based on the standard SyntaxError.
    See Parser.error(). Refer to this as Parser.ParseError().
    '''
    class ParseError(SyntaxError):
        def __init__(self,a_token:Token,message:str):
            self.error_token = a_token
            self.error_message = message

    '''
    Initialize a new Parser instance passing a list of tokens as
    produced by Scanner.py, and an error reporting function.
    '''
    def __init__(self, tokens:List[Token],error_report:Callable[[Token,str],None]):
        # save the list of tokens
        self.tokens = tokens
        # save the error reporter
        self.error_report = error_report
        # initialize our index to the next Token to eat
        self.current = 0

    '''
    Initialize a tuple of the declaration keywords, see statement()
    '''
    declarators = (CLASS,ELSE,FUN,FOR,IF,VAR,WHILE)
    '''
    Top level and only external entry to this code: Initiate parsing of the
    list of tokens given us at initialization.
    '''
    def parse(self) -> Optional [Stmt.Stmt]:
        results = [] # List[Stmt.Stmt]
        try:
            while not self.isAtEnd():
                results.append(self.declaration() )
        except Parser.ParseError as PEX:
            self.error_report(PEX.error_token, PEX.error_message)
            results = None
        return results # here's the return!

    '''
    Utility functions for parsing.
    U1. peek: get current token without advancing
    '''
    def peek(self) -> Token:
        return self.tokens[self.current]
    '''
    U2. previous: last-consumed token; obvs. not to be called before advance()
    '''
    def previous(self) -> Token:
        return self.tokens[self.current-1]
    '''
    U3. isAtEnd: are we on the final token, which must be an EOF?
    '''
    def isAtEnd(self) -> bool:
        return EOF == self.peek().type
    '''
    U4. check: return truth of current token has a given type.

    n.b. in Python, "type" is reserved, well actually not reserved but unwise
    to override it.
    '''
    def check(self, ttype:int) -> bool :
        if self.isAtEnd(): return False
        return ttype == self.peek().type
    '''
    U5. advance: return the current token and advance the pointer.
    '''
    def advance(self) -> Token:
        if not self.isAtEnd() :
            self.current += 1
        return self.previous()
    '''
    U6. Check current token against possible matches. Consume a matched token
    and return True; return False if none match.
    '''
    def match(self, *types:int)->bool:
        for ttype in types:
            if (self.check(ttype)):
                self.advance()
                return True
        return False
    '''
    U7. Require a particular token type, consume it if found, if not, report
    an error. Currently this is the only method that calls self.error().
    '''
    def consume(self, ttype:int, message:str) -> Token:
        if self.check(ttype):
            return self.advance()
        self.error(self.peek(),message)
    '''
    U8. Actually report an error. In the book this method RETURNS the exception
       instead of raising ("throwing") it. Maybe in a later chapter that will
       be made clear. One hopes.
    '''
    def error(self, a_token:Token, message:str) -> ParseError:
        raise Parser.ParseError(a_token,message)
    '''
    U9. Discard tokens until the next token is a likely statement beginning.
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
            self.advance();
    '''
    Statement parsing! For reference, this is the statement grammar as of
    Chapter 8.2.1:

        program           → declaration* EOF

        declaration       → var_declare
                          | statement
                          # etc TBS

        var_declare       → 'var' IDENTIFIER (= expression)? ';'

        statement         → expr_statement
                          | print_statement
                          # etc TBS
        expr_statement    → expression ';'
        print_statement   → "print" expression ';'
        # etc TBS
    '''
    '''
    S0. Top of the grammar: Declaration statements.
    '''
    def declaration(self) -> Stmt.Stmt:
        try:
            if not self.peek().type in Parser.declarators:
                # it isn't VAR etc, so get normal statement
                return self.statement()
            if self.match(VAR):
                return self.var_stmt()
            # other declaration keywords TBS
            raise NotImplementedError
        except Parser.ParseError as PEX:
            self.error_report(PEX.error_token, PEX.error_message)
            self.synchronize()
            return None
    '''
    SS0. Absorb one ordinary statement through ';' .
    '''
    def statement(self) -> Stmt.Stmt:
        if self.match(PRINT):
            return self.print_stmt()
        # other statement keywords TBS
        # None of the above, assume expression statement
        return self.expr_stmt()
    '''
    SD1. Var statement
    '''
    def var_stmt(self) -> Stmt.Stmt:
        name = self.consume(IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(EQUAL):
            initializer = self.expression()
        self.consume(SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)

    '''
    SS1. Print statement.
    '''
    def print_stmt(self)->Stmt.Print:
        expr = self.expression()
        self.consume(SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(expr)
    '''
    SS2. Expression statement.
    '''
    def expr_stmt(self)->Stmt.Expression:
        expr = self.expression()
        self.consume(SEMICOLON, "Expect ';' after value.")
        return Stmt.Expression(expr)

    '''
    Expression parsing! For reference, this is the expression grammar to be parsed
    (as modified in section 8.4.1 to include assignment):

    sequence       → expression ( , expression )*
    expression     → assignment ;
    assignment     → IDENTIFIER "=" assignment
                   | equality;
    equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    comparison     → addition ( ( ">" | ">=" | "<" | "<=" ) addition )* ;
    addition       → multiplication ( ( "-" | "+" ) multiplication )* ;
    multiplication → unary ( ( "/" | "*" ) unary )* ;
    unary          → ( "!" | "-" ) unary
                   | primary ;
    primary        → NUMBER | STRING | IDENTIFIER | "false" | "true" | "nil"
                   | "(" expression ")" ;

    E0. Process a sequence of expressions, Challenge 1.
       My approach is, when comma is present, to make a binary Expr with
       operator COMMA and the first Expr as lhs, and the second, which
       may itself turn out to be a COMMA, as the rhs.
    '''
    def sequence(self)->Expr.Expr:
        result = self.expression()
        while self.match(COMMA):
            operator = self.previous() # save the COMMA token
            rhs = self.sequence() # and around we go!
            result = Expr.Binary(result, operator, rhs)
        return result
    '''
    E0. Process the expression by deferring to assignment.
    '''
    def expression(self)->Expr.Expr:
        return self.assignment()
    '''
    E1. Process what may or may not be an assignment expression.
    '''
    def assignment(self)->Expr.Expr:
        '''
        Suck up what might be an assignment target, or might be an expression.
        '''
        possible_lhs = self.equality()
        '''
        If the next token is not "=", we are done, with an expression.
        '''
        if not self.match(EQUAL):
            return possible_lhs
        '''
        Now ask, We have something =, but is it variable =?
        '''
        if not isinstance(possible_lhs, Expr.Variable):
            # flag an error at the "=" token, which is previous
            self.error(self.previous(), "Invalid target for assignment")
        '''
        We have variable = something, collect the r-value.
        Notice the recursion? We take a = b = c as a = (b = c).
        '''
        rhs = self.assignment()
        return Expr.Assign(possible_lhs.name, rhs)

    '''
    E2. Process the equables: comparable (op comparable)*
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
    E3. process the comparables: addable (op addable)*
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
    E4. process the multables: multable (+/- multable)*
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
    E5. process the unaries: unary (*// unary)*
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
    E6. process the primaries: [!-]primary
    '''
    def unary(self)->Expr.Expr:
        if self.match(BANG,MINUS):
            operator = self.previous() # capture the !/-
            rhs = self.unary()
            return Expr.Unary(operator, rhs)
        return self.primary()
    '''
    E7. pick up the pieces: literals and groups.

    Those possibilities include: LEFT_BRACE, FUN, RETURN and etc. Presumably
    such token types will be dealt with at a higher level, as part of parsing
    statements.

    Note 3: here, as also in Scanner.py, I am substituting Python None for
    the Java literal null -- to represent the Lox literal nil.
    '''
    def primary(self)->Expr.Expr:
        if self.match(IDENTIFIER):
            # IDENTIFIER token contains a word, make it into an Expr
            return Expr.Variable(self.previous())
        # handle the keyword values
        if self.match(FALSE): return Expr.Literal(False)
        if self.match(TRUE):  return Expr.Literal(True)
        if self.match(NIL):   return Expr.Literal(None)
        # handle literal values
        if self.match(NUMBER,STRING):
            return Expr.Literal(self.previous().literal)
        '''
        The only remaining legitimate option is a left paren, which will
        contain an expression and must be followed by a right paren.

        What would this code do, one asks, given input of "()"? As Nystrom
        wrote it (through Chapter 8, maybe it gets improved later?) it will
        look at the token list of [LEFT_PAREN,RIGHT_PAREN,...]; it will call
        self.expression to process the list [RIGHT_PAREN,...], and will fall
        through to be an error below. Thus Lox doesn't support the null
        expression.

        I am changing this to recognize "()" and return "(nil)".

        '''
        if self.match(LEFT_PAREN):
            if self.peek().type == RIGHT_PAREN:
                grouped_expr = Expr.Literal(None)
            else:
                grouped_expr = self.expression()
            self.consume(RIGHT_PAREN,
                         "Expected ')' after expression"
                         )
            return Expr.Grouping(grouped_expr)
        '''
        This is the basement of the recursive ladder. It only returns a value
        when there is a match to one of the ttypes it checks for. Ergo all
        possible Expression token types must be checked-for here, or above
        here. A token type not explicitly checked-for ends up at this error.

        This is also where we end up, if there is a binary operator without a
        left argument, e.g. /5 or (!=3). Per challenge 3, detect that. Note
        that BANG and MINUS have been dealt with in unary() above. If one of
        those is not followed by a valid rhs, it is the following character
        that drops through to here.
        '''
        bad_token = self.peek()
        if bad_token.type in (PLUS,SLASH,STAR,EQUAL,GREATER,LESS) :
            self.error(bad_token,'operator requires a left operand')
        '''
        Finally we just don't know what's going on.
        '''
        self.error(bad_token,'Unanticipated input')
