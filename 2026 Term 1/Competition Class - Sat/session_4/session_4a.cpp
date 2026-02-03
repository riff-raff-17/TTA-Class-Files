#include <iostream>
#include <vector>
#include <algorithm> // vector functions: sort, reverse, find, count, removing

using namespace std;

void printVector(const vector<int>& v, const string& label){
    cout << label << "(size=" << v.size() << ", capacity=" << v.capacity() << "): " ;
    for (int x : v) cout << x << " ";
    cout << endl;
}

// Adds a value to every element (pass by reference)
void addToAll (vector<int>& v, int add){
    for (int& x : v) x += add;
}

// Sums elements (pass by const reference)
int sumVector(const vector<int>& v){
    int total = 0;
    for (int x : v) total += x;
    return total;
}

int main(){
    cout << "--- 1) Creating and initializing vectors ---\n";
    vector<int> a; // empty
    vector<int> b(5); // 5 zeroes: {0, 0, 0, 0, 0}
    vector<int> c(4, 7); // 4 copies of 7: {7, 7, 7, 7}
    vector<int> d = {3, 1, 4, 1, 5};

    printVector(a, "a");
    printVector(b, "b");
    printVector(c, "c");
    printVector(d, "d");

    cout << "--- 2) size vs capacity, reserve, shrink_to_fit ---\n";
    vector<int> v;
    printVector(v, "v (start)");

    v.reserve(10); // pre-allocate space to reduce re-allocations
    printVector(v, "v after reserve(10)");

    for (int i = 1; i <= 6; i++) v.push_back(i * 10);
    printVector(v, "v after push_back");

    // shrink_to_fit requests to reduce capacity to size
    v.shrink_to_fit();
    printVector(v, "v after shrink_to_fit()");

    cout << "--- 3) Adding/removing: push_back, pop_back, clear ---\n";
    v.push_back(999); // adds to the back
    printVector(v, "v after push_back(999)");

    v.pop_back(); // removes last element
    printVector(v, "v after pop_back()");

    vector<int> temp = {1, 2, 3};
    temp.clear();
    printVector(temp, "temp after clear()");

    cout << "--- 4) Accessing elements: [], at(), front(), back() ---\n";
    // [] does NOT do bounds checking
    cout << "v[6] = " << v[6] << endl;

    // at() DOES bounds checking and can throw an exception if out of range
    cout << "v.at(1) = " << v.at(1) << endl;
    // cout << "v.at(6) = " << v.at(6) << endl; // will throw an error

    cout << "front() = " << v.front() << endl;
    cout << "back() = " << v.back() << endl;

    cout << "--- 5) Iteration styles ---\n";
    cout << "Index-based: ";
    for (int i = 0; i < v.size(); i++) cout << v[i] << " ";
    cout << endl;

    cout << "Value-based: ";
    for (int x : v) cout << x << " ";
    
    cout << "--- 6) insert and erase ---\n";
    vector<int> e = {10, 20, 30, 40};

    // insert value at position (begin() + index)
    e.insert(e.begin() + 2, 999);
    printVector(e, "e after insert at index 2");

    // erase elements
    e.erase(e.begin() + 1); // removes 20
    printVector(e, "e after erase index 1");

    // erase a range: remove elements [index 1, index 3) (end index NOT included)
    // Make sure indices are valid before doing this in real programs!
    if (e.size() >= 3){
        e.erase(e.begin() + 1, e.begin() + 3);
        printVector(e, "e after erase range [1, 3)");
    }

}

