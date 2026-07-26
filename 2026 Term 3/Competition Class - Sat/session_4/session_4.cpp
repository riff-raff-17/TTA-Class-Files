#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <map>
#include <memory>

using namespace std;

class Player; // forward declaration - Item::use() needs a reference to Player

// --- Items ---
class Item {
protected:
    string name;
    int value;
public:
    Item(string n, int v) : name(move(n)), value(v) {}
    virtual ~Item() { cout << "  [" << name << " destroyed.]" << endl; }
    virtual void use(Player& player) = 0;
    virtual string describe() const = 0;
    const string& getName() const { return name; }
    int getValue() const { return value; }
};

class Potion : public Item {
    int healAmount;
public:
    Potion(string n, int v, int heal) : Item(move(n), v), healAmount(heal) {}
    void use(Player& player) override; // defined after Player is complete
    string describe() const override {
        ostringstream oss;
        oss << name << " (Potion, heals " << healAmount << ", worth " << value << ")";
        return oss.str();
    }
};

class Weapon : public Item {
    int damage;
public:
    Weapon(string n, int v, int dmg) : Item(move(n), v), damage(dmg) {}
    void use(Player& player) override; // equips itself
    int getDamage() const { return damage; }
    string describe() const override {
        ostringstream oss;
        oss << name << " (Weapon, damage " << damage << ", worth " << value << ")";
        return oss.str();
    }
};

class Armor : public Item {
    int defense;
public:
    Armor(string n, int v, int def) : Item(move(n), v), defense(def) {}
    void use(Player& player) override; // equips itself
    int getDefense() const { return defense; }
    string describe() const override {
        ostringstream oss;
        oss << name << " (Armor, defense " << defense << ", worth " << value << ")";
        return oss.str();
    }
};

class Room
{
private:
    string name;
    string description;
    map<string, Room*> exits; // raw pointer for now

public:
    // Constructor - how the Room is created
    Room(string n, string desc) : name(move(n)), description(move(desc)) {}

    // Create exits for the Room
    void setExit(const string &direction, Room *room) { exits[direction] = room; }

    Room *getExit(const string &direction) const
    {
        auto it = exits.find(direction);
        return it == exits.end() ? nullptr : it->second;
    }

    void describe() const
    {
        cout << "\n== " << name << " ==" << endl;
        cout << description << endl;
        if (!exits.empty())
        {
            cout << "Exits:";
            for (const auto &[dir, room] : exits)
                cout << " " << dir;
            cout << endl;
        }
    }

    const string &getName() const { return name; }
};

int main()
{
    cout << "=== Navigation ===" << endl;

    // main() owns every room, via unique_ptr. The raw Room* pointers handed
    // out via setExit()/getExit() are safe because this vector outlives them.
    vector<unique_ptr<Room>> rooms;
    rooms.push_back(make_unique<Room>("Entrance Hall", 
        "A dusty stone hall. Torches flicker on the walls."));
    rooms.push_back(make_unique<Room>("Armory", "Racks of rusted weapons line the walls."));
    rooms.push_back(make_unique<Room>("Damp Cave", "Water drops somewhere in the darkness."));

    rooms[0]->setExit("north", rooms[1].get());
    rooms[1]->setExit("south", rooms[0].get());
    rooms[1]->setExit("east", rooms[2].get());
    rooms[2]->setExit("west", rooms[1].get());

    Room* current = rooms[0].get();
    current->describe();
    cout << "\nCommands: look, go <direction>, quit" << endl;

    string line;
    while (true) {
        cout << "\n> ";
        if (!getline(cin, line)) break;

        istringstream iss(line);
        string cmd;
        iss >> cmd;
        string rest;
        getline(iss, rest);
        if (!rest.empty() && rest.front() == ' ') rest.erase(0, 1);

        if (cmd == "quit"){
            cout << "Good bye!" << endl;
            break;
        } else if (cmd == "look") {
            current->describe();
        } else if (cmd == "go"){
            Room* next = current->getExit(rest);
            if (!next){
                cout << "You can't go that way." << endl;
            } else {
                current = next;
                cout << "You head " << rest << "." << endl;
                current->describe();
            }
        } else{
            cout << "Unknown command." << endl;
        }
    }
}