#include <iostream>
#include <vector> // remember to include if you are working with vectors
#include <string> // ditto for strings

using namespace std;

int main(){
    // Arrays

    // Indices start at 0
    int numbers[5];

    // Slicing
    // ARRAY_NAME[x]
    int idx = 0;
    cout << "Index " << idx << ": " << numbers[idx];

    cout << endl;
    cout << "-----------------------" << endl;

    // Strings
    string name;

    cout << "Enter your full name: ";

    getline(cin, name);

    cout << "Hello, " << name << endl;

    int idx_s = 0;
    cout << "Index " << idx_s << ": " << name[idx_s] << endl;

    // Length of strings
    cout << "Length: " << name.length() << endl;

    // Accessing last index
    cout << "Last char: " << name[name.length() - 1] << endl;

    // Change string characters
    name[2] = 'B';
    cout << "Changed name: " << name << endl;

    // at() function
    string safe_string = "Hello";

    cout << safe_string.at(10);
}