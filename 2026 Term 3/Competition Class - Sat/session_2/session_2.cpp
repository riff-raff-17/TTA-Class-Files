#include <iostream>
#include <memory>
#include <vector>
#include <map>
#include <unordered_map>
#include <set>

using namespace std;

class Engine {
public:
    Engine() { cout << "Engine built" << endl; }
    ~Engine() { cout << "Engine destroyed" << endl; }
    void start() { cout << "Vroom" << endl; }
};

// Smart pointers in our Car that owns an Engine
class Car {
private:
    unique_ptr<Engine> engine;
    int speed = 0;
public:
    Car() : engine(make_unique<Engine>()){
        cout << "Car built with its own engine" << endl;
    }
    void start() { engine->start(); }
    void accelerate() { speed += 10; }
    int getSpeed() const { return speed; }
};

void garage() {
    vector<unique_ptr<Car>> cars;
    cars.push_back(make_unique<Car>());
    cars.push_back(make_unique<Car>());

    for (const auto& car : cars) {
        car->start();
    }
}

int main() {
    cout << "--- Pointers and Move Semantics ---" << endl;
    unique_ptr<Engine> a = make_unique<Engine>();
    unique_ptr<Engine> b = move(a);

    if (!a) {
        cout << "a is now empty" << endl;
    }
    b->start();

    vector<unique_ptr<Engine>> engines;
    unique_ptr<Engine> e = make_unique<Engine>();
    engines.push_back(move(e));

    if (!e) {
        cout << "e is now empty" << endl;
    }
    cout << "------------------------------" << endl;
    cout << "--- Containers ---" << endl;
    garage();
}