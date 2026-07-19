#include <iostream>
#include <string>

using namespace std;

class Car {
public: 
    string color; 
    int speed;
    
    void accelerate() {
        speed += 10;
        cout << "Speed is now " << speed << endl;
    }
};

class CarEncapsulated {
private:
    int speed; // now hidden
public:
    string color;

    void accelerate() {
        speed += 10;
        cout << "Speed is now " << speed << endl;
    }

    // Getter
    int getSpeed() {
        return speed;
    }

    // Setter with validation
    void setSpeed(int s){
        if (s < 0) {
            cout << "Speed can't be negative" << endl;
            return;
        }
        speed = s;
        cout << "Speed is now " << speed << endl;
    }
};

class CarConstructor {
private:
    int speed;
public:
    string color;

    // Default constructor
    CarConstructor() {
        color = "unknown";
        speed = 0;
        cout << "A car was created" << endl;
    }

    // Parameterized constructor
    CarConstructor(string c, int s){
        color = c;
        speed = s;
        cout << "A " << color << " car was created" << endl;
    }

    // Destructor
    ~CarConstructor() {
        cout << "A " << color << " car was destroyed" << endl;
    }
};

int main() {
    // Car car1;
    // car1.color = "red";
    // car1.speed = 10;

    // Car car2;
    // car2.color = "blue";
    // car2.speed = 0;

    // CarEncapsulated car3;
    // car3.setSpeed(-100); // rejected
    // car3.setSpeed(50); // accepted 

    CarConstructor car4; // default constructor
    CarConstructor car5("green", 20); // parameterized
}