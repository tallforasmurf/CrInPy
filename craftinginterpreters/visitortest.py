'''
This is my adaptation of the Python code found in the Wikipedia article,

https://en.wikipedia.org/wiki/Visitor_pattern#Python_example

'''

from abc import ABCMeta, abstractmethod

'''
CarElement is the generic, or abstract, class for all parts of a car.
All elements of the collection descend from this class.
'''
class CarElement:
    '''
    It is allowed to have a class variable in an abstract class.
    '''
    notImplementedMessage = "You should implement this."
    '''
    I have yet to learn what benefit comes from the following 2 lines!
    '''
    __metaclass__ = ABCMeta
    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError(CarElement.notImplementedMessage)

'''
The following are the various things that can turn up on a Car collection.
Note that they have different attributes (members); these are the
differences a visitor must expect and deal with.
'''
class Body(CarElement):
    def __init__(self):
        self.looks = "a Wonderland"
    '''oh dear did we forget to implement this?'''
    def accept(self, visitor):
        visitor.visitBody(self)

class Engine(CarElement):
    def __init__(self):
        self.noise = "vroom, vroom"
    def accept(self, visitor):
        visitor.visitEngine(self)

class Wheel(CarElement):
    def __init__(self, name):
        self.name = name # e.g. "front left"
    def accept(self, visitor):
        visitor.visitWheel(self)

'''
This class represents the collection. In the Wikipedia code, it is also a
subclass of CarElement -- but I see no necessity for that, it is a needless
complication. A collection is not at all the same thing as an element of a
collection, and needn't be related to it.

Indeed this needn't be a class at all; it could be a file or an array. Making
Car a class is convenient in that we can get the initialization done in one
place.
'''
class Car:
    '''populate the collection with CarElements'''
    def __init__(self):
        self.elements = [
            Wheel("front left"), Wheel("front right"),
            Wheel("back left"), Wheel("back right"),
            Body(), Engine()
        ]

    #def accept(self, visitor):
        #for element in self.elements:
            #element.accept(visitor)
        #visitor.visitCar(self)
'''
This is the abstract class of ANY visitor to a collection of
CarElement objects. It predefines the visitXxxxx() methods that
any real visitor needs to define.
'''
class CarElementVisitor:
    def __init__(self):
        self.msgname = self.__class__.__name__
    '''
    And again, I see no benefit yet from the following 2 lines.
    '''
    __metaclass__ = ABCMeta
    @abstractmethod
    def visitBody(self, element):
        raise NotImplementedError(f"visitBody in {self.msgname}")
    @abstractmethod
    def visitEngine(self, element):
        raise NotImplementedError(f"visitEngine in {self.msgname}")
    @abstractmethod
    def visitWheel(self, element):
        raise NotImplementedError(f"visitWheel in {self.msgname}")

class CarElementRunVisitor(CarElementVisitor):
    def visitBody(self, body):
        print("Opening door to", body.looks)
    def visitWheel(self, wheel):
        print("Kicking my {} wheel.".format(wheel.name))
    def visitEngine(self, engine):
        print("The engine goes", engine.noise)

class CarElementPrintVisitor(CarElementVisitor):
    def visitBody(self, body):
        print("This body is",body.looks)
    def visitWheel(self, wheel):
        print(f"Visiting {wheel.name} wheel.")
    def visitEngine(self, engine):
        print("Engine looks like",engine.noise)

'''
Execute the above code, performing two visitations.

First, create the collection
'''
car = Car()
'''
In this visitation, every element is passed a newly-made instance of the
visitor class. That's what the wiki code does, and it is ok but not
performant, making a new object every time.
'''
print('Looking at the car:')
for element in car.elements:
    element.accept(CarElementPrintVisitor())
'''
In this version, we make a single visitor object and pass it every time.
Not only is this less overhead, but many visitor classes I can imagine
might well have object variables that need to be preserved, sums, averages,
counts and the like.
'''
print('Using the car:')
avon = CarElementRunVisitor()
for element in car.elements:
    element.accept(avon) # avon calling ;-)

