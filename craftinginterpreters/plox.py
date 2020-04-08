'''

Main entry to the Lox interpreter.
Refer to book section 4.1

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''

import sys

def main():
    '''
    Top level of plox: if invoked with a single file path,
    execute the contents of that file. Invoked with no file,
    go into interactive mode.
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
    Get the contents of a Lox source file and pass it to run_lox
    '''
    #print('running file at',fpath)
    try: # to open the file as UTF_8 text
        f = open(fpath,mode='r',encoding='utf_8')
    except Exception as E:
        print('problem accessing',fpath)
        print(E)
        sys.exit(78)
    run_lox(f.read())

def run_prompt():
    '''
    Prompt the user for lines of Lox code.
    Pass each line to run_lox for execution.
    Stop on KeyboardInterrupt (^c) or EOFError (^d).
    When stopping, print something with a newline so as not to
    mess up the command line in the terminal window.
    '''
    #print('prompting for code now')

    while True:
        try:
            line_in = input('> ')
        except EOFError:
            print("\nthx byeee")
            sys.exit()
        except KeyboardInterrupt:
            print("\n")
            sys.exit()
        run_lox(line_in)
    # end while


def run_lox(lox_code:str):
    print('executing:',lox_code)


if __name__ == '__main__' :
    main()