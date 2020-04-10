'''

Enumeration of token types.
Refer to book section 4.2.1

I'm making these simple integer globals, as that approximates the
Java/C enum type better than Python's Enum metaclass. See Readme.

This work is licensed under a
  Creative Commons Attribution-NonCommercial 4.0 International License
  see http://creativecommons.org/licenses/by-nc/4.0/

'''
# Single-character tokens.
LEFT_PAREN = 1
RIGHT_PAREN = 2
LEFT_BRACE = 3
RIGHT_BRACE = 4
COMMA = 5
DOT = 6
MINUS = 7
PLUS = 8
SEMICOLON = 9
SLASH = 10
STAR = 11
# One or two character tokens.
BANG = 12
BANG_EQUAL = 13
EQUAL = 14
EQUAL_EQUAL = 15
GREATER = 16
GREATER_EQUAL = 17
LESS = 18
LESS_EQUAL = 19
#Literals.
IDENTIFIER = 20
STRING = 21
NUMBER = 22
# Keywords.
AND = 23
CLASS = 24
ELSE = 25
FALSE = 26
FUN = 27
FOR = 28
IF = 29
NIL = 30
OR = 31
PRINT = 32
RETURN = 33
SUPER = 34
THIS = 35
TRUE = 36
VAR = 37
WHILE = 38
EOF = 39

TokenNames = {
    1 : "LEFT_PAREN",
    2 : "RIGHT_PAREN",
    3 : "LEFT_BRACE",
    4 : "RIGHT_BRACE",
    5 : "COMMA",
    6 : "DOT",
    7 : "MINUS",
    8 : "PLUS",
    9 : "SEMICOLON",
    10 : "SLASH",
    11 : "STAR",
    12 : "BANG",
    13 : "BANG_EQUAL",
    14 : "EQUAL",
    15 : "EQUAL_EQUAL",
    16 : "GREATER",
    17 : "GREATER_EQUAL",
    18 : "LESS",
    19 : "LESS_EQUAL",
    20 : "IDENTIFIER",
    21 : "STRING",
    22 : "NUMBER",
    23 : "AND",
    24 : "CLASS",
    25 : "ELSE",
    26 : "FALSE",
    27 : "FUN",
    28 : "FOR",
    29 : "IF",
    30 : "NIL",
    31 : "OR",
    32 : "PRINT",
    33 : "RETURN",
    34 : "SUPER",
    35 : "THIS",
    36 : "TRUE",
    37 : "VAR",
    38 : "WHILE",
    39 : "EOF"
    }