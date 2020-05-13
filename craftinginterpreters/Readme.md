# What is this?

This repo contains my version of code found in the book CRAFTING INTERPRETERS by Bob Nystrom. I'm reading from the online text found at https://craftinginterpreters.com.

The book teaches via building an interpreter for a small language Lox, first in Java, then in C. The source for these along with the book are found in Nystrom's repository at https://github.com/munificent/craftinginterpreters

The purpose of this project is to translate the Java code into Python, first as a way to prove I understand the book, and second to have something to do while in CV Quarantine. I'm also finding it a great refresher course in Python. (In fact, I come into this knowing a little something about interpreters. Most recently I've prowled around the internals of CPython and made a Python 3 version of [Byteplay](https://github.com/tallforasmurf/byteplay), a tool for playing with Python's byte-code. Plus, my first real software development experience was helping implement [APL\360](https://en.wikipedia.org/wiki/APL_(programming_language)#APL\360). Where I expect this book to teach me something new, is in the use of a syntax tree, and more general parsing and compiling, and software design techniques I've never had to use.)


Direct quotes from Nystrom's work are kept to a minimum, and only used when explaining how or why I did something differently than he, or otherwise want to comment on the book. Hopefully that keeps me within "fair use" bounds. When anything is unclear, refer to Nystrom's book or repository for explanations.

My own text and Python code has
License:<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.

## Chapter 4

### Java vs Python modules (Section 4.1)

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

### Error Handling (Section 4.1.1)

Nystrom is using a program global, hadError, set in various places and tested in others. Not sure I like this, but whatever. At least, Python makes the use of a global more obvious, first by the convention of using an all-cap name HAD\_ERROR, second by having to write `global HAD_ERROR` in any function that sets it. Points to Python.

### Token Types (Section 4.2.1)

A new Java/Python problem arises. The book uses an enum for the 35 or so token types. I started to make that a Python Enum, but the Python Enum is a pitiful thing. It's a class, so any reference to an enumerated value can't be just its name, but the qualified name. So given

    class TokenType(Enum):
        LEFT_PAREN = auto()
        ... etc

the code can't just refer to `LEFT_PAREN`, it has to say `TokenType.LEFT_PAREN` which is just ugly. Explicit, but ugly. (Points to Java/C.) Plus I don't know if the Java enums are effectively ints, and if so, whether at some point the book won't try to compare token types for greater or less. So maybe I should use an IntEnum, but that requires me to specify each int value (the auto() initializer isn't allowed). Bleagh. I'm going to make them globals of the TokenType module initialized to unique ints.

### Token (Section 4.2.3)

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

### The Scanner (Sections 4.5-4.7)

I have implemented the complete code now, and run it successfully against the simple lexeme test files in Nystrom's repo. I made one significant change. In his Scanner.java, the scanner reports errors by invoking `Lox.error()`, a function defined in the main module. I copied the `error()` function in my plox.py module. However, it isn't practical for code in Scanner.py to refer back to plox.py. Python namespaces don't work that way.

In section 4.1.1 Nystrom says,

> Ideally, we would have an actual abstraction, some kind of "ErrorReporter" interface that gets passed to the scanner and parser so that we can swap out different reporting strategies.

So I did that; i.e. I changed Scanner so that besides a string of text it accepts a reference to an error reporting function. In plox.py I pass the `error` reference so Scanner can call it in the two (2) places it reports an error. Also I extended error reporting to include not just a line number but a character position in the line. That required noting the source index of the latest newline seen, so that the offset into that line could be calculated. Trivial extra code.

I changed the error reporting for string literals as well. There's really only one possible error in a string, the absence of a terminator. That won't be found until the scanner has sucked up all the text to EOF. At which point it reports the error as happening on the line number where EOF happened. Which could be a long way from where the orphan opening quote was. So I saved the line number and start position of the opening quote, and when reporting the "unterminated quote" error, give that position, not the EOF position.

## Chapter 5

### Visitor Pattern (Sections 5.2-3)

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

(Next day) I have absorbed the basics of the Visitor Pattern and have written it up for my own pleasure, see [visitations.md](https://github.com/tallforasmurf/CrInPy/blob/master/craftinginterpreters/visitations.md) in this repo. Also in that note are comments on the contrasting implementations between Java and Python. Then I implemented the code from the wiki article, see visitortest.py.

### Generating ASTs(*sic*) (Section 5.2.2)

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

### Not Very Pretty Printer (Section 5.4)

I call foul! In this section, Nystrom writes code to visit a tree and print its contents. But we have not seen any code whatever for *building* a tree. We've seen the classes that will be the nodes of the tree, and we've talked about the Visitor Pattern as a way of processing a tree in various ways *after it's built* -- but we have not seen any code for building one.

In particular, we have not seen the code that takes a list of Token objects, as produced by our scanner in the prior chapter, and parse them and convert them into Expr subclasses. But still he wants us to write code for a PrintVisitor, with no way of testing it, other than to hand-code assembly of a tree.

Not gonna do it. I'll proceed on to the parsing chapter, and maybe revisit the printer problem when I have a tree built.

## Chapter 6

### Java optional arguments

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

### Parser Error Handling (Section 6.3, see also The Scanner above)

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

### Error handling rant (Section 6.3.2)

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

### Error Handling clarification (Section 6.3.3)

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

### Printer, and Challenges

I did the expression printer, taking pains to follow the nice Visitor pattern, see [AstPrinter.py](https://github.com/tallforasmurf/CrInPy/blob/master/craftinginterpreters/AstPrinter.py). It will be easy to expand it to print other things as we add statements to the AST.

However, the top part of it, the meta-class `astVisitor` is potentially useful for other "visitations" to the AST. Soon I am going to want to pull that out to a separate module, and make the AstPrinter import it. Then I can write other types of visitors importing `astVisitor`.

I also implemented challenge #1, the comma operator; and challenge #3, giving a separate error message for a binop that lacks a left hand value.

## Chapter 7

I have implemented the Expr interpreter. It went quite easily. I'm onto Nystrom's method now, so when he left obvious loose ends dangling I did not get upset, but just kept reading, waiting for him to weave them in. Which he mostly did.

As usual the most fraught piece of design was error handling. I implemented it much as he suggests, making the considerable adjustments required to bridge from Java's exception handling to Python's. But I did what I should have done during the prior chapter; I read up on [user-defined exceptions](https://docs.python.org/3/tutorial/errors.html#tut-userexceptions) and crafted a specific exception for the Interpreter to use. Then I used `try` to trap all the predictable built-in exceptions (ValueError from float conversion, ZeroDivide) and in the `except` clause, raised the custom exception instead. That's what Nystrom was doing, basically, although it was disguised from me by the Java conventions. (Well, I still don't understand about the executable code, see above.)

An odd thing, though. He has specific error display handlers for the Scanner, the Parser, and now the Interpreter. The Parser handler gets a token and a message; from the token it extracts the line number, the lexeme (e.g. `+`), and displays that, `Error line 2 at +: message`.

His handler for the Interpreter takes the same arguments, but only displays the line number, not the operator. I don't see why it shouldn't, so I just had the Interpreter use the Parser's error display: `Error line 2 at /: division by zero`. Why not?

And as with the Scanner and Parser classes, my top-level code passes the error handler when intantiating the class, rather than having the object try to call back into the calling module by name, which doesn't work well (at all?) with Python namespaces.

### Challenges

Challenge 3 at the end of the chapter is, figure out a way to diagnose division by zero nicely. *Hey*-o! I did that automatically, in the course of handling other errors. I saw that was a possibility and just included it in the process of converting built-in exceptions into the custom exception.

Challenge 1 suggests extending the handling of the overloading of "`+`", which in Lox, if applied to strings, means concatenate. The initial spec required both operands to be of the same type. Challenge 1 asks, how about if *either* operand is a string, make the other into a string, so "scone"+4 -> "scone4". It would be easy to do, but I see a problem.

By that rule, "3"+4 -> "34". I can see equal justification for saying, if either operand is numeric, try to convert the other to numeric, and if you can, do numeric addition, so that "3"+4 -> 7. Wouldn't that be what a naive user might expect? (By the way, Python only allows "`+`"-concatenation for strings; no helpful coercion.)

Thing is, "convert a string operand to numeric if you can" is a trickier thing to do than "convert a numeric operand to string". There's no easy test. For example, `"3.5".isdecimal()` yields False, so that nice test is no use. And, there's `float("4e5")` which works fine. You could ask if a string contained only "`+-.e0123456789`" but that wouldn't tell you if it was syntactically a number. The only simple test is to do `float(thing)` inside a try, which is a
bore. So no doubt this is the reason that the languages that allow mixed-type concatenation, force to string instead of to number.

Finally, I think that on balance it is a bad idea, in a language described as "simple", to get into the game of coercing types at all. Once you do it in one situation, the user can justifiably call you "inconsistent" if you fail to do it in any other situation.

## Chapter 8

Working through this chapter I add the parsing and interpreting code for var and print statements, and for executing expression statements and print statements.

Nystrom shows how to interpret an expression statement, but omits to mention that the expression statement, since its execution returns no value, is only useful when it has side-effects, e.g. 

    2+7*3

is useless, but

    some_fun(2+7*3)

will presumably change the state of the program somehow. 

### Section 8.3

Now we are defining the "Environment", what in more primitive days on APL (that's a pun, but nobody is going to get it) we called the "symbol table". Anyway, I perhaps foolishly run ahead of the text and read the Environment.java module and [implement it in full](https://github.com/tallforasmurf/CrInPy/blob/master/craftinginterpreters/Environment.py). I feel clever, because where Nystrom has a class that *contains* a Java hash map, I make my Environment a sub-class of dict so it *is* a hash-map.

I feel even cleverer later. The Environment is designed to support nested syntactic scopes, so there will be (typically) a local Environment that is logically enclosed by a global Environment. Or possibly multiple levels? We'll no doubt see later on in the book. Anyway, each instance of Environment has a member `enclosing` which points to a more global Environment. The Java code has a method, `ancestor()` which returns its *n*th outer enclosure, like so:

```
  Environment ancestor(int distance) {
    Environment environment = this;
    for (int i = 0; i < distance; i++) {
      environment = environment.enclosing;
```

And I code up a very similar piece of Python, then I realize this is just begging for a nice obscure recursive one-liner:

```
    def ancestor(distance):
        return self.enclosing.ancestor(distance-1) if distance>0 else self
```

But I didn't actually code it that way; just too tricksy.

### Section 8.4

So implementing assignment didn't present any surprises. Especially because I had already prepared the complete Environment class, working from the Java code. Otherwise I'd have had to add its `assign()` method in the middle of implementing the Interpreter code to execute assignment.

I made a change to flatten his version of the assignment parsing code. This is his:

```
    private Expr assignment() {                                   
    Expr expr = equality()
    if (match(EQUAL)) {                                         
      Token equals = previous();                                
      Expr value = assignment();                                
      if (expr instanceof Expr.Variable) {                      
        Token name = ((Expr.Variable)expr).name;                
        return new Expr.Assign(name, value);                    
      }                                                         
      error(equals, "Invalid assignment target."); 
    }                                                           
    return expr;                                                
    }                                                             
```

I don't see any reason not to pick off the "invalid target" error first, and thus flatten the logic. This reads more easily to me for two reasons: One, there's no nesting of blocks to keep track of, it's just linear execution; and Two, that linearity makes it possible to comment it in "literate" style.

```
def assignment(self)->Expr.Expr:
    # Suck up what might be an assignment target, or might be an expression.
    possible_lhs = self.equality()
    # If the next token is not "=", we are done, with an expression.
    if not self.match(EQUAL):
        return possible_lhs
    # Now ask, We have "something =", but is it "variable ="?
    if not isinstance(possible_lhs, Expr.Variable):
        # flag an error at the "=" token, which is previous
        self.error(self.previous(), "Invalid target for assignment")
    # We have variable = something, collect the r-value.
    # Notice the recursion? We take a = b = c as a = (b = c).
    rhs = self.assignment()
    return Expr.Assign(possible_lhs.name, rhs)
```

### Challenge 1

Challenge 1 is to re-enable the "desk-top calculator" mode we had a couple chapters ago, when the Parser and Interpreter only handled expressions. The user could type in `10/3` and get back `3.333333333335`. Over Chapters 7 and 8 we have converted the Interpreter so it only accepts a list of Statement objects, and the Parser so that it only parses statements, which in particular meant that it required everything to end in semicolons. And the Interpreter didn't return any values because Statements don't return values.

How to get back to an interactive REPL (read-interpret-print-loop, and acronym from LISP)? I looked at what I had wrought. It would have been possible to call into the Interpreter at its `evaluate()` method with an `Expr` object. That was the old pre-Chapter-7 code still there. The problem was that the Parser no longer returned any `Expr` objects; it only returned a list of `Stmt` objects. One of those could be an "expression statement" but I didn't want to get into the business of taking one of those apart at the top level of the program.

What I finally did was, after parsing, to look at the result. If it was a single statement of the Expression type, I passed it to a new Interpreter entry point, which would execute it and return its value.

```
    if 1 == len(program) and isinstance(program[0],Stmt.Expression):
        value = interpreter.one_line_program(program)
        print(value)
    else:
        interpreter.interpret(program)
```

I also gave the user a little hand: in the console-input code, if the user enters a line that doesn't end in ";" I paste one on for her. That may come back to bite me later, but it's a help for now.

It isn't horribly kludgy. But it is complex enough to make you appreciate the brutal simplicity of LISP, in which there *are* no "statements", only expressions.

### Challenge 2

Challenge 2 was to find a way to make it illegal to reference a variable that had been declared but not assigned a value. The code as shown in Chapter 8 (and not changed later I believe) gives a new variable the value *nil* when it is created, so my code follows that, adding the variable to the Environment with a value of `None`, Python's equivalent.

This challenge would require one of two things, neither of which seems acceptable. One, find a special, initial value, which could mean "not initialized", and which would have to be checked-for every time a variable was referenced. That has two problems. A, nil/None are valid literal values that a variable could be given by assignment, and there is no "out of band" value that could be given to a variable to say "I'm not initialized". Every other possible value might arise in normal execution. And B, checking for "not initialized" every time a variable is fetched would be a bad performance hit, especially when the overwhelming majority of checks would find nothing.

The second way would be to keep a separate list of variable names that have been declared (`var some_name;`) but not yet assigned a value. Don't file them in the dictionary with the initialized names; file the names in, let us call it `limbo`. Then, when code refers to a name, and it isn't found, the only change is to have to decide which of two error messages to give. If the missing name is in `limbo`, say "uninitialized variable x"; otherwise say "undefined variable x".

(Incidentally, Python does this. I ran into it by accident the other day: an error message "variable x referenced before assignment". It can only come up in some very odd circumstances.)

That approach needs a bunch of extra code in the Environment, messing up a particularly clean implementation of mine. It is not a performance hit; all references and most assignments would be unaffected. Only when assigning to a variable for the very first time, it would not be found in the dictionary; then you have to look it up in the other list and create it.  However, thinking further -- there would have to be a limbo at each level of scope. If user code is trying to reference `x` in a local scope, is the error that the user did not declare `x` in this scope, or that she did not initialize the `x` that might be in limbo in a more global scope?

I could do this, now I've thought it through, but I choose not to. It's a bunch of code with not clear benefit and some ambiguity.

## Chapter 9

### section 9.2, if statement

Yup, what I said up there about my helpfully appending a ';' if the user didn't type one in calculator mode? It came back to bite me. Testing the if-statement, I entered a `{block of code}` which immediately caused an error, something about a semicolon. There's no semicolon in there... I actually had to trace into the parser to realize, oh yes there is a semicolon following the `}`. So I changed the interactive routine to only append one if the line ended in neither `;` nor `}`. Then all proceeded smoothly.

### sesction 9.3 and 9.4, loops

This went very smoothly. I really dislike the C-style `for (;;)` statement, but I was impressed with Nystrom's approach, to "de-sugar" it by reducing it to the statements already implemented. With that hint, I coded my version; then I went back to the text. His implementation was much smoother than my first cut at it, so I revised to match.

The test of the loop is a simple fibonacci calculation:

```
var a = 0;
var b = 1;

while (a < 1000000) {
  print a;
  var temp = a;
  a = b;
  b = temp + b;
}
```

Not a lot of computing in there, but in case there was any worry about a Python implementation being slow? The user execution time of the command `python3 plox.py test_fib.lox` is 0.026 seconds of user time. That 26 milliseconds includes loading python3, initializing it, reading the several hundred lines of code of the interpreter from several different files, compiling that, then executing that code while it reads, compiles, and executes the test program. In other words, execution time is negligible.

Coding this I did bite myself with my favorite Python mistake, forgetting to put the parens on a simple function call, e.g. `something = self.methodname`. Python happily says, "oh, you want to assign the function `self.methodname` to some variable? Cool." And silently does so. Problems only surface many statements later when the code tries to use `something` and it's a function reference, not whatever I intended it to be.

### Challenge: break statement

Wow, this one stopped me:

>  Add support for break statements...The syntax is a break keyword followed by a semicolon. It should be a syntax error to have a break statement appear outside of any enclosing loop. At runtime, a break statement causes execution to jump to the end of the nearest enclosing loop and proceeds from there. Note that the break may be nested inside other blocks and if statements that also need to be exited.

The first problem is for the parser. There needs to be a flag `now_in_loop` which the parser sets when it begins processing a `while` or `for`, and can be checked upon finding a `break`. Not hard to do.

The second issue is the runtime unwinding. The problem is that, at runtime, in an interpreter built on Python, the nesting of control statements is not expressed in a testable data structure, but in the Python execution stack:

    visitWhile() invokes
        visitBlock() invokes
            visitIf() invokes
                visitBreak()

how do we get out of that? Thinking this out: the only two problems are the while and the block. Execution of `if` visits either its `then` or `else` statement; whether that's an assignment, a function call, a block, or a `break` makes no odds to the `if`; it has finished and returns. Again for functions, a function body is also a single statement (typically a block); when that ends for any reason, function execution is done. So we don't need any special "unwinding" logic for ordinary statements; they just return as normal.

The block statement is different; it contains a list that might be `{stmt;stmt;break;stmt...}`. When it executes the break, it has to stop as if it had reached the end of its list. It's easy to put a test for a break statement in the condition of the loop that runs down the list.

The `while` already has a user-defined continuation test; in principle it only needs to `and` that test with a test of a flag that would be set by execution of `break`. (Wait: that implies that a block has to execute a break, not just recognize one and stop.) Now, where to store that flag? It has to be visible to the `while` code, and also visible to a `break` that might be nested several environments deep.

Oh, now, wait a minute. We already have this structure of nested local environments, with a lookup algorithm that finds the latest-defined version of a variable. Suppose part of execution of `while` is to do, in effect, `breakflag=false;` and the execution of `break` is simply to do `breakflag=true;`. Even if the `break` is nested in several blocks, the assignment logic will find the most recently defined break-flag. So that would work...

...not quite. This is valid code and not unheard of:

    while (i < i_limit)
        while (j < j_limit)
            if (array[i,j] == sentinel) break;
            j = j+1
        i = i+1

Nystrom's challenge says, "causes execution to jump to the end of the nearest enclosing loop". So break in the inner shouldn't end the outer loop. Well, that's fixable: when a `while` starts it clears the break-flag, and again when it ends, it clears the break-flag.

Next issue: the break-flag is to be stored in the environment as a variable; what to call it? It cannot be called anything that is a valid variable name, otherwise somebody, someday, will use that name and file a bug because their loop breaks too soon. Fortunately, (checking the Environment code) it accepts as a name, any string from a `Token.lexeme`. The Parser will never allow creation of a variable with a nonstandard name, but there's no reason the while-code can't assign to a variable named `¿seguir?`. That's "out of band" from normal code.

OK, I think I have a plan here. I will work on this tomorrow. "Thanks for watching." (A wee shout-out to you-tuber James Sharman.)

### continuing the challenge

Hah. Started working on the "not hard to do" parser bit. IS hard! Because loops can be *nested*, doh! So a simple flag won't work, because when can you clear it? If you set the in-loop flag on beginning a `while`, and clear it when finishing the `while`, you just cleared it for a possible enclosing `while`:

    while (foo)
        while (bar)
            break; // this is ok
        break; // this is not ok but should be

So the next obvious move is to make the in-loop variable an integer, incremented at the start of parsing a loop, decremented on the way out. That might be fine except for errors. In fact, cleaning up after an error is a problem no matter how the in-loop is marked. On an error, the parser has a "synchronize" method that tries to find the start of the next statement, skipping as many tokens as it needs to, which is indeterminate. Does it peel out of a loop, or not?

OK, new policy: it is *not* a syntax error to write `break;` outside a loop. It is a *run-time* error. That would be one way to handle it. But that's not good either. It's the sort of error the compiler/parser ought to catch, not leave like a little cow-pie for the user to step into an unknown time ahead.

I need a complete rethink. But! I got quite a ways into coding this, including modifying the list of valid tokens and regenerating the Stmt class (Make\_AST, from chapters ago) to have a .Break subclass. And now I'd like to back all that work out and... *shit* I have completely lost my Git discipline. If I was doing it right, I'd have started a *branch* before beginning, and then could reset out and that would be it. I didn't. Now I have to go back and clean up manually.

### and the break challenge is broken (he he)

While on my daily walk I figured out how to handle the parser. I would pass the in-loop flag as a parameter to the methods that deal with compound statements, and to the break statement. When the compound statements recurse to handle nested statements, they pass the same flag to their descendants. Thus when parsing reaches a BREAK token, it knows if it has inherited the fact of being in a loop or not.

The implementation was a bit trickier than I thought. I had to do some tweaking of the Environment code that I had translated from Java. Partly this was because some of its methods received the name of the variable to fetch or set, as part of a Token object. Some received the name as a string. Then, in the Interpreter, executing a while or a block, I want to set or test the value of a continue flag often, and it would be silly to make that constant name string into a Token just so the environment fetch() method could get it out again.

So I split the Environment's methods for assign and retrieve into pairs, one that took a Token and one that took a plain string. The latter can be called by internal code.

Then I could make the changes I discussed earlier. In `while`, assign True to a special Continue variable; then test it before every iteration. In effect and-ing it with the user's condition. In `break` just assign False to that variable. And in a block, test the variable before executing each statement, so the block can be abandoned as soon as a break has executed.

And after picking off the usual stupid typos, it all worked:

```
> var i = 9; while (i> 0) { print i; i=i-1; if (i==4) {print "4!"; break;}}
9
8
7
6
5
4!
> 
```

Note the break is nested in a block nested in an if. But the nested scopes of the Environment work fine. The `while` defines a variable in the global scope; by the time execution reaches the `break` there are two temporary local environments, one for each left-brace. But the assignment finds the global variable.

So that was a nice Sunday afternoon exercise.

## Chapter 10, Functions

Glad to be getting to this. But I immediately have some questions.

### Function Syntax: "7()" a call?

First order of business, as in prior chapters, is to define the syntax of a function call, which has rather a high priority. In the expression grammar he sets up

    unary → ( "!" | "-" ) unary | call ;
    call  → primary ( "(" arguments? ")" )* ;

He then spends some words justifying the part about `(`*args*`)*`, as allowing a production like,

    getAfunc()()(foo)

Yeah, no prob: `getAfunc` is a function that takes no arguments, returns a *function* that also takes no arguments, but returns *another* function that takes `foo`. Easy.

What boggles me, and he doesn't explain, is that the thing preceding a `(` is a *primary* -- not an identifier. Further down in the grammar we have,

    primary        → NUMBER | STRING | IDENTIFIER | "false" | "true" | "nil"
                   | "(" expression ")"

Which means that by this grammar, `7(foo)` and `"hello"(foo)` and `false(foo)` are all acceptable function calls. And indeed, in his Java code, he has (slightly edited) `callee = primary()`.

I'm filing an issue at the book on github, even though I know that lots of other people have been filing issues since 2017 and nobody has commented on this. I'll probably get chastened.

### Loopy loop

For a while I thought Java was going to have a leg up on Python in the loop department, and it may, but not this time. I was looking at his Java for processing function arguments:

```
    if (!check(RIGHT_PAREN)) {
      do {
        arguments.add(expression());
      } while (match(COMMA));
    }
    Token paren = consume(RIGHT_PAREN, "Expect ')' after arguments.");
```

And thinking, oh rats, I can't do that in Python because it does not have the do-statement-while construct, which does something and looks for a reason to stop afterward. In the above, since the current token is *not* a right paren, collect an argument, and as long as the next thing is a comma, do it again.

Python only has while-condition-do, testing the condition at the top of the loop. How to translate and not have a lot of code. Hmmm. After a lot of thought I came up with,
```
    while not self.check(RIGHT_PAREN):
        args.append( self.expression() )
        self.match(COMMA)
    rparen = self.consume(RIGHT_PAREN,"This message cannot be displayed")
```
which is the same length but isn't quite the same. His loop invariant is "next token is whatever followed a comma." Mine is, "next token is not a right paren".

It took some thinking to be sure they did the same thing on correct input. I suspect they behave differently on invalid input. Take the case of the error,

    funcname(foo;bar)

where there's an extraneous semicolon. His code will process the argument `foo`, then it will fail to match a comma, and will exit the loop, followed by an error message like `Line 1 char 25: Expect ')' after arguments`.

My code will process `foo`, look for a comma and do nothing because the next thing isn't a comma but a semicolon, and go around again. The `expression()` method will choke on the semicolon and give the message `Line 1 char 25: Unanticipated input ';'`.

In either case we stop with an error message, but the error is detected at different levels of code.

Just a little mental "fuzzing" gives several things to try: `fun(,)` for example.

### Java Jive (Section 10.1.1ff)

Once again I find myself at odds with Nystrom's pedagogy. He has a big swathe of complex code worked out and is now trying to dole it out in small comprehensible bits. Unfortunately it doesn't break down that way; there's a lot of stuff you need to know, before you can understand the starting pieces. Wait, example.

We are implementing functions and function calls. We got the parsing out of the way yesterday. Parsing a function call produces an Expr.Call object, so:
```
class Call(Expr):
    def __init__(self, callee:Expr,paren:Token,arguments:List[Expr] ):
        # initialize attributes
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
    def accept(self, visitor:object):
        return visitor.visitCall(self)
```
After parsing, we have a three-part object with

* The callee, the thing to be called, which can be any kind of expression that yields a callable thing;

* the right-paren token that closed the call (that is just there because it contains a source line number we can use in error messages);

* and a list of expressions for the arguments to the call.

So far so perfectly clear. Now we want to implement this, execute the call at runtime. But Nystrom also knows that there are going to be built-in (he calls them "native") functions (digression: in APL they were "primitives") and also there will be Classes, which also are callable, and class methods, and probably other things. 

What he has *not* said is, there is a general *class* of things that can be called with this syntax and (can legitimately turn up as the "callee" of a call). He has focused entirely on functions, but then he is forced to spring the class on us without explaining the need or purpose. He presents the interpreter code for a call in this Java:
```
 public Object visitCallExpr(Expr.Call expr) {         
    Object callee = evaluate(expr.callee);

    List<Object> arguments = new ArrayList<>();         
    for (Expr argument : expr.arguments) { 
      arguments.add(evaluate(argument));                
    }                                                   
```
I'm reading along saying, uh huh, evaluate the expression to find out what we are calling, great, uh huh, evaluate each argument expression in the list of them, saving their values, ok. And then:
```
    LoxCallable function = (LoxCallable)callee;         
    return function.call(this, arguments);              
```
You what now? Where did this LoxCallable thing come from? He "explains" as follows,

> all that remains is to perform the call. We do that by casting the callee to a LoxCallable and then invoking a call() method on it. The Java representation of any Lox object that can be called like a function will implement this interface.

My jaw is flapping. This is absolutely the first time in the book the term LoxCallable has appeared. I have no idea what is going on. I go off into his code and find out that `LoxCallable` is an "interface"; I go off into the googles and find out that a Java interface is an abstract class that defines methods but does not implement them; any other class can implement them.

What boggles me is the use of the word "cast". I'm quite familiar with casts from C, for example. In C, notation like `i += (int)*memptr` tells the compiler, "trust me, the bits at the the address in memptr can safely be treated like an int". But the cast only tells the compiler how to treat the memory; it doesn't actually *change* the memory.

If that's so for Java, then what happened back there in 

    callee = evaluate(expr.callee);

must have returned something of a class compatible with LoxCallable. This cast now just tells the compiler to believe that. But nothing we've done so far ever produced anything called LoxCallable.

Well, wait, that's not too far-fetched because -- I suddenly realized -- we have not yet either parsed or executed a function *definition*. What's *callable* is a *defined function* and the language we have built to this point doesn't have those.

Now, after 20 minutes of stewing about this, I realize, I can't possibly know what a LoxCallable is, because we haven't built any yet. Presumably when we get around to implementing a function *definition*, it will be obvious what kind of structure it needs to represent it, and that will be a LoxCallable.

And when we know *that*, it will be obvious how to *execute* it.

So **why the flak are we trying implement calls when we don't know what functions look like???**

Upside-down pedagogy. I absolutely do not agree with this order of presentation.

### Moron Callables

So coming back to this today, I thought well, I'll get a leg up by defining a simple meta-class for Callables, something similar to his LoxCallable "interface" code, which would be basically,
```
class LoxCallable():
    def arity(self):
        raise NotImplementedError()
    def call(self):
        raise NotImplementedError()
```
which is what I did for the two "visitor" classes, `visitExpr` and `visitStmt`, both of which are implemented by the Interpreter class.

Then I thought, fine, what would a concrete Callable item, say Function, look like? Why it would have as properties the parts of a function, its name, list of argument-names, and presumably a compiled Stmt for its body. And *then* I noticed that we already have defined this in the Stmt module,
```
class Function(Stmt):
    def __init__(self, name:Token,params:List[Token],body:List[Stmt] ):
        # initialize attributes
        self.name = name
        self.params = params
        self.body = body
    def accept(self, visitor:object):
        return visitor.visitFunction(self)
```
That (which came from aping the existing Java code) is presumably what would be output by the Parser, after parsing a function declaration. And it's ready for the Interpreter to visit it for execution. Something's not right. OK, *sigh*, I will start reading again.

### Interface-off

Things get no better. Now he implements a simple built-in function `clock()` by adding the following code to the Interpreter class (section 10.2.1),
```
    globals.define("clock", new LoxCallable() {            
      @Override                                            
      public int arity() { return 0; }
      @Override                                            
      public Object call(Interpreter interpreter,          
                         List<Object> arguments) {         
        return (double)System.currentTimeMillis() / 1000.0;
      }                                                    
      @Override                                            
      public String toString() { return "<native fn>"; }   
    });                                                    
```
and says it "is a Java anonymous class that implements LoxCallable." So this presents some problems for the non-Javanese: is there another language that allows nonce implementations of anonymous classes? The whole book *Crafting Interpreters* should have a big red notice on the front, "Non-Javanistas need not apply". Well, I can mostly grok what he's doing. Suppose I had that meta-class I showed a few paragraphs back. Then I could do this exact reproduction,
```
class builtinClock(LoxCallable):
  import time
  def arity(self): return 0
  def call(self, interpreter:Interpreter, args:List[object])->float:
    return time.time()
  def __str__(self): return "native fn 'time'"
```
although I could not put it in the context of a call to `globals.define()` because in Python, a class declaration is a statement, not an expression -- as apparently it can be in Java?

Several questions remain, more dangling loose threads that this student finds so frustrating about Nystrom's teaching:

* What the *heck* is the relationship between the `Stmt.Function` class, and the `LoxCallable` class? Obviously at some point the statement, representing the declaration of a function, has to get turned into something that can be called. Darned if I can imagine when; anyway, why isn't it that already?

* What is that argument `interpreter` in the `call()` method? Will the Interpreter, when executing a function call, pass itself in? Why doesn't it just *execute* the thing?

Meanwhile, I'm going to do the above: add a module `LoxCallable.py`, import it into the Interpreter module, declare the `builtinClock` class inside the Interpreter class, and assign an instance of it to the global environment during startup.

### Functional success (Section 10.3, 10.4)

So he finally does introduce all the machinery. And the answer to my first question above *maybe* should have been obvious to me even without reading ahead.

A program has declarative statements like, oh, I dunno, `fun` to declare a function, and imperative ones like expressions that invoke functions. Both kinds of statements get *executed*, in the sense of the Interpreter "visits" each type of statement in the list of `Stmt` objects that comprise a program.

To "execute" a function statement, is to process the function invocation into a callable thing. In other words, when the Interpreter visits the (parsed form) of the statement

    fun hello(who) { print "hello " + who; }

that is when it takes the parts of that declaration, wraps them in a LoxCallable object, and (this is key) defines the function name in the current environment, as having the value of that object. So from that moment on in the program, the *name* `hello` has the value "callable object that contains the body of that function and its argument list".

Later, the Interpreter encounters a statement like

    hello("world");

and looks up `hello` in the environment, finds a callable, and calls it.

What I had forgotten and so was very puzzled about, was that the declaration is going to be "executed" just like any other statement, and to "execute" a declaration is to put its meaning in the environment.

I'm still not positive why it is better to pass the interpreter itself, into the call, so it can be invoked to execute the function body. Nystrom is pretty high on it, though. Speaking of the actual call,

> This handful of lines of code is one of the most fundamental, powerful pieces of our interpreter. 

And invites us to meditate on that, which I will do.

Anyway, I still deeply dislike the way he organized this chapter, although now that I have seen it all, the code makes sense. And my Python translation of it worked first time.

### Sections 10.4 and 10.5

Here we actually execute functions including implementation of `return`. It all goes together smoothly. The `return` statement, Nystrom notes, causes a function to stop, but it may come in deeply-nested code. How to unwind the interpreter's stack no matter what it's doing? Raise an exception. That's the answer in Java, and it maps smoothly into Python, although I have to think for a while as to where to define the custom exception. I put it in the LoxCallable module. With that, I run the fibonacci test case. Here's my version.
```
// test fibonacci function with time measurements
// refer to book section 10.5
fun fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n-2) + fibonacci(n-1);
  }
print "Starting..." ;
var t0 = clock();
var t1 = clock();
var tt = clock();
for( var i= 10; i <= 25; i = i+1 ) {
  print i ;
  t0 = clock();
  print fibonacci(i);
  t1 = clock();
  print t1 - t0 ;
  print "---------" ;
}
print "total" ;
print clock() - tt ;
```
As Nystrom notes, this is starting to look like a real  programming language. (But it really needs some way to put multiple expressions in a `print` statement!).

Anyway, this is a heavy test of recursion. Here are the reported times for the last two iterations and the total:
```
24
46368
2.0661370754241943
---------
25
75025
3.4064881801605225
---------
total
8.838949918746948
```
So `fib(25)` is taking 3.4 seconds of a fairly powerful CPU's time. But, I put an invocation counter into the fib function, adding just one statement:
```
fun fibonacci(n) {
  invoke = invoke + 1;
  if (n <= 1) return n;
  return fibonacci(n-2) + fibonacci(n-1);
  }
```
Here's the timing result for input 25:
```
25
75025
4.878959894180298
242785
```
Adding an expression and an assignment to a global variable bumped the execution time from 3.4 to 4.9 seconds, a 44% increase. But now we know the `fibonacci()` function was invoked 242,785 times in that period. Going back to the 3.4 second time, that's 14 microseconds per iteration. Not bad really, considering the dozens of Python statements being executed to implement each call. Not to mention that each of the quarter-million calls ends with raising an exception to implement the `return`.

### Challenge 1

Since the arity-check between function signature and argument list is done on every call, the book says, it's a performance load. Smalltalk doesn't have the problem, why not?

Is Smalltalk compiled? Clearly compiled languages make the check when *compiling* the call. In fact any language like Java and C++ would have to do that because they support "overloading" functions, choosing which version of a function to call, based on the match between the call arguments and the functions' different signatures.

So the answer is, Smalltalk compiles (maybe to a byte-code?) before execution, and checks then?

Checking the answers, it turns out that Smalltalk has a completely different syntax for function invocation which bypasses the problem.

### Challenge 2

Add anonymous function/lambda support. This is tricky because the syntax as built has a high fence between what are syntactically "statements" and "expressions". Expressions can appear at specified points within statements, e.g. "`print` *expression*`;`" but not the other way around.

The code that parses an expression returns an instance of `Expr` which represents the top of what may be quite a deep tree of `Expr`s. The code that parses a statement returns an instance of `Stmt` which gets put in a linear list. 

The declarators, `var`, `fun`, and eventually `class`, are statements. Now he is proposing to make the following simple example work:
```
  var foo = fun (x) { print x; } ;
  foo(33) // prints 33
  fun thrice(afun) { afun(1); afun(2); afun(3); }
  thrice( foo ) // prints 1 then 2 then 3
```
The key is that "`fun (`*parms*`)`" needs to be treated as an *expression*. That raises two big issues.

One, at Parse time, recognizing the two-token sequence `fun (` at a point where an expression is expected. And then do what? OK, one could factor out the latter 2/3 of function statement parsing and use it also from expression parsing. Create a new variant of `Expr`, say `Expr.Lambda` to store the parameter-name list and the body code.

Two, execution time. When the Interpreter "visits" an `Expr.Lambda` it can create a `LoxFunction` instance, exactly as it does when visiting a function statement. The init method of `LoxFunction` would have to accept a missing (or `None` valued) function name. Otherwise it would be the same.

So this is doable; I just don't want to do it right now.

Checking the answers, yes, this just how to do it; with the addition that to allow a lambda at the head of a statement (an "expression statement") one needs to guard the function *statement* code with a two-token lookahead. If the parser sees FUN it has to look ahead for IDENTIFIER, LEFT\_PAREN to know it has a statement. Let the sequence FUN, LEFT\_PAREN pass on and it will be caught as an expression. This would be the only time in the Lox syntax where a two-token lookahead is needed.

### Challenge 3

This challenge asks, what does this code do and is it valid? Actually I've extended the example from the challenge to make a point.
```
var a = 200;
fun sr(a) { print a; var a = 99; print a; }
sr(a); // prints 200, then 99
print a; // prints 200
```
In other words, the names of function parameters are treated as local variables of the function, which is the same as Python, and I think that's fine.

Now here's a strange thing. In the answers, he say "no it isn't (valid)". But it is, it works just fine. The local variable shadows the global. Then the assignment replaces the value of the parameter. That's fine with me. 

He says the question is, is a function's parameters in a scope outer to its local variables, or the same as them? In Lox as written, they are in the same scope, the environment created by the call. But I don't see what difference it would make if parameters were in an outer scope. A parameter name would still be shadowed by a local declaration/assignment. The only way you could tell a difference would be, if we had an `undef` statement that removed a name from the local dictionary. Then you could "unshadow" the parameter and would be surprised if it didn't go back to its call-value. Since you can't, there's no functional difference whether a local var `a` *shadows* a parameter `a`, or simply *redefines* it.


## Chapter 11

Here we apply the visitor paradigm to inspect the parsed code and build a map showing from which "depth" in the nested environments, a name should be fetched. This enables "closures", references that are frozen into functions declared within another scope, like this:

    var a = "glob"; { fun showA(){print a;} showA(); var a = "loc"; showA(); }

On its second invocation, `showA()` should print "glob". And, after adding quite a bit of code including a completely new visitor, it does. The reference to `a` stored in the code body of the function `showA` "knows" that it wants the global `a` and happily ignores the local one.

### Cleverness, also uniqueness of objects

The implementation of this is clever in a way that Nystrom does not even dwell on, and he's not usually shy about mentioning such. Here's the issue.

We want to store information about every *access* to a variable. Not much; just a number giving its "depth" in the nested environments. So, a simple key-value map is created. The mapped values are those depths, as ints. The keys are the references to variables. In a parsed program, a reference to a variable is represented as an `Expr.Variable` object. So the keys in the map are just references to those Expr objects. They contain the *name* of the variable being accessed, but the *name* is not the key in the map. If it were, we could only store one number per name; but a name may be used many times in a program, and possibly in a different context each time.

So we create a map (in Python, a `dict`, but in Java it's a special `HashMap` class, same thing). Wherever in the parsed program there is an `Expr.Variable`, we put that and its then-current access depth in the map. When the Interpreter is executing the program, and has to execute an `Expr.Variable` -- which simply means, get its current value -- it checks the map to see how deep in the nested environments to look.

Using the `Expr.Variable` instances as keys is kind of brilliant. Each stands for a particular reference to that variable; but each is a unique chunk of memory. No matter how many times the program refers to variable `foo`, every one is a unique thing, so there can't be any name collisions in the database.

Well, I thought it was ingenious.

### Still, we differ (Section 11.4)

Not so ingenious, I thought, was that Nystrom chooses to store this map in the *Interpreter*, not with the *program*. Granted, at the point it's built, the "program" is just a list of `Stmt` objects. But the map is specific to, and uniquely descriptive of, that list of statements. It has nothing to do with the Interpreter. But he files it there. Which means, before a program is executed, we have to create an Interpreter instance so we can put the map in it. And then, that instance can only be used to execute that program.

Nystrom addresses this issue very briefly in Section 11.4, but he only considers one other option. He says we could store the access-depth integer int the `Expr.Variable` instance itself. Hell, yeah! And if he were using Python he'd do just that, because you can stuff a new attribute into any object any time.

He says "We could do that, but it would require mucking around with our syntax tree generator". I'm not quite sure what he means by that. There's the independent program that generates the declaration of the `Expr` class; that would have to be modified if we want to add another attribute slot to the `Expr.Variable` subclass. Or he could mean the Parser, which turns the program tokens into the syntax tree, but that wouldn't be affected if `Expr` had one more attribute.

Storing the depth info right in the `Expr.Value` object makes the most sense, and imposes the least overhead on the interpreter at runtime. But there's another option. All you have to do is create a very simple new class, call it `Program`, that is simply a structure that holds (a) a list of statement objects and (b) that depth hash-map. Then the hash map would be associated with the code that it describes. The Program would be the input to any Interpreter, instead of a list of statements as now.

Then a parsed and "resolved" program could be processed in other ways (he mentions the possibility of other kinds of visitations that could be done), with more and more info put into the Program to describe the code. Such a Program could be given to a different kind of Interpreter, for example the byte-code compiler that is coming up in a later chapter.

So I think this was a missed opportunity.

