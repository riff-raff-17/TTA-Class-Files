#include <iostream>
#include <string>
using namespace std;

// Classes and Objects
class Car{
public:
    string color;
    int speed;

    void accelerate() {
        speed += 10;
        cout << "Vroom! Speed is now " << speed << endl;
    }
};

class CarEncapsulated {
private:
    int speed;
public:
    string color;

    void accelerate() {
        speed += 10;
        cout << "Vroom! Speed is now " << speed << endl;
    }

    int getSpeed() { return speed; };

    void setSpeed(int s) {
        if (s < 0) {
            cout << "Error: Speed can't be negative" << endl;
            return;
        }
        speed = s;
    }
};

class CarWithConstructor {
private:
    int speed;
public:
    string color;

    // Default constructor
    CarWithConstructor() {
        color = "unknown";
        speed = 0;
        cout << "A car was created" << endl;
    }

    // Parameterized constructor
    CarWithConstructor(string c, int s){
        color = c;
        speed = s;
        cout << "A " << color << " car with speed " << speed << " was created" << endl;
    }

    // Destructor (sort of optional)
    ~CarWithConstructor(){
        cout << "A car was destroyed" << endl;
    }

    void accelerate() {
        speed += 10;
        cout << "Vroom! Speed is now " << speed << endl;
    }

    int getSpeed() { return speed; };
};

int main() {
    CarWithConstructor car4; // default constructor
    cout << car4.color << " " << car4.getSpeed() << endl;

    CarWithConstructor car5("green", 20);
    cout << car5.color << " " << car5.getSpeed() << endl;
}
