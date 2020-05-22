'''

# The Parser class Llox.

Refer to book section 6.2ff.

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
    Define a private exception class based on the standard SyntaxError. See
    error() for use. Refer to this as Parser.ParseError().
    '''
    class ParseError(SyntaxError):
        def __init__(self,a_token:Token,message:str):
            self.error_token = a_token
            self.error_message = message

    '''
    Define the essentially arbitrary limit on function arguments as a class var.
    Per section 10.1.1 it's 255, but here we can reduce it for testing.
    '''
    Max_Args = 16
    '''
    Initialize a new Parser instance, receiving a list of tokens as
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
    Initialize a tuple of the declaration keyword types, see statement()
    '''
    declarators = (CLASS,FUN,VAR)
    '''
    Top level, and only, entry to this code: Initiate parsing of the list of
    tokens given us at initialization. The result of successful parsing is a
    list of Stmt objects to execute.
    '''
    def parse(self) -> Optional [Stmt.Stmt]:
        results = [] # List[Stmt.Stmt]
        try:
            while not self.isAtEnd():
                results.append(self.declaration())
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
    U2. previous: last-consumed token, for when you get somewhere
        via match(), which consumes the matched token, and you need
        to quote it in an error message.
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
    U7. Check for a particular token type and consume it if found. If no match,
    report an error.
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
    Chapter 9, revised in 10.3.

        program           → declaration* EOF

        declaration       → class_declare
                          | fun_declare
                          | var_declare
                          | statement

        class_declare     → "class" IDENTIFIER ( "<" IDENTIFIER )?
                          | "{" function* "}"
        fun_declare       → 'fun' function
        function          → IDENTIFIER "(" parameters? ")" block
        parameters        → IDENTIFIER ( "," IDENTIFIER )*
        var_declare       → 'var' IDENTIFIER (= expression)? ';'

        statement         → for_statement
                          | if_statement
                          | print_statement
                          | return_statement
                          | while_statement
                          | break_statement
                          | block
                          | expr_statement

        for_statement     → "for" "(" ( varDecl | exprStmt | ";" )
                            expression? ";"
                            expression? ")" statement
        if_statement      → "if" "(" expression ")" statement ( "else" statement )?
        print_statement   → "print" expression ";"
        return_statement  → "return" expression? ";"
        while_statement   → "while" "(" expression ")" statement
        break_statement   → "break" ";"
        block             → "{" declaration* "}"
        expr_statement    → expression ";"
    '''
    '''
    S0. Top of the grammar: Declaration statements. Make a quick check for
        the three keywords, which are the minority of statements, to move
        on to regular statements.
    '''
    def declaration(self, in_loop=False) -> Stmt.Stmt:
        try:
            if not self.peek().type in Parser.declarators:
                # it isn't VAR etc, so get normal statement
                return self.statement(in_loop=in_loop)
            # statement is one of the declarators, which?
            if self.match(CLASS): # see and consume "class"
                return self.class_decl() # process the rest
            if self.match(FUN): # consume FUN token,
                return self.function("function") # process the rest
            if self.match(VAR):
                return self.var_stmt()
            raise NotImplementedError
        except Parser.ParseError as PEX:
            self.error_report(PEX.error_token, PEX.error_message)
            self.synchronize()
            return None
    '''
    SS0. Absorb one ordinary statement through ';' .
    '''
    def statement(self, in_loop=False) -> Stmt.Stmt:

        if self.match(FOR):
            return self.for_stmt(in_loop=in_loop)
        if self.match(IF):
            return self.if_stmt(in_loop=in_loop)
        if self.match(PRINT):
            return self.print_stmt()
        if self.match(RETURN):
            return self.return_stmt()
        if self.match(WHILE):
            return self.while_stmt(in_loop=in_loop)
        if self.match(BREAK):
            return self.break_stmt(in_loop=in_loop)
        if self.match(LEFT_BRACE):
            return Stmt.Block( self.block(in_loop=in_loop) )
        # None of the above, assume expression statement
        return self.expr_stmt()
    '''
    SS1. Absorb a block, which is any declarations to a '}'
         Note an empty block is allowed; return can be [].
    '''
    def block(self, in_loop=False) -> List[Stmt.Stmt]:
        stmts = []
        while (not self.check(RIGHT_BRACE)) and (not self.isAtEnd()) :
            stmts.append( self.declaration(in_loop=in_loop) )
        self.consume(RIGHT_BRACE, "Expect '}' after block.")
        return stmts
    '''
    SDC. Absorb all of a class declaration.
    '''
    def class_decl(self):
        name = self.consume(IDENTIFIER, "Expect class name.")
        superclass = None
        if self.match(LESS) :
            self.consume(IDENTIFIER, "Expect superclass name.")
            superclass = Expr.Variable(self.previous())
        self.consume(LEFT_BRACE, "Expect '{' before class body.")
        methods = []
        while (not self.isAtEnd()) and (not self.check(RIGHT_BRACE)):
            methods.append( self.function("method") )
        self.consume(RIGHT_BRACE, "Expect '}' to close class declaration.")
        return Stmt.Class(name,methods,superclass)

    '''
    SD1. Process a function declaration. Depending on context the
         expected var is either "function" or "method".
    '''
    def function(self, expected:str)->Stmt.Function:
        name = self.consume(IDENTIFIER, f"Expect {expected} name")
        self.consume(LEFT_PAREN, f"Expect '(' after {expected} name")
        parameters = []
        while not self.check(RIGHT_PAREN):
            # next token is not ')' so s.b. a parameter name
            if len(parameters) > Parser.Max_Args :
                self.error(self.peek(),
                    f"Cannot have more than {Parser.Max_Args} parameters.")
            parameters.append(
                self.consume(IDENTIFIER,"Expect parameter name")
                )
            if not self.match(COMMA):
                break # not a comma, probably a ')' but exit loop regardless
            # we did see a comma, continue the loop
        self.consume(RIGHT_PAREN,"Expect ')' to close parameter list")
        self.consume(LEFT_BRACE,
                     f"Expect block statement as {expected} body" )
        body = self.block() # block and not in a loop
        return Stmt.Function(name,parameters,body)

    '''
    SD2. Var statement. Doesn't nest, so doesn't care about in_loop.
    '''
    def var_stmt(self) -> Stmt.Var:
        name = self.consume(IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(EQUAL):
            initializer = self.expression()
        self.consume(SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)
    '''
    SSf. For statement, which is an abomination but here we go.

    Nystrom's approach is "de-sugaring", converting the higher-level statement
    to its lower-level equivalent. In the case of "for(init;test;post) body;"
    we construct:
         { init; while (test) {body; post;} }
    Okayyyy but I think there will be problems with error messages...
    '''
    def for_stmt(self, in_loop=False)->Stmt.Block:
        ''' at this point we have matched FOR, check ( '''
        self.consume(LEFT_PAREN,"Expect '(' after 'for'")
        '''
        next is either "var...;" or "expression;" or just ";". Initially I was
        testing that the var stmt contained a non-null initializer, but
        that technically is not an error. You could have "for (var foo;...)"
        which doesn't make much sense but could work as long as the test
        expression doesn't refer to foo.
        '''
        init_Stmt = None
        if not self.match(SEMICOLON): # match() consumes a naked ';'
            if self.match(VAR):
                init_Stmt = self.var_stmt() # consumes the ';'
            else:
                init_Stmt = self.expr_stmt() # also consumes ';'
        '''
        next is a possibly-empty test expression followed by ';'
        '''
        test_Expr = Expr.Literal(True) # for(...;;...) loops forever
        if not self.check(SEMICOLON) : # look for, do not eat, ';'
            test_Expr = self.expression() # does not consume ';'
        self.consume(SEMICOLON, "expect ';' after loop condition") # now!
        '''
        and then an optional post-loop expression before the ')' -- Nystrom
        calls it the increment, which it almost always is.
        '''
        post_Expr = None
        if not self.check(RIGHT_PAREN):
            post_Expr = self.expression()
        self.consume(RIGHT_PAREN, "expect ')' to close for(...)")
        '''
        finally, gather the body of the loop, a single statement, (typically
        a block but who knows?) which is definitely in a loop.
        '''
        body_Stmt = self.statement(in_loop=True)
        '''
        put it all together in a single statement. I coded this before seeing
        what Nystrom does, and his was better so I changed it. I was always
        building a block, with possibly null init/post statements. That
        required a change in the Interpreter to allow null statements in a
        block. I didn't see, initially, that if the init or test or post
        items are left out, I could just build simpler statements.

        Body of the loop is either a single statement, or two statements
        in a block, the second being the increment.
        '''
        loop_body = body_Stmt
        if post_Expr : # is given, make loop body a block
            loop_body = Stmt.Block( [body_Stmt, Stmt.Expression(post_Expr)] )
        ''' the loop is that body, conditioned by the test expression '''
        loop_Stmt = Stmt.While(test_Expr,loop_body)
        ''' if there is an initializer, we need to put the loop in a block '''
        if init_Stmt:
            loop_Stmt = Stmt.Block( [init_Stmt,loop_Stmt] )
        return loop_Stmt

    '''
    SS1. If statement. Note that the "greedy" ELSE match ensures that the
         ELSE of a nested IF is paired with its nearest IF.
    '''
    def if_stmt(self,in_loop=False)->Stmt.If:
        self.consume(LEFT_PAREN,"'(' required for if-condition")
        condition = self.expression()
        self.consume(RIGHT_PAREN,"')' expected after if-condition")
        then_clause = self.statement(in_loop=in_loop)
        else_clause = None
        if self.match(ELSE): # Grab an else right now
            else_clause = self.statement(in_loop=in_loop)
        return Stmt.If(condition,then_clause,else_clause)
    '''
    SS2. Print statement. Doesn't nest, doesn't care about in_loop.
    '''
    def print_stmt(self)->Stmt.Print:
        expr = self.expression()
        self.consume(SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(expr)
    '''
    SSr. Return statement. Doesn't nest. Expression is optional,
         but semicolon is not. Note as in the book, if there is
         no explicit expression, Expr.value is actually None, as
         opposed to Expr.Literal with value None.
    '''
    def return_stmt(self)->Stmt.Return:
        keyword = self.previous() # save for Stmt
        value = None # default return value
        if not self.check(SEMICOLON):
            value = self.expression()
        self.consume(SEMICOLON,"Expect semicolon after 'return'")
        return Stmt.Return(keyword, value)

    '''
    SS3. While statement.
    '''
    def while_stmt(self, in_loop=False)->Stmt.While:
        self.consume(LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(RIGHT_PAREN, "Expect while condition to close with ')'.")
        body = self.statement(in_loop=True)
        return Stmt.While(condition, body)
    '''
    SSb. Break statement. Syntax error if not in_loop.
    '''
    def break_stmt(self, in_loop)->Stmt.Break:
        if not in_loop:
            self.error(self.previous(),"Break statement only allowed within a loop.")
        self.consume(SEMICOLON, "Expect ';' after 'break'.")
        return Stmt.Break(self.previous())
    '''
    SS9. Expression statement. Doesn't nest, doesn't know in_loop.
    '''
    def expr_stmt(self)->Stmt.Expression:
        expr = self.expression()
        self.consume(SEMICOLON, "Expect ';' after value.")
        return Stmt.Expression(expr)

    '''
    Expression parsing! For reference, this is the expression grammar to be
    parsed (as modified in section 8.4.1 to include assignment) (as modified
    in 9.3 to wrap "equality" inside the logical operators) (as modified in
    10.1 to support function calls) (as modified in 12.3 for properties):

    sequence       → expression ( , expression )*
    expression     → assignment ;
    assignment     → (call "." )? IDENTIFIER "=" assignment
                   | logic_or
    logic_or       → logic_and ( "or" logic_and )*
    logic_and      → equality ( "and" equality )*
    equality       → comparison ( ( "!=" | "==" ) comparison )*
    comparison     → addition ( ( ">" | ">=" | "<" | "<=" ) addition )*
    addition       → multiplication ( ( "-" | "+" ) multiplication )*
    multiplication → unary ( ( "/" | "*" ) unary )*
    unary          → ( "!" | "-" ) unary | call
    call           → primary ( "(" arguments? ")" | "." IDENTIFIER )*
    arguments      → expression ( "," expression )*
    primary        → "true" | "false" | "nil" | "this"
                   | NUMBER | STRING | IDENTIFIER |
                   | "(" expression ")"
                   | "super" "." IDENTIFIER

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
        possible_lhs = self.logic_or()
        '''
        If the next token is not "=", we are done, with an expression.
        '''
        if not self.match(EQUAL):
            return possible_lhs
        '''
        We have "something =" so note the location of the "=" for a possible
        later error message; then collect the r-value.
        Note the recursion; We take a = b = c as a = (b = c).
        '''
        error_pos = self.previous()
        rhs = self.assignment()
        '''
        Now ask, We have something =, but is it variable = or property?
        '''
        if isinstance(possible_lhs, Expr.Variable):
            return Expr.Assign(possible_lhs.name, rhs)
        if isinstance(possible_lhs, Expr.Get):
            return Expr.Set(possible_lhs.object, possible_lhs.name, rhs)
        '''
        Neither, flag an error at the "=" token noted earlier.
        '''
        self.error(error_pos, "Invalid target for assignment")

    '''
    E1a. Process logic-or.
    '''
    def logic_or(self)->Expr.Expr:
        possible_lhs = self.logic_and()
        while self.match(OR):
            operator = self.previous() # save that OR token
            rhs = self.logic_and()
            possible_lhs = Expr.Logical(possible_lhs,operator,rhs)
        return possible_lhs
    '''
    E1b. Process logic-and.
    '''
    def logic_and(self)->Expr.Expr:
        possible_lhs = self.equality()
        while self.match(AND):
            operator = self.previous()
            rhs = self.equality()
            possible_lhs = Expr.Logical(possible_lhs,operator,rhs)
        return possible_lhs

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
        return self.call()
    '''
    E7. process the call, property-reference, and other unaries.
        The loop allows for cases like
            get_fun().meth()()(obj.field)
        in which the first call yields a class instance whose
        method meth() returns a function that yields a function
        that takes the field value of obj.
    '''
    def call(self)->Expr.Expr:
        an_expr = self.primary()
        while True:
            if self.match(LEFT_PAREN):
                an_expr = self.finish_call(an_expr)
            elif self.match(DOT):
                name = self.consume(IDENTIFIER,
                            "Expect property name after '.'")
                an_expr = Expr.Get(an_expr,name)
            else:
                break
        return an_expr

    def finish_call(self, callee:Expr.Expr)->Expr.Call:
        # we are here because we've seen callee( -- don't leave without ')'
        args = []
        # there are only 3 ways out of this loop: seeing a ')' at an
        # appropriate place, or somebody raises an error exception.
        while not self.check(RIGHT_PAREN):
            # next token is not ')'
            args.append( self.expression() )
            # expression complete: next token is not legal as an expression
            if len(args) >= Parser.Max_Args:
                raise Parser.ParseError(self.peek,f"Function may not have {len(args)} arguments")
            self.match(COMMA) # if it is a comma, eat it
            # next token is not comma: could be start of expression, or ')'
        # next token is ')' without question
        rparen = self.consume(RIGHT_PAREN,"This message cannot be displayed")
        return Expr.Call(callee, rparen, args)

    '''
    E8. pick up the pieces: literals and groups.

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
        if self.match(THIS):  return Expr.This(self.previous())
        if self.match(SUPER):
            keyword = self.previous() # save "super" token
            self.consume(DOT, "Expect '.' after 'super'")
            method_name = self.consume(IDENTIFIER,
                            "Expect superclass method name.")
            return Expr.Super(keyword,method_name)
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
