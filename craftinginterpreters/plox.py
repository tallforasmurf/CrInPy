'''

Main entry to the Lox interpreter.
Refer to book section 4.1 and forward

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''

import sys
from Scanner import Scanner
from Parser import Parser
from Token import Token
from TokenType import *
from Expr import Expr
from AstPrinter import AstPrinter
from Interpreter import Interpreter

# Syntax/parsing error detection flag. See book, sect. 4.1.1
#   set: report() run_prompt()
#   tested: run_file()
HAD_ERROR = False

def main():
    '''
    Top level of plox: if invoked with a single file path, execute the
    contents of that file. Invoked with no file, go into interactive mode.
    '''
    num_args = len(sys.argv)
    if num_args > 2 :
        # more than 1 command argument, ergo confused user
        print('Usage: plox [script]')
        # with some research I find that Unix exit code 64
        # is EX_USAGE, command line usage error. TIL!
        sys.exit(64)
    elif num_args == 2 : # one argument, hopefully a path to a script
        run_file(sys.argv[1])
    else: # no argument
        run_prompt()
    # and out

def run_file( fpath:str ):
    '''
    Get the contents of a Lox source file. If an error opening the file,
    abort with error code 66, EX_NOINPUT.

    Pass the file as a single string to run_lox. If it reports an error,
    abort the program with code 65, EX_DATAERR
    '''
    #print('running file at',fpath)
    try: # to open the file as UTF_8 text
        f = open(fpath,mode='r',encoding='utf_8')
    except Exception as E:
        print('problem accessing',fpath)
        print(E)
        sys.exit(66)
    run_lox(f.read())
    if HAD_ERROR : sys.exit(65)

def run_prompt():
    global HAD_ERROR
    '''
    Prompt the user for a line of Lox code. Stop on KeyboardInterrupt (^c) or
    EOFError (^d). When stopping, print something with a newline so as not to
    mess up the command line in the terminal window.

    Pass each line to run_lox for execution. After running the line, clear
    the global HAD_ERROR.
    '''
    #print('prompting for code now')

    while True:
        try:
            line_in = input('> ')
        except EOFError:
            print("\nk thx byeee")
            sys.exit()
        except KeyboardInterrupt:
            print()
            sys.exit()
        run_lox(line_in)
        HAD_ERROR = False

    # end while


def run_lox(lox_code:str):
    print('executing:',lox_code)
    scanner = Scanner(lox_code,lex_error)
    tokens = scanner.scanTokens()
    #for token in tokens:
        #print(token)
    parser = Parser(tokens, parse_error)
    # parse() now returns a list of statements, not tokens.
    program = parser.parse()
    if not HAD_ERROR:
        # no error, so program is in fact [Stmt...]
        interpreter = Interpreter(parse_error)
        print('executing!...\n')
        interpreter.interpret(program)

'''
The book provides (at least?) two variations of the function error():
one in section 4.1.1 for reporting scanner errors, which takes a line number;
and one in section 6.3.2 for reporting parser errors, which takes a Token.
Nystrom depends on Java function overloading to work out which to call.

Python not so much. Now it would be possible to write a single Python function
error whose first argument could be *either* an int or a Token, but that would
be I think more ugly than what I'm doing, defining two functions.

lex_error is called from the Scanner with a line number, a message, and an
optional character position.
'''

def lex_error(line:int, message:str, where:int=None):
    report(line,  f"chr {where}" if where else "", message)

'''
parse_error is called by the Parser with a Token from which both the line number and the operator
character are extracted, and a message.
'''

def parse_error(a_token:Token, message:str):
    report(a_token.line,
           "at " + (a_token.lexeme if (a_token.type != EOF) else "end"),
           message)

'''
interpret_error is called by Interpreter with a Token and a message. Only the
line number is extracted from the Token. Not the lexeme, hence a different
function is needed. I don't know why in this case he avoids displaying the
token.lexeme. I believe I will do so by passing parse_error instead.
'''
#def interpret_error(a_token:Token, message:str):
    #report(a_token.line, a_token.lexeme, message)

'''
Here recreate the following Java from section 4.1.1

private static void report(int line, String where, String message) {
    System.err.println(
        "[line " + line + "] Error" + where + ": " + message);
    hadError = true;
  }

Note that Nystrom is using the (to me, dubious) practice of setting
a global variable which is interrogated at a number of points in his
main module Lox.java.
'''
def report(line:int, where:str, message:str):
    global HAD_ERROR
    print(
        f"Error in line {line} {where}: {message}",
        file=sys.stderr
        )
    HAD_ERROR = True

if __name__ == '__main__' :

    main()