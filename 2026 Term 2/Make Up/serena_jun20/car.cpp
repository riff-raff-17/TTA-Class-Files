// ============================================================
// OOP BASICS — LIVE CODE FILE
// Build this UP in stages during the lesson. Each STAGE below
// corresponds to a section in lesson_talking_points.md
//
// Tip: comment out later stages while live-coding earlier ones,
// or keep a separate "final" copy and type into a blank file.
// ============================================================

#include <iostream>
#include <string>
using namespace std;

// ------------------------------------------------------------
// STAGE 2: Classes & Objects
// ------------------------------------------------------------
// Start with just this. Type it live.

class Car {
public:
    string color;
    int speed;

    void accelerate() {
        speed += 10;
        cout << "Vroom! Speed is now " << speed << endl;
    }

    void honk() {
        cout << "Beep beep!" << endl;
    }
};

// In main(), show creating two objects and that each has its
// own data:
//
// Car car1;
// car1.color = "red";
// car1.speed = 0;
// car1.accelerate();
//
// Car car2;
// car2.color = "blue";
// car2.speed = 0;
// car2.accelerate();
// car2.accelerate();
//
// cout << car1.speed << " vs " << car2.speed << endl;
// -> shows they don't share state


// ------------------------------------------------------------
// STAGE 3: Access Specifiers & Encapsulation
// ------------------------------------------------------------
// Evolve the class: make speed private, add getters/setters.
// Demo the "bug" first: car1.speed = -500; (nonsense, but the
// compiler allows it) -- THEN fix it with encapsulation.

class CarEncapsulated {
private:
    int speed;       // now hidden
public:
    string color;

    void accelerate() {
        speed += 10;
        cout << "Vroom! Speed is now " << speed << endl;
    }

    // Getter
    int getSpeed() {
        return speed;
    }

    // Setter with validation -- this is the payoff moment
    void setSpeed(int s) {
        if (s < 0) {
            cout << "Speed can't be negative! Ignoring." << endl;
            return;
        }
        speed = s;
    }
};

// In main(), show:
// CarEncapsulated car3;
// car3.setSpeed(-100);     // rejected
// car3.setSpeed(50);       // accepted
// cout << car3.getSpeed() << endl;
//
// Try car3.speed = -100; here too -- show it won't even compile.


// ------------------------------------------------------------
// STAGE 4: Constructors & Destructors
// ------------------------------------------------------------
// Evolve again: add a constructor so we can't forget to
// initialize. Add a destructor just to show it exists.

class CarWithConstructor {
private:
    int speed;
public:
    string color;

    // Default constructor
    CarWithConstructor() {
        color = "unknown";
        speed = 0;
        cout << "A car was created!" << endl;
    }

    // Parameterized constructor
    CarWithConstructor(string c, int s) {
        color = c;
        speed = s;
        cout << "A " << color << " car was created!" << endl;
    }

    // Destructor
    ~CarWithConstructor() {
        cout << "A " << color << " car was destroyed." << endl;
    }

    void accelerate() {
        speed += 10;
        cout << "Vroom! Speed is now " << speed << endl;
    }

    int getSpeed() { return speed; }
};

// In main(), show:
// CarWithConstructor car4;                  // default constructor
// CarWithConstructor car5("green", 20);     // parameterized
// car5.accelerate();
//
// Mention: destructor message prints automatically at end of
// main() / end of scope -- no manual cleanup needed for this
// simple example.


// ------------------------------------------------------------
// STAGE 5: A Taste of Inheritance
// ------------------------------------------------------------
// SportsCar IS-A Car. Reuses everything, adds turbo boost.

class SportsCar : public CarWithConstructor {
public:
    SportsCar(string c, int s) : CarWithConstructor(c, s) {
        cout << "...and it's a SPORTS car!" << endl;
    }

    void turboBoost() {
        accelerate();   // reuse the base class behavior
        accelerate();   // sports cars accelerate twice as hard!
        cout << "TURBO BOOST ENGAGED!" << endl;
    }
};

// In main(), show:
// SportsCar sc("yellow", 0);
// sc.accelerate();     // inherited, works as-is
// sc.turboBoost();      // new behavior
//
// Point out: SportsCar didn't have to redefine color, speed,
// accelerate(), the constructor logic, etc. It got all of that
// for free from Car. That's the "is-a" payoff.


// ------------------------------------------------------------
// CHALLENGE FOR STUDENTS (mentioned at end of lesson):
// Add a "Truck" class that inherits from CarWithConstructor
// and has an extra member variable `cargoWeight`, plus a
// method `loadCargo(int weight)` that adds to it.
// ------------------------------------------------------------
//
// SOLUTION -- don't show this until students have had a chance
// to try it themselves!
//
// Truck IS-A CarWithConstructor, same idea as SportsCar above,
// but the "extra ability" this time is carrying cargo instead
// of a turbo boost.

class Truck : public CarWithConstructor {
private:
    int cargoWeight;   // private, just like speed in the base class
public:
    // Constructor: build the car part via the base class
    // constructor, then initialize the truck-specific part.
    Truck(string c, int s) : CarWithConstructor(c, s) {
        cargoWeight = 0;
        cout << "...and it's a TRUCK, ready to haul!" << endl;
    }

    void loadCargo(int weight) {
        if (weight < 0) {
            cout << "Can't load negative cargo! Ignoring." << endl;
            return;
        }
        cargoWeight += weight;
        cout << "Loaded " << weight << "kg. Total cargo: "
             << cargoWeight << "kg" << endl;
    }

    int getCargoWeight() {
        return cargoWeight;
    }
};

// In main(), show:
// Truck t("white", 0);
// t.accelerate();          // inherited from CarWithConstructor
// t.loadCargo(200);
// t.loadCargo(150);
// cout << t.getCargoWeight() << endl;
//
// Point out the parallels to SportsCar:
//   - Same inheritance syntax: `: public CarWithConstructor`
//   - Same constructor pattern: call the base constructor first,
//     then set up the new part
//   - The new method (loadCargo) is private-data-safe, just like
//     setSpeed() was back in Stage 3 -- encapsulation still applies
//     even in a derived class.


// ------------------------------------------------------------
// MAIN -- uncomment sections as you progress through the lesson
// ------------------------------------------------------------
int main() {
    // ---- Stage 2 demo ----
    Car car1;
    car1.color = "red";
    car1.speed = 0;
    car1.accelerate();

    Car car2;
    car2.color = "blue";
    car2.speed = 0;
    car2.accelerate();
    car2.accelerate();

    cout << car1.color << " car speed: " << car1.speed << endl;
    cout << car2.color << " car speed: " << car2.speed << endl;
    cout << "------------------------" << endl;

    // ---- Stage 3 demo ----
    CarEncapsulated car3;
    car3.color = "black";
    car3.setSpeed(-100);   // rejected, see validation message
    car3.setSpeed(50);     // accepted
    cout << "Car3 speed: " << car3.getSpeed() << endl;
    cout << "------------------------" << endl;

    // ---- Stage 4 demo ----
    CarWithConstructor car4;
    CarWithConstructor car5("green", 20);
    car5.accelerate();
    cout << "------------------------" << endl;

    // ---- Stage 5 demo ----
    SportsCar sc("yellow", 0);
    sc.accelerate();
    sc.turboBoost();
    cout << "------------------------" << endl;

    // ---- Challenge solution demo: Truck ----
    Truck t("white", 0);
    t.accelerate();          // inherited from CarWithConstructor
    t.loadCargo(200);
    t.loadCargo(150);
    t.loadCargo(-50);        // rejected by validation
    cout << "Total cargo: " << t.getCargoWeight() << "kg" << endl;
    cout << "------------------------" << endl;

    return 0;
}