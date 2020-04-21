'''
This stand-alone program generates Expr.py and Stmt.py, the two syntax-tree
class modules. Refer to book Section 5.2.2.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

Nystrom uses this program to save the "tedious" work of writing 21
subclasses, each of which is mostly a data class, its only behaviour being
the visit<classname>() method.

Nystrom places his generateAst program in a separate directory but that is
because it is part of its own Java "package". There's no semantic benefit to
putting it in a separate directory in Python, so I'm leaving it with all the
other code.

Note that the dataclasses library module of Python 3 could simplify a little
of the following work, but not enough to justify the extra coding.

'''
from typing import List, TextIO

'''
The following is the template for the opening of the modules Expr.py and
Stmt.py. Note it can't be an f-string because those are evaluated where
defined. At this point master_class is not defined so an undefined name error
would when the module was loaded. The string will be filled in using the
.format() method.
'''
TEMPLATE = '''
# {master_class}.py defines the class {master_class} and its
# subclasses that make up one abstract syntax tree.

# This code is automatically generated (see make_ASTs.py), *DO NOT EDIT*.

#This work is licensed under a
#  Creative Commons Attribution-NonCommercial 4.0 International License
#  see http://creativecommons.org/licenses/by-nc/4.0/

from Token import Token
from typing import List

class {master_class}:
\tdef accept(self,visitor:object):
\t\traise NotImplementedError("Forgot something?")
'''
'''
The following are templates for the start and end of one subclass in either
module.
'''
SUBTEMPLATE1 = '''
class {subclass}({master_class}):
\tdef __init__(self, {args} ):
\t\t# initialize attributes
'''
SUBTEMPLATE2 = '''
\tdef accept(self, visitor:object):
\t\treturn visitor.visit{subclass}(self)
'''

'''

The subclasses to be defined are specified here as a list of strings.
Each string defines one subclass in the form
    classname : type varname [, type varname]*
The strings here were made by editing Nystrom's GenerateAST.java.

'''

EXPRS = [
      "Assign   : Token name, Expr value",
      "Binary   : Expr left, Token operator, Expr right",
      "Call     : Expr callee, Token paren, List[Expr] arguments",
      "Get      : Expr object, Token name",
      "Grouping : Expr expression",
      "Literal  : object value",
      "Logical  : Expr left, Token operator, Expr right",
      "Set      : Expr object, Token name, Expr value",
      "Super    : Token keyword, Token method",
      "This     : Token keyword",
      "Unary    : Token operator, Expr right",
      "Variable : Token name"
    ]
STMTS = [
    "Block      : List[Stmt] statements",
    "Expression : Expr expression",
    "Function   : Token name, List[Token] params, List[Stmt] body",
    "If         : Expr condition, Stmt thenBranch, Stmt elseBranch",
    "Print      : Expr expression",
    "Return     : Token keyword, Expr value",
    "Var        : Token name, Expr initializer",
    "While      : Expr condition, Stmt body",
    "Class      : Token name, List[Function] methods, Expr.Variable=None superclass"
    ]


def make_one_tree( f:TextIO, master_class:str, sub_list:List[str] ):
    # build string so I can inspect it while debugging
    head = TEMPLATE.format(master_class=master_class)
    # feed string to file
    f.write(head)
    # fugly hack here: Stmt needs another import
    if master_class == 'Stmt':
        f.write('import Expr\n')
    for subspec in sub_list :
        subclass, arg_str = subspec.split(':')
        subclass = subclass.strip()
        signature = []
        for onearg in arg_str.split(','):
            tname, vname = onearg.split()
            signature.append(
                    "{0}:{1}".format(vname.strip(),tname.strip())
                            )
        sub_start = SUBTEMPLATE1.format(
            subclass=subclass,
            master_class=master_class,
            args = ','.join(signature)
            )
        f.write(sub_start)
        for arg in signature:
            vname = arg.split(':')[0]
            f.write(f"\t\tself.{vname} = {vname}\n")
        f.write(
            SUBTEMPLATE2.format(subclass=subclass)
            )

if __name__ == '__main__':
    import sys
    from pathlib import Path
    usage = 'usage: python make_ASTs.py path_to_directory'
    if len(sys.argv) != 2 :
        print(usage)
        sys.exit(-1)
    p = Path(sys.argv[1])
    if p.is_dir() :
        f1 = open('Expr.py','w',encoding='UTF8')
        make_one_tree(f1, 'Expr', EXPRS)
        f1.close()
        f2 = open('Stmt.py','w',encoding='UTF8')
        make_one_tree(f2, 'Stmt', STMTS)
        f2.close()
    else:
        print(usage)
