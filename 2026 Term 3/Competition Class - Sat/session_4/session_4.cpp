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

// --- Player ---

class Player {
private:
    string name;
    int health;
    int maxHealth;
    vector<unique_ptr<Item>> inventory;
    Weapon* equippedWeapon = nullptr; // non-owning observer into inventory
    Armor* equippedArmor = nullptr; // non-owning observer into inventory

public: 
    explicit Player(string n, int hp = 100) : name(move(n)), health(hp), maxHealth(hp) {}

    void pickUp(unique_ptr<Item> item) {
        cout << "Picked up " << item->getName() << "." << endl;
        inventory.push_back(move(item));
    }

    Item* findItem(const string& itemName) {
        auto it = find_if(inventory.begin(), inventory.end(),
            [&](const unique_ptr<Item>& i) { return i->getName() == itemName; });
            return it == inventory.end() ? nullptr : it->get();
    }

    unique_ptr<Item> removeItem(const string& itemName) {
        auto it = find_if(inventory.begin(), inventory.end(),
            [&](const unique_ptr<Item>& i) { return i->getName() == itemName; });
        if (it == inventory.end()) return nullptr;
        unique_ptr<Item> found = move(*it);
        inventory.erase(it);
        if (equippedWeapon == found.get()) equippedWeapon = nullptr;
        if (equippedArmor == found.get()) equippedArmor = nullptr;
        return found;
    }

    void listInventory() const {
        if (inventory.empty()) { cout << "  (empty)" << endl; return; }
        for (const auto& item : inventory) cout << "  - " << item->describe() << endl;
    }

    void equipWeapon(Weapon* w) { equippedWeapon = w; cout << name << " equips " 
                                    << w->getName() << "." << endl; }
    void equipArmor(Armor* a) { equippedArmor = a; cout << name << " equips " 
                                    << a->getName() << "." << endl; }
    
    void heal(int amount) {
        health = min(maxHealth, health + amount);
        cout << name << " heals to " << health << "/" << maxHealth << " HP." << endl;
    }

    const string& getName() const { return name; }
    int getHealth() const { return health; }
};

// Item::use() implementations
void Potion::use(Player& player) {
    cout << player.getName() << " drinks the " << name << "." << endl;
    player.heal(healAmount);
}
void Weapon::use(Player& player) { player.equipWeapon(this); }
void Armor::use(Player& player) { player.equipArmor(this); }

class Room {
private:
    string name;
    vector<unique_ptr<Item>> items;
public:
    // Constructor - how the Room is created
    explicit Room(string n) : name(move(n)) {}

    void addItem(unique_ptr<Item> item) { items.push_back(move(item)); }

    unique_ptr<Item> takeItem(const string& itemName) {
        auto it = find_if(items.begin(), items.end(), 
            [&](const unique_ptr<Item>& i) { return i->getName() == itemName; });
        if (it == items.end()) return nullptr;
        unique_ptr<Item> found = move(*it);
        items.erase(it);
        return found;
    }

    void describe() const {
        cout << "\n== " << name << " ==" << endl;
        if (items.empty()) {
            cout << "There is nothing of interest here." << endl;
        } else {
            cout << "Items here:" << endl;
            for (const auto& i : items) cout << "  - " << i->getName() << endl;
        }
    }
};

int main() {
    Room armory("Armory");
    armory.addItem(make_unique<Weapon>("Iron Sword", 50, 15));
    armory.addItem(make_unique<Armor>("Leather Armor", 40, 5));
    armory.addItem(make_unique<Potion>("Fire Potion", 10, 20));

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