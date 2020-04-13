What is this?
===============

This repo contains my version of code found in the book CRAFTING INTERPRETERS by Bob Nystrom. I'm reading from the online text found at https://craftinginterpreters.com.

The book teaches via building an interpreter for a small language Lox, first in Java, then in C. The source for these along with the book are found in Nystrom's repository at https://github.com/munificent/craftinginterpreters

The purpose of this project is to translate the Java code into Python, first as a way to prove I understand the book, and second to have something to do while in CV Quarantine. I'm also finding it a great refresher course in Python. (In fact, I come into this knowing a little something about interpreters. Most recently I've prowled around the internals of CPython and made a Python 3 version of [Byteplay](https://github.com/tallforasmurf/byteplay), a tool for playing with Python's byte-code. Plus, my first real software development experience was helping implement [APL\360](https://en.wikipedia.org/wiki/APL_(programming_language)#APL\360). Where I expect this book to teach me something new, is in the use of a syntax tree, and more general parsing and compiling, and software design techniques I've never had to use.)


Direct quotes from Nystrom's work are kept to a minimum, and only used when explaining how or why I did something differently than he, or otherwise want to comment on the book. Hopefully that keeps me within "fair use" bounds. When anything is unclear, refer to Nystrom's book or repository for explanations.

My own text and Python code has
License:<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.

Java vs Python modules (Section 4.1)
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

Error Handling (Section 4.1.1)
-------------------------

Nystrom is using a program global, hadError, set in various places and tested in others. Not sure I like this, but whatever. At least, Python makes the use of a global more obvious, first by the convention of using an all-cap name HAD\_ERROR, second by having to write `global HAD_ERROR` in any function that sets it. Points to Python.

Token Types (Section 4.2.1)
---------------------------

A new Java/Python problem arises. The book uses an enum for the 35 or so token types. I started to make that a Python Enum, but the Python Enum is a pitiful thing. It's a class, so any reference to an enumerated value can't be just its name, but the qualified name. So given

    class TokenType(Enum):
        LEFT_PAREN = auto()
        ... etc

the code can't just refer to `LEFT_PAREN`, it has to say `TokenType.LEFT_PAREN` which is just ugly. Explicit, but ugly. (Points to Java/C.) Plus I don't know if the Java enums are effectively ints, and if so, whether at some point the book won't try to compare token types for greater or less. So maybe I should use an IntEnum, but that requires me to specify each int value (the auto() initializer isn't allowed). Bleagh. I'm going to make them globals of the TokenType module initialized to unique ints.

Token (Section 4.2.3)
-----------------

This class uses the Java keyword `final`, which I learn means "read-only after initialization". OK, Python has that in the `@property` decorator, so the equivalent of

    class Token {
        final TokenType type
        ...}

is 

    class Token():
        def __init__(self, type,...)
            self._type = type # note leading underscore
        ...
        @property
        def type(self): return self._type

A bit more awkward, for sure. OTOH, the Java class implements a rather verbose `toString()` method, while I can just override the default `__str__()` method for the same output.

However, the class initializer can specify its token type argument as a type, where (see above) mine are just ints. Also its `toString()` can display `type` as its name e.g. COMMA where mine can't, without I set up some kind of name-to-value map. I need to rethink the use of Enum for TokenType.

The Scanner (Sections 4.5-4.7)
----------------------------

I have implemented the complete code now, and run it successfully against the simple lexeme test files in Nystrom's repo. I made one significant change. In his Scanner.java, the scanner reports errors by invoking `Lox.error()`, a function defined in the main module. I copied the `error()` function in my plox.py module. However, it isn't practical for code in Scanner.py to refer back to plox.py. Python namespaces don't work that way.

In section 4.1.1 Nystrom says,

> Ideally, we would have an actual abstraction, some kind of "ErrorReporter" interface that gets passed to the scanner and parser so that we can swap out different reporting strategies.

So I did that; i.e. I changed Scanner so that besides a string of text it accepts a reference to an error reporting function. In plox.py I pass the `error` reference so Scanner can call it in the two (2) places it reports an error. Also I extended error reporting to include not just a line number but a character position in the line. That required noting the source index of the latest newline seen, so that the offset into that line could be calculated. Trivial extra code.

I changed the error reporting for string literals as well. There's really only one possible error in a string, the absence of a terminator. That won't be found until the scanner has sucked up all the text to EOF. At which point it reports the error as happening on the line number where EOF happened. Which could be a long way from where the orphan opening quote was. So I saved the line number and start position of the opening quote, and when reporting the "unterminated quote" error, give that position, not the EOF position.

Visitor Pattern (Sections 5.2-3)
----------------------

Oh boy, my first real learning moment. He shows this snippet,

```
abstract class Expr { 
  static class Binary extends Expr {
    Binary(Expr left, Token operator, Expr right) {
      this.left = left;
      this.operator = operator;
      this.right = right;
    }
    final Expr left;
    final Token operator;
    final Expr right;
  }
```

Nothing exciting there, since I understand the idea of an abstract base class being subclassed (or in Java terms, extended). But before I start recoding this in Python I want to see the surrounding stuff to get an idea what module it's in, what other pieces there will be etc. That's what I did for the Scanner in the previous section. And here's what I find, lightly edited:

```
abstract class Expr {
  interface Visitor<R> {
    R visitAssignExpr(Assign expr);
    R visitBinaryExpr(Binary expr);
    ...and a bunch more like that...
  }
  // Nested Expr classes here...

  static class Binary extends Expr {
    Binary(Expr left, Token operator, Expr right) {
      this.left = left;
      this.operator = operator;
      this.right = right;
    }
    @Override
    <R> R accept(Visitor<R> visitor) {
      return visitor.visitBinaryExpr(this);
    }
```

OK, I have *heard* of the "visitor" pattern but never read code using it. Is this how it is implemented? WTF is that leading `R` and `<R> R` business? Is that some kind of macro substitution thing? And how's it done in Python? Which I shouldn't ask, since I don't yet know what "it" is.

So off I go to read about [the Visitor Pattern](https://en.wikipedia.org/wiki/Visitor_pattern), bless you Wikipedia for including a complete Python example! Which starts by importing a module `abc` which I'd never heard of (but yes, it's in the standard lib). And ending with a truly arcane formula for Python 3, an abstract implementation of the `accept()` method that is definitely heavily dependent on CPython internals.

Yup, that will be all for today, students. I must go and think on this.

In the small hours of the night I was pondering this and thought, come on, surely Nystrom is going to explain some of this. Just read ahead. And yes he does; section 5.3 is a detailed backgrounder on the Visitor pattern and why it's useful for our AST. I worked some of this out in the depths of the night. We will have our tree composed of varied subclasses of `Expr`. In several different instances we would want to pass over the tree, visiting every element, to do some related task for each, for example:

* to print the tree, displaying each element
* to execute the code, performing the action mandated by each
* to generate code for each element, if we were compiling it

and even, one or more optimization tours, in which we look for elements that can be eliminated or combined. For example, if both arguments to a binary operator are literals, to replace it with the known result. Now *that* case would be a rather intrusive "visitor" because it might not just *visit* a node but *replace* the node. Not sure if the Visitor Pattern covers that. But onward, to read and understand Nystrom's text.

Except for one thing: he doesn't explain the peculiar syntax of the lines like

    R visitBinaryExpr(Binary expr);
    <R> R accept(Visitor<R> visitor) 

He does say,

> We can’t assume every visitor class wants to produce the same type, so we’ll use generics to let each implementation fill in a return type.

Is that a "generic"? Something else Java-related to read up on.

(Next day) I have absorbed the basics of the Visitor Pattern and have written it up for my own pleasure, see visitor\_pattern.md in this repo. Also in that note are comments on the contrasting implementations between Java and Python. Then I implemented the code from the wiki article, see visitortest.py.








