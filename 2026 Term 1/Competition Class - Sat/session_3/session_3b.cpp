#include <iostream>
#include <vector> // remember to include if you are working with vectors
#include <string> // ditto for strings

using namespace std;

int main(){
    // Vectors
    vector<string> floors = {"wood", "concrete", "marble", "plastic", "bricks", "carpet"};

    // Iterate over vector elements
    for (string i : floors){
        cout << i << endl;
    }

    // Accessing a vector
    cout << floors[0] << endl;
    cout << floors[floors.size() - 1] << endl;
    cout << floors.at(1) << endl;

    // front() and back()
    cout << floors.front() << endl; // Access the first element
    cout << floors.back() << endl; // Access the last element

    // Change elements
    floors[0] = "hardwood";
    cout << floors[0] << endl;

    // Add and remove elements of a vector
    floors.push_back("steel");

    floors.pop_back();

    floors.push_back("transistors");

    // Sample problems
    // Use a vector to read `n` numbers. Print how many are even.
    int n;
    cin >> n;

    vector<int> v(n);

    // Read n numbers
    for (int i = 0; i < n; i++){
        cin >> v[i];
    }

    cout << "Vector --------" << endl;
    for (int i : v){
        cout << i << endl;
    }

    // count even numbers
    int even_numbers = 0
    for (int num : v){
        if (num % 2 == 0){
            even_numbers++;
        }
    }

    cout << even_numbers << endl;
}