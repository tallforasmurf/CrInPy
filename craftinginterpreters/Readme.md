What is this?
===============

This repo contains my version of code found in the book CRAFTING INTERPRETERS by Bob Nystrom. I'm reading from the online text found at https://craftinginterpreters.com.

The book teaches via building an interpreter for a small language Lox, first in Java, then in C. The source for these along with the book are found in Nystrom's repository at https://github.com/munificent/craftinginterpreters

The purpose of this project is to translate the Java code into Python, first as a way to prove I understand the book, and second to have something to do while in CV Quarantine. I'm also finding it a great refresher course in Python. (In fact, I come into this knowing a little something about interpreters. Most recently I've prowled around the internals of CPython and made a Python 3 version of [Byteplay](https://github.com/tallforasmurf/byteplay), a tool for playing with Python's byte-code. Plus, my first real software development experience was helping implement [APL\360](https://en.wikipedia.org/wiki/APL_(programming_language)#APL\360). Where I expect this book to teach me something new, is in the use of a syntax tree, and more general parsing and compiling, and software design techniques I've never had to use.)


Direct quotes from Nystrom's work are kept to a minimum, and only used when explaining how or why I did something differently than he, or otherwise want to comment on the book. Hopefully that keeps me within "fair use" bounds. When anything is unclear, refer to Nystrom's book or repository for explanations.

My own text and Python code has
License:<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.

Chapter 4
==========

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

Chapter 5
===========

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

Generating ASTs(*sic*) (Section 5.2.2)
------------------------

Nystrom generates the two modules Expr and Stmt automatically, using one-time code `GenerateAst`. It basically defines a little DSL; a table of definitions for the 20-odd subclasses of the abstract classes `Expr` and `Stmt`. I have repeated that work in Python, calling it `make_AST`. (Pedantically speaking, the ASTs are in fact the dynamic tree-structured collections of instances of `Expr` and `Stmt` that are created at runtime, not the classes that compose them. But whatever.)

In making this I ran into a couple of J-to-P issues. First, the two created modules are part of the `craftinginterpreters` Java package. As a result, they can freely invoke each other. Two Python modules can't unless they explicitly import each other. Actually, only `Stmt.py` has to refer to the `Expr` class and one time to its subclass `Expr.Variable`.

To make that happen, I had to insert an ugly hack. I generate the head of each module, including its prolog, its top class definition (`Expr` or `Stmt`) and its few needed imports, from a single, triple-quoted string. Because they are the same, except for the master class-name. But thanks to `Stmt` referencing `Expr`, it needs one more `import`. So I have a nasty `if master_class == "Stmt"` to add that line to the common header string.

The Java code has explicit types for all arguments; yay Java. Python's equivalent is the typing module, with exact analogs. For example where the Java code has an argument type of `List<Token> varname`, I could generate `varname:List[Token]`. So it was a small matter to edit Nystrom's list of subclass definitions into a Python list with the same meanings.

With one exception. Java apparently allows class overloading as well as function overloading, where it picks the subclass to instantiate based on the signature of the initialization call. So Nystrom has two versions of the `Class` statement, one instantiated with, and one without, the superclass name. At least, that's what I infer from these definition lines:

```
/* Classes class-ast < Inheritance superclass-ast
      "Class      : Token name, List<Stmt.Function> methods",
*/
//> Inheritance superclass-ast
      "Class      : Token name, Expr.Variable superclass," +
                  " List<Stmt.Function> methods",
```

Actually, the simpler one is commented out, and only the longer one appears in `Stmt.java` in the repo. So maybe he introduces the shorter version early and replaces it with the longer? But why then would you add the new parameter in the middle, rather than the end of the signature? Whatever; I covered the bases by moving the superclass to the third position and making it optional,

```
class Class(Stmt):
	def __init__(self, name:Token,methods:List[Function],superclass:Expr.Variable=None ):
```

This may come back to bite me later? Maybe. Also, isn't it good that Python syntax is case-sensitive? Because `class` is a reserved word but we can define `class Class` (not to mention `class If` and `class Return`) and all is good.

Anyway, on with learning about ASTs. ASTerisks. ASTers. ASTronomics?

Not Very Pretty Printer (Section 5.4)
--------------------------------------

I call foul! In this section, Nystrom writes code to visit a tree and print its contents. But we have not seen any code whatever for *building* a tree. We've seen the classes that will be the nodes of the tree, and we've talked about the Visitor Pattern as a way of processing a tree in various ways *after it's built* -- but we have not seen any code for building one.

In particular, we have not seen the code that takes a list of Token objects, as produced by our scanner in the prior chapter, and parse them and convert them into Expr subclasses. But still he wants us to write code for a PrintVisitor, with no way of testing it, other than to hand-code assembly of a tree.

Not gonna do it. I'll proceed on to the parsing chapter, and maybe revisit the printer problem when I have a tree built.

Chapter 6
===========

Java optional arguments
-----------------------

An important utility function in the parser is `match()` defined so:

```
private boolean match(TokenType... types) {
    for (TokenType type : types) {
      if (check(type)) {
        advance();
        return true;
      }
    }
    return false;
```

Hello! Multiple arguments. Interesting to me, the syntax puts the ellipsis on the *type*, which I guess says "TokenType and maybe more TokenType" although in English it could mean, "TokenType and maybe Salad or Dessert". Never mind that, how does Python do this? I know it involves an asterisk... time for a review of the docs!

Oh of course, it's star-args, and they can be type-annotated. So the Python equivalent is:

```
def match(self, *types:TokenType)->bool:
    for ttype in types:
        if (self.check(ttype)):
            self.advance()
            return True
    return False
```

Easy, except for the irritation that, because all the Parser machinery is methods of a class, every damn method call has to have `self.` in front of it, and every parameter list starts with `self`.

Parser Error Handling (Section 6.3, see also The Scanner above)
----------------------------------------

With the parser we are getting into more sophisticated error handling than in the scanner, and I am finding Nystrom's methods a bit on the opaque side. First there's the use of Java `throw` as in the `consume` method.

```
private Token consume(TokenType type, String message) {
    if (check(type)) return advance();
    throw error(peek(), message);
}
```

Whu? Is that like Python `raise` which definitely initiates a stack unwind to the nearest handler? Apparently not because he says that is going to (somehow?) invoke

```
private ParseError error(Token token, String message) {
    Lox.error(token, message);
    return new ParseError();
  }
```

So `throw` is actually a call? The called `error` refers to the error method in the top level module. I already worked around that with the scanner, by passing `Plox.error` when instantiating the Scanner. Well and good, but *this* call to `error` uses a different signature than that one (first arg is a Token not a line#). Java overloading again. So I split that function into two, one for the scanner and one for the parser.

Problem still is, what happens when the `error()` method exits, returning a ParseError. Nystrom says

> The error() method returns it instead of throwing because we want to let the caller decide whether to unwind or not.

But *who is the caller?* If it's `consume()` then it might return a Token (`return advance()`) or it might return a ParseError which is in no way compatible with the Token class. If it isn't `consume()` then where is the code that is supposed to decide what to do? No clue!

Hah! Looking back I see that Nystrom's code never makes use of the return value of `consume()`. Once it sees a left paren it *always* returns a Grouping object. Which must mean, it is relying on that magical `throw` verb to prevent control from every returning from a mismatch to the right paren. But I cannot fathom where he expects execution to continue; and where the returned ParseError instance would ever be of use.

The ParseError class itself is easy enough to translate, it is just

    class ParseError(SyntaxError)
        pass

Thus a Python Exception derived from one of the standard exceptions. But should it be returned or should it be raised? Time may tell.

Error handling rant (Section 6.3.2)
-------------------------------------

Sorry Mr. Nystrom, this section, for the non-Java programmer, is a puzzler. I've just been reading a [tutorial on Java Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/index.html) and it is just very hard to match up what the book is advocating, to what Oracle says is possible or conventional.

An important source of confusion (at least, mine) is the multiple, ambiguous uses of the identifier `error`: as the name of a function in the main Lox module (which turns out to be an overloaded version of *another* function `error`), and as the name of an instance of an exception class, a class that isn't defined until further down the page.

So the parser method `consume()` throws something called `error` which turns out to be an instance of something called `ParseError`, I'm sort of on board here; but this class instance contains *executable code that calls the `error` in a completely different module using a new signature. But when is that call executed?

From Python I'm quite used to the idea of raising exceptions, where an exception is an instance of a subclass from an heirarchy of exceptions. No problemo. But I am not used to the idea of an *exception instance* containing executable code:

```
private ParseError error(Token token, String message) {
    Lox.error(token, message);                           
    return new ParseError();                             
  }                                                      
```

N.B. the Oracle [tutorial on creating exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/creating.html) says  nothing about an exception subclass having properties of *any* kind, let alone code. So, where, in what context, is that call to `Lox.error()` going to be executed? And to what caller is it returning a new instance of itself? And why would it do that?

Error Handling clarification (Section 6.3.3)
--------------------------

Ok the above confusions get somewhat straightened out in the final section of the chapter, by whichI mean (a) he explains something he's been withholding and (b) it gets to look a lot more like Python.

The big problem through all of 6.3.1 and 6.3.2 was it was not at all clear how this code was called, what top-level function could receive ("catch") an exception generated below. That finally gets sorted out; the Parser class gets a method `parse()` in which is --*Hello!* -- a simple `try` statement to begin parsing and handle a generated error.

That removed a lot of the confusion, although there remains the issue of a Java Exception instance having executable code, and also this sentence which still makes absolutely no sense to me:

>  The error() method *returns* it [the exception] instead of *throwing* because we want to let the caller decide whether to unwind or not.

I think the problems I've had here, have pointed out a basic problem with Nystrom's pedagogy. He has worked all this out and coded it; now he is trying to introduce the code in bits as he explains the concepts. But that leads to the very awkward problem of trying to introduce thought-out design elements before the context in which they'll sit is shown. It's the major strategy of his book, and here it just led an experienced programmer to all sorts of confusion. Literally you need to read this chapter twice: once quickly to grasp the theory and the structure; then, after you understand the context they plug into, a second time to see the details.

I think he should rewrite the latter half of the chapter: Start by introducing the Parser class skeleton including the `parse()` method with its `try` block. Then go back and fill in the details of it.

Another issue: he ends the chapter by bringing the Parser class to a runnable state; that's fine. But in order to test it he says, 

> we can hook up our brand new parser to the main Lox class and try it out... for now, we’ll parse to a syntax tree and then use the `AstPrinter` class from the last chapter to display it.

I thought by "last chapter" he meant, the last chapter of the book. There is a module `AstPrinter.java` in the github repo. So I spent several minutes cruising the table of contents to find where it was discussed. Turns out, he meant "prior chapter", the "ugly pretty-printer" exercise that I had skipped over.

Why did I skip over it? Because at that point, the only way I would have to unit-test that code would have been, to cobble up some kind of expression-tree-building scaffold code. Or code a static tree of Expr's in the printer module. Now, a chapter later, I have a nice expression-tree-builder I need to test. Now I need to go and implement that exercise. But again, upside-down pedagogy.

Printer, and Challenges
------------------------

I did the expression printer, taking pains to follow the nice Visitor pattern, see [AstPrinter.py](https://github.com/tallforasmurf/CrInPy/blob/master/craftinginterpreters/AstPrinter.py). It will be easy to expand it to print other things as we add statements to the AST.

However, the top part of it, the meta-class `astVisitor` is potentially useful for other "visitations" to the AST. Soon I am going to want to pull that out to a separate module, and make the AstPrinter import it. Then I can write other types of visitors importing `astVisitor`.

I also implemented challenge #1, the comma operator; and challenge #3, giving a separate error message for a binop that lacks a left hand value.











