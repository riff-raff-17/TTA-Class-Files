#include <iostream>
#include <string>
#include <memory>

using namespace std;

class CarWithConstructor {
private:
    int speed;
public:
    string color;

    CarWithConstructor() {
        color = "unknown";
        speed = 0;
        cout << "A car was created" << endl;
    }

    CarWithConstructor(string c, int s){
        color = c;
        speed = s;
        cout << "A " << color << " car was created" << endl;
    }

    ~CarWithConstructor(){
        cout << "A " << color << " car was destroyed" << endl;
    }

    void accelerate() {
        speed += 10;
        cout << "Speed is now " << speed << endl;
    }

    int getSpeed() { return speed; }
};

class Engine {
    public:
    Engine() { cout << "Engine built" << endl; }
    ~Engine() { cout << "Engine destroyed" << endl; }
    void start() {cout << "Vroom" << endl; }
};

void leaky() {
    Engine* e = new Engine();
    e->start();
    //no delete e; -> "Engine destroyed" never happens
}

void leakyWithException(bool badInput){
    Engine* e = new Engine();
    e->start();
    if (badInput) {
        throw runtime_error("bad input"); // jumps out immediately - 
        // delete e; below never runs, even though we wrote it
    }
    delete e;
}

// RAII - Resource Acquisition is Initialization
// Object - region of memory with a type
// Resource - external or limited that needs to be acquired and released

/* Smart pointers - wrapper class around pointers that follows RAII;
they delete what they own automatically when it goes out of scope,
including during exception unwinding

Three to know:
1) std::unique_ptr - exactly one owner. Cannot be copied, only moved.
    The default choice.
2) std::shared_ptr - multiple owners. The object is destroyed when
    the last owner goes away.
3) std::weak_ptr - non-owning observer of a shared_ptr. Used to break
    reference cycles
*/

void notLeaky(){
    unique_ptr<Engine> e = make_unique<Engine>();
    e->start();
}

void safeWithException(bool badInput){
    unique_ptr<Engine> e = make_unique<Engine>();
    if (badInput) {
        throw runtime_error("Bad Input");
    }
    e->start();
}

void sharedDemo(){
    shared_ptr<Engine> e1 = make_shared<Engine>();
    cout << "Owners: " << e1.use_count() << endl; // 1
    {
        shared_ptr<Engine> e2 = e1; // copy is allowed
        cout << "Owners: " << e1.use_count() << endl; // 2
    } // e2 destroyed, but Engine survives - e1 still owns it
    cout << "Owners: " << e1.use_count() << endl; // 1
} // Engine is destroyed at the end

struct Room;

struct Door {
    shared_ptr<Room> connectsTo;
    ~Door() { cout << "Door destroyed" << endl; }
};

struct Room {
    shared_ptr<Door> door;
    ~Room() { cout << "Room destroyed" << endl; }
};

void cycleLeak() {
    auto room = make_shared<Room>();
    auto door = make_shared<Door>();
    room->door = door;
    door->connectsTo = room;
}

struct RoomFixed;

struct DoorFixed {
    weak_ptr<RoomFixed> connectsTo;
    ~DoorFixed() { cout << "Door destroyed" << endl; }
};

struct RoomFixed {
    shared_ptr<DoorFixed> door;
    ~RoomFixed() { cout << "Room destroyed" << endl; }
};

void weakPtrFixed() {
    auto room = make_shared<RoomFixed>();
    auto door = make_shared<DoorFixed>();
    room->door = door;
    door->connectsTo = room;

    if (auto lockedRoom = door->connectsTo.lock()){
        cout << "Room is still alive, accessed safely via lock()" << endl;
    }

    cout << "Function ending" << endl;
}

int main() {
    weakPtrFixed();
}