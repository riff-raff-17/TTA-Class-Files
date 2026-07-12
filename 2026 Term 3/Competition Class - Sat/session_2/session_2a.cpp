#include <iostream>
#include <memory>
#include <vector>
#include <map>
#include <unordered_map>
#include <set>
#include <algorithm>

using namespace std;

int main() {
    cout << "--- vector ---" << endl;

    vector<int> speeds = {50, 120, 30, 95};
    speeds.push_back(75); // grows automatically

    for (int s : speeds){
        cout << s << " ";
    }

    cout << endl;

    cout << "First: " << speeds[0] << endl;
    cout << "Total num: " << speeds.size() << endl;

    cout << "\n--- map ---" << endl;

    map<string, int> speedByColor; 
    speedByColor["red"] = 120;
    speedByColor["blue"] = 95;
    speedByColor["green"] = 30;

    for (const auto& [color, speed] : speedByColor){
        cout << color << ": " << speed << endl;
    }

    cout << "\n--- unordered map ---" << endl;

    unordered_map<string, int> fastLookup;
    fastLookup["red"] = 120;
    fastLookup["blue"] = 95;
    fastLookup["green"] = 30;

    cout << "Red car speed: " << fastLookup["red"] << endl;

    for (const auto& [color, speed] : fastLookup){
        cout << color << ": " << speed << endl;
    } // notice the order is not guaranteed

    cout << "\n--- set ---" << endl;

    set<string> visitedRooms;
    visitedRooms.insert("Entrance");
    visitedRooms.insert("Hallway");
    visitedRooms.insert("Entrance"); // duplicate: silently ignored
    visitedRooms.insert("Backyard");

    cout << "Rooms visited: " << visitedRooms.size() << endl;
    for (const auto& room : visitedRooms){
        cout << " - " << room << endl;
    }

    cout << "\n--- algorithms ---" << endl;

    vector<int> algoSpeeds = {50, 120, 30, 95};

    // sort - rearranges elements in place, ascending by default
    sort(algoSpeeds.begin(), algoSpeeds.end());
    cout << "Sorted: ";
    for (int s : algoSpeeds) cout << s << " ";
    cout << endl;

    // find_if - first element matching a condition (a lambda here)
    auto fast = find_if(algoSpeeds.begin(), algoSpeeds.end(), 
        [](int s) { return s > 100; });

    if (fast != algoSpeeds.end()) {
        cout << "First speed over 100: " << *fast << endl;
    }

    // count_if - how many elements match a condition
    int slowCount = count_if(algoSpeeds.begin(), algoSpeeds.end(),
        [](int s){ return s < 60; });
    
    cout << "Speeds under 60: " << slowCount << endl;
}