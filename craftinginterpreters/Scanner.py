'''

The Scanner class for plox. Refer to book section 4.4.

Because Java, Nystrom's Scanner class can refer to "Lox.error()" without
having to import or otherwise link the Lox module into its namespace. Python
not so much. Since plox imports this module, this module can't mutually
import plox to access the error() function in it.

So, I am doing what he suggests as a future possibility in 4.1.1, handing the
error-report method as a parameter of the Scanner class init.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/


'''
from TokenType import * # all the names of lexemes e.g. COMMA, WHILE, etc.
from Token import Token
from typing import Callable

class Scanner():
        '''
        The source argument to __init__ is a string of (presumably) Lox code,
        from a single line to a file-full. Also a reference to an error method.

        The Java class uses the "private" keyword, meaning not accessible
        from outside the class code. The Python equivalent is only a
        convention, to name attributes with a leading underscore. Since the
        actual Scanner is a singleton (tsk-tsk, BTW) and the only reason I
        can think of for external code accessing its attributes would be for
        debugging, I am not going to bother with leading underscores.
        '''
        def __init__(self, source:str, error_report:Callable[[int,str],None] ):
                self.error_report = error_report
                self.source = source # source string
                self.tokens = list() # collected tokens
                # initialize the state of the scan
                self.start = 0
                self.current = 0
                self.line = 1
                # factor a call out of the much-used isAtEnd()
                self.source_len = len(source)
                # note char position of each new line, for error displays
                self.last_newline = 0
                '''
                This lengthy dict is the core of a switch statement used in
                scanToken(), see section 4.5. The keys are expected
                characters. Each value is a lambda returning a TokenType.
                Only some of the lambdas contain logic, but all must be
                lambdas so that the result of searching the dict is always an
                executable.
                '''
                self.switch_dict = {
                        '(':lambda: LEFT_PAREN,
                        ')':lambda: RIGHT_PAREN,
                        '{':lambda: LEFT_BRACE,
                        '}':lambda: RIGHT_BRACE,
                        ',':lambda: COMMA,
                        '.':lambda: DOT,
                        '-':lambda: MINUS,
                        '+':lambda: PLUS,
                        ';':lambda: SEMICOLON,
                        '*':lambda: STAR,
                        '!':lambda: BANG_EQUAL if self.look_for('=') else BANG,
                        '=':lambda: EQUAL_EQUAL if self.look_for('=') else EQUAL,
                        '<':lambda: LESS_EQUAL if self.look_for('=') else LESS,
                        '>':lambda: GREATER_EQUAL if self.look_for('=') else GREATER,
                        '/':lambda: SLASH if not self.look_for('/') else None
                        }
                '''
                Dict (== Java Map) converting input keywords to token types
                '''
                self.keywords = {
                        "and":    AND,
                        "class":  CLASS,
                        "else":   ELSE,
                        "false":  FALSE,
                        "for":    FOR,
                        "fun":    FUN,
                        "if":     IF,
                        "nil":    NIL,
                        "or":     OR,
                        "print":  PRINT,
                        "return": RETURN,
                        "super":  SUPER,
                        "this":   THIS,
                        "true":   TRUE,
                        "var":    VAR,
                        "while":  WHILE
                        }

        '''
        Helper functions for scanning the source string
        '''
        def isAtEnd(self)->bool:
                # True when current is no longer a valid index to source
                return self.current >= self.source_len
        def peek(self)->str:
                if self.isAtEnd() : return '\x00'
                return self.source[self.current]
        def peek_next(self)->str:
                if (self.current+1) >= self.source_len: return '\x00'
                return self.source[self.current+1]
        def advance(self)->chr:
                # one hopes, never called when isAtEnd()?
                c = self.source[self.current]
                self.current += 1
                return c
        def look_for(self, c:str)->bool:
                if self.isAtEnd(): return False
                if self.source[self.current] != c :
                        return False
                self.current += 1
                return True
        def addToken(self, type:int, literal:object = None):
                '''
                Create a new Token and append it to our list. In the Java
                this uses overloading to allow for a call that omits the 2nd
                argument. Python uses a default argument for the same effect.
                '''
                lexeme = self.source[self.start:self.current]
                self.tokens.append(
                        Token( type, lexeme, literal, self.line )
                        )

        def scanTokens(self):
                '''
                Scan and collect all the tokens from the source input into
                the list self.tokens. Return self.tokens. This is the only
                entry to Scanner, called from plox.run_lox()
                '''
                while not self.isAtEnd() :
                        self.start = self.current
                        self.scanToken()
                # append a final EOF token
                self.tokens.append(Token(EOF, "", None, self.line));
                return self.tokens;

        def scanToken(self):
                '''
                Collect one lexeme from the input source starting at index
                self.start, advancing self.current. Append the corresponding
                Token to self.tokens

                The book's Java makes use of a switch statement. Here we use
                the somewhat more verbose Python form, a dict whose values
                are executables, initialized in the __init__ function.
                '''
                c = self.advance()
                if c in self.switch_dict :
                        # handle a one- or two-char special character
                        code = self.switch_dict[c]() #execute lambda
                        if code is not None :
                                # normal lexeme, create token
                                self.addToken(code)
                        else:
                                # lexeme is //, swallow comment to end of
                                # line and do not add a token.
                                while not self.isAtEnd()
                                and self.peek() != '\n':
                                        self.advance()
                elif c == '\n' :
                        # note position of next line start, increment the
                        # line count, but produce no token.
                        self.last_newline = self.current
                        self.line += 1
                elif c.isspace() :
                        # discard Unicode whitespace (\n already done)
                        pass
                elif c == '"' :
                        self.string_lit() # build a string literal token
                elif c.isdigit() :
                        self.number_lit() # build a number literal token
                elif c.isidentifier() :
                        # Python's .isidentifier(), applied to a single
                        # character, allows only valid initials of an
                        # identifier, i.e. underscore and alphabetics.
                        self.identifier() # create IDENTIFIER token

                else : # ??
                        self.error_report(self.line, "Unexpected character",
                                          where=self.current-self.last_newline)
        def string_lit(self):
                '''
                Absorb a "literal" string, adding the contents as a token.
                Handle errors like unclosed string. See Section 4.6.1.

                Note there is no support for escapes like \n.

                Lox allows string lits to span newlines. Update self.line
                appropriately when they occur in the string. Note an
                unterminated string won't be detected until end of file,
                potentially, or the start of the next string lit, which will
                lead to a cascade of errors.

                Adding a bit of code to get accurate line/char position of start
                of an unterminated string.
                '''
                start_line = self.line
                start_pos = self.current - self.last_newline
                while not self.isAtEnd() and '"' != self.peek() :
                        if self.peek() == '\n' :
                                self.line += 1
                        self.advance()
                if not self.isAtEnd() :
                        self.advance() # swallow closing quote
                        literal = self.source[ self.start+1 : self.current-1 ]
                        self.addToken(STRING, literal)
                else :
                        # the string wasn't terminated
                        self.error_report(start_line,"Unterminated string",where=start_pos)
        def number_lit(self):
                '''
                Absorb a numeric literal "\d+(\.\d+)?". Book section 4.6.2

                Note that \d+\. alone is not valid, keeping the option of
                methods on numeric values. Also \.\d+ is not supported (the
                dot will end up an "unexpected character".

                First step, bound the literal in source[start:current]
                '''
                while self.peek().isdecimal() : # get leading digits
                        self.advance()
                if self.peek() == '.' and self.peek_next().isdecimal() :
                        self.advance() # step current over the dot
                while self.peek().isdecimal() : # get trailing digits
                        self.advance()
                self.addToken(NUMBER,
                              float(self.source[self.start:self.current])
                              )
        def identifier(self):
                '''
                Absorb a valid identifier string and make a token. Book
                section 4.6. We can't use .isidentifier here because, applied
                to a single char, it doesn't accept digits. So use isalnum
                plus a test for underscore.

                The dict map of keywords to codes is initialized in __init__.

                This while would be a perfect place to use the "walrus"
                operator, but I don't have Python 3.8 yet.
                '''
                while self.peek().isalnum() or self.peek() == '_' :
                        self.advance()
                text = self.source[self.start:self.current]
                # assume it's your average tom, dick or harry
                ttype = IDENTIFIER
                # but if it is actually a keyword, get the right Token code.
                if text in self.keywords :
                        ttype = self.keywords[text]
                self.addToken(ttype)

