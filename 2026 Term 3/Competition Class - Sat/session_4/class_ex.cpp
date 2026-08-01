#include <iostream>
#include <string>

using namespace std;

class Dog {
protected:
    string name; // hidden from the outside
    int age;
public:
    // Constructor: runs when a Dog is created
    Dog(string n, int a){
        name = n;
        age = a;
        cout << name << " has been created" << endl;
    }

    // Public methods are how you interact with private data
    void printInfo() {
        cout << name << " is " << age << " years old" << endl;
    }

    void bark() {
        cout << name << " says Woof" << endl;
    }

    // Destructor runs when a Dog goes out of scope
    ~Dog() {
        cout << name << " is being destroyed" << endl;
    }
};

// Puppy inherits from Dog
class Puppy : public Dog {
private:
    string favoriteToy;

public: 
    // Puppy's constructor calls Dog's constructor
    Puppy(string n, int a, string toy) : Dog(n, a) {
        favoriteToy = toy;
        cout << name << " (a puppy) has been created" << endl;
    }

    void play(){
        cout << name << " (age " << age << ") is playing with a " 
        << favoriteToy << endl;
    }

    ~Puppy() {
        cout << name << " (the puppy) is being destroyed" << endl;
    }
};

int main(){
    Dog myDog("Jeff", 3); // constructor
    myDog.bark();  // bark() method
    myDog.printInfo(); // printInfo() method

    // destructor runs automatically at the end

    Puppy myPuppy("Joe", 1, "ball");
    myPuppy.bark(); // inherited from Dog
    myPuppy.printInfo(); // inherited from Dog
    myPuppy.play(); // Puppy's own method
}