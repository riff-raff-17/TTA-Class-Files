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

int main() {
    Car car1;
    car1.color = "red";
    car1.speed = 0;
    car1.accelerate();

    Car car2;
    car2.color = "blue";
    car2.speed = 0;
    car2.accelerate();
    car2.accelerate();

    cout << car1.speed << " vs " << car2.speed << endl;
}
