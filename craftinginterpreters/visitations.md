What the heck is the Visitor Pattern in software engineering? The following is my understanding of it, based Nystrom's text in Section 5.3, and in part on the excellent wikipedia entry, https://en.wikipedia.org/wiki/Visitor_pattern.

The Common Problem
------------------

Consider the common case in which you develop a collection of objects that are related, but different.

The type of collection doesn’t matter; it could be a list, an array, a tree, a file, or a database. The important feature of the collection is that your code can pass through it, accessing each of the objects in the collection in some predictable order.

All the collected objects are instances of various subclasses of a single superclass. For example the superclass might be Mammals, and the collection comprises instances of the subclasses Ape, Canine, Rodent, etc. Another example might be a collection with the superclass of Image and subclasses named JPEG, GIF, TIFF and PNG. 

The Wiki entry above has an excellent example based on the collection of geometric elements that make up a CAD drawing. And of course, in *Crafting Interpeters* the elements of the collection are syntactic units like `Literal` and `BinaryOp` that are being parsed. Here there are multiple reasons to pass over the collection (the syntax tree) element by element: to list them, to generate code, or to execute the code.

You could implement many operations on the collection as a whole by inspecting its elements one at a time, and doing something with each one in turn. You might want to sample the data to collect statistics, perhaps to get the pixel dimensions of each image or the diet needs of each type of Mammal. Or you might want to duplicate the collection, in whole or part, by copying the objects.

Some operations might modify some or all objects: raise all inventory prices 5%, or apply sharpening to only the TIFF images.

What is common to all these cases is that you want your code to “visit” the objects in sequence. Upon arriving at each object, your code will do something, but in a way that is appropriate to the subclass of that specific object.

You do not know, while you are designing the collection itself, everything you might want to do across the collection in this way. New requirements will come up after you have implemented and tested the super-class, the subclasses, and the collection. You need to be able to add a new kind of process *without having to modify the existing class definitions*. For example you do not want to have to add a new method to the members of the collection.

The Solution
--------------

The Visitor Pattern is a general solution to this dilemma. 

First, create an abstract class `Visitor`. It represents the generic task of looking at one element of the collection.

For every new collection-scanning operation you want to implement, now or in the future, you create a subclass of `Visitor` that implements the work to be done by that operation, on one object. For example, if you want to scan the collection to find a maximum value, you might create 

    Class MaximumVisitor(Visitor)

And in it, you will define how to extract a maximum from an object in the collection. I’ll come back to this.

Each subclass in the collection must also define a single method that is conventionally called `accept()` — I think it should have been called `knock_knock()` or maybe `welcome()` — which accepts a visit. This is the only concession that the elements of the collection make to support visiting operations of any kind.

The argument to `accept()` is an instance of Visitor — any instance, whether a MaximumVisitor or a PrintVisitor or CalculateTaxVisitor. It doesn’t matter. The code of `accept()` is very simple. It’s the same in every subclass, except it has its own classname in it:

    class Gorilla(Mammal):
        …
        def accept( visitor:Visitor ):
            return visitor.visitGorilla(self)

    class Rodent(Mammal):
        …
        def accept( visitor:Visitor ):
            return visitor.visitRodent(self)
 

That’s it. Each subclass calls a method of the visitor that is named uniquely for that subclass (but see note at end), and returns whatever that method returns (see other note at end).

Each specific subclass of Visitor must provide a separate method, with an appropriate name, for each subclass that can exist in the collection. The MaximumVisitor has to define a method `visitGorilla()`, a method `visit_Rodent()`, and so forth, for every possible subclass it might visit. And so must the CalculateTaxVisitor, and any other specific visitor. However, this code is confined to that single type of visitor. No changes are required in the collection or any of the collection subclasses, or in any other Visitor type.

In order to process the entire collection for one purpose -- to perform a *visitation*, as we might call it -- the Python code is simply,

    max_visit = MaximumVisitor() # create a visitor object
    for element in collection:
        element.accept(max_visit) # present the visitor to each object

Every element is visited and the visitor is handed to `accept()`; `accept()` calls the specific method of the visitor for that subclass. To that method the object passes itself, that is, a reference to the object being visited. The visitor can then sample or modify its host object in any way that the host supports.

To ensure that a given visitor fully implements all the necessary methods, the Visitor superclass defines abstract versions of them:

    class Visitor:
        def visit_Rodent(item:object):
            raise NotImplementedError('Rodent visit')

And so forth for all the necessary methods. If a subclass of Visitor fails to override the inherited method with its own, an error is raised with some helpful text.

So to implement a new *visitation*, we only need to code a new subclass of `Visitor` that defines a method for each possible subclass to do its work.
  
Note about visitor names
-------------------------

In languages that permit function overloading, you can define methods that have the same name, but differ in the type of argument they accept. In these languages (e.g. Java) it is not necessary for the `accept()` method to call a particular method of `visitor` that is named for its class. It simply calls `visitor.visit(self)`. The compiler works out that the type of the argument to `visitor.visit(self)` is a Gorilla, say, or a Rodent, and it calls the correct method of the visitor depending on that.

Note about visitor return values
---------------------------------

The collection object doesn't know if this visitor returns anything, or what type of thing it returns. In Python that is not a problem. All Python functions return something. If they do not have an explicit `return` statement, they return `None`. It is not required to declare what the type of return may be. The `accept()` method just passes it on.

In other languages, it is necessary to declare whether, and what, is returned. In the Java of *Crafting Interpreters* this is dealt with using "generic" types. The `Visitor` is defined as an "interface" within the `Expr` class (not as a separate class) and its methods are defined using a generic, a single `R` (for return type?). Then the `accept()` method of each subclass starts

       <R> R accept(Visitor<R> visitor) {

which I frankly don't understand. In general I believe it tells the compiler what type the visitor accepts(?) and returns. But I'm puzzled, in part because I can't find any code in the book that uses this Visitor interface. Different types of visitor would surely have different return values; does that mean for every use of the Visitor Interface with a different type `R`, a whole new set of subclasses is created, using that type in place of `R`?
