#include <iostream>
#include <memory>

using namespace std; 

class Engine {
public:
    Engine() { cout << "Engine built" << endl; } 
    ~Engine() { cout << "Engine destroyed" << endl; } 
    void start() {cout << "Vroom" << endl; } 
};

void pointerDemo() {
    Engine* e = new Engine();
    e->start();
    delete e;
}

void leaky() {
    Engine* e = new Engine();
    e->start();
}

// RAII - Resource Acquisition Is Initialization
void notLeakyAnymore() {
    unique_ptr<Engine> e = make_unique<Engine>();
    e->start();
}

int main() {
    notLeakyAnymore();
}