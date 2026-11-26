#include <algorithm>
#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <set>

using namespace::std;

// tiny helpers
template <typename Container>
void print(const char* label, const Container& c) {
    cout << label << ": [";
    bool first = true;
    for (const auto& x : c) {
        cout << (first ? "" : ", ") << x; // [1, 2, 3, 4]
        first = false;
    }
    cout << "]\n";
}

void section(const char* title) { cout << "\n=== " << title << " ===\n"; }

// vector: size vs capacity, reserve vs resize, emplace, invalidation
void demo_vector() {
    section("A1. vector");

    // Capacity
    vector<int> v;
    size_t lastCap = v.capacity();
    for (int i = 0; i < 20; i++) {
        v.push_back(i);
        if (v.capacity() != lastCap) {
            cout << "  size " << v.size() << " -> capacity " << v.capacity() << '\n';
            lastCap = v.capacity();
        }
    }

    // reserve() allocates but creates no elements. resize() creates elements.
    vector<int> a; a.reserve(5);
    vector<int> b; b.resize(5);
    cout << "  reserve(5): size=" << a.size() << " cap=" << a.capacity() << '\n';
    cout << "  resize(5):  size=" << b.size() << " cap=" << b.capacity() << '\n';
    cout << "a[0]=" << a[0] << "  b[0]=" << b[0] << '\n';
}

// map vs unordered_map
void demo_maps() {
    section("A2. map vs unordered_map");

    // map: red-black tree, sorted by key
    // unordered_map: hash table, no order
    map<string, int> ordered{{"pear", 3}, {"apple", 1}, {"fig", 2}};
    unordered_map<string, int> hashed(ordered.begin(), ordered.end());

    cout << "  map iterates sorted:";
    for (const auto& [key, value] : ordered)
        cout << ' ' << key << '=' << value;
    cout << '\n';

    // operator inserts a default value if the key is missing
    cout << "  size before ordered[\"banana\"]: " << ordered.size() << '\n';
    if (ordered["banana"] == 0) { /* just looking...*/ }
    cout << "  size after:                      " << ordered.size() << '\n';

    // Looking up without inserting
    if (auto it = ordered.find("kiwi"); it != ordered.end())
        cout << "  found kiwi\n";
    else
        cout << "  no kiwi, and nothing was inserted: " << ordered.size() << '\n';

    // Insertion helpers:
    auto [pos, inserted] = ordered.try_emplace("apple", 99);  // does NOT overwrite
    cout << "  try_emplace apple: inserted=" << boolalpha << inserted
         << " value=" << pos->second << '\n';
    ordered.insert_or_assign("apple", 99);  // DOES overwrite
    cout << "  insert_or_assign apple: " << ordered["apple"] << '\n';

    unordered_map<char, int> freq;
    for (char c : string("mississippi")) ++freq[c];
    cout << "  's' appears " << freq['s'] << " times\n";
}

// set / multiset: sorted containers
void demo_sets() {
    section("A3. set / multiset");

    set<int> s{5, 1, 4, 1, 3};  // duplicates dropped, kept sorted
    print("  set", s);
    cout << "  min=" << *s.begin() << " max=" << *s.rbegin() << '\n';

    
}

int main() {
    demo_vector();
    demo_maps();
    demo_sets();
}