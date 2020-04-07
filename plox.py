'''

Main entry to the Lox interpreter.
Refer to book section 4.1

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''

import sys

def main():
    num_args = len(sys.argv)
    if num_args > 2 :
        # more than 1 argument, ergo confused user
        print('Usage: plox [script]')
        # with some research I find that Unix exit code 64
        # is EX_USAGE, command line usage error. TIL.
        sys.exit(64)
    elif num_args == 2 :
        # one argument, presumably path to a script
        run_file(sys.argv[1])
    else:
        # no argument, go to interactive mode
        run_prompt()
    # and out

def run_file( fpath:str ):
    print('running file at',fpath)

def run_prompt():
    print('prompting for code now')


if __name__ == '__main__' :
    main()