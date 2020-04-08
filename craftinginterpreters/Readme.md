What is this?
===============

This repo contains my version of code found in the book CRAFTING INTERPRETERS by Bob Nystrom. I'm reading from the online text found at https://craftinginterpreters.com.

The book teaches via building an interpreter for a small language Lox, first in Java, then in C. The source for these along with the book are found in Nystrom's repository at https://github.com/munificent/craftinginterpreters

The purpose of this project is to translate the Java code into Python, first as a way to prove I understand the book, and second to have something to do while in CV Quarantine.

Direct quotes from Nystrom's work are kept to a minimum, and only used when explaining how or why I did something differently than he, or otherwise want to comment on the book. Hopefully that keeps me within "fair use" bounds. When anything is unclear, refer to Nystrom's book or repository for explanations.

My own text and Python code has
License:<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.

Java vs Python modules (section 4.1)
-------------------

The first problem I run into is understanding how the code of Jlox, the Java interpreter, is structured. (I am hampered in this by not knowing Java!) Every module starts with a `package` statement, for example here are parts of the first snippets the reader is to try to work with.

```Java
package com.craftinginterpreters.lox;
// Java imports omitted
public class Lox {
// omitted
}
private static void run(String source) {
    Scanner scanner = new Scanner(source);
    List<Token> tokens = scanner.scanTokens();

    // For now, just print the tokens.
    for (Token token : tokens) {
      System.out.println(token);
    }
  }
```

The problem comes up with the line `scanner = new Scanner(source);`. At this point in the book we have not defined any Scanner class. Where is it coming from? Given I am supposed to be able to actually run these snippets.

I look around the repo and find `Scanner.java`. From my Python point of view, the code for the Scanner class should be imported, but there's no import naming it.

A little reading about the `package` statement teaches me that since (almost?) every module in the repo has that same `package com.craftinginterpreters.lox`, that means that basically all the module files constitute one big happy module. Since module Scanner.java has the same package statement as this module, it is effectively part of this code. I think.

(Later: the book is ambiguous about whether the code should be executable as of section 4.1. He says "Stick that in a text file, and go get your IDE or Makefile or whatever set up." Does that mean it should run? It certainly can't unless you have duplicated his github repo, or otherwise copied down all his Java code. He didn't say to do that; he just said stick these snippets in your IDE. Not try to run them.)

The package statement tells me that Nystrom's setup has a two-level folder structure. The top level is `craftinginterpreters`, which contains a folder `lox` in which almost all the Java modules live. (Presumably there's a `craftinginterpreters.clox` folder I'll meet later?) OK, I'm going to put all my modules into a similar structure. Because they are all in the same folder, I'll be able to import them individually by name--but I will have to import them, e.g. `import Scanner` to get my Scanner.py module.

I don't think that's a problem, in fact it's an advantage to have the import dependencies of each module explicit.

Error Handling (section 4.1.1)
-------------------------

Nystrom is using a program global, hadError, set in various places and tested in others. Not sure I like this, but whatever. At least, Python makes the use of a global more obvious, first by the convention of using an all-cap name HAD\_ERROR, second by having to write `global HAD_ERROR` in any function that sets it. Points to Python.

Token Types (section 4.2.1)
---------------------------

A new Java/Python problem arises. The book uses an enum for the 35 or so token types. I started to make that a Python Enum, but the Python Enum is a pitiful thing. It's a class, so any reference to an enumerated value can't be just its name, but the qualified name. So given

    class TokenType(Enum):
        LEFT_PAREN = auto()
        ... etc

the code can't just refer to `LEFT_PAREN`, it has to say `TokenType.LEFT_PAREN` which is just ugly. Explicit, but ugly. (Points to Java/C.) Plus I don't know if the Jave enums are effectively ints, and if so, whether at some point the book won't try to compare token types for greater or less. So maybe I should use an IntEnum, but that requires me to specify each int value (the auto() initializer isn't allowed). Bleagh. I'm going to make them globals of the TokenType module initialized to unique ints.
