#include <iostream>
#include <string>

using namespace std;

int main(){
    int age = 11; // integer
    double height = 1.75; // floating point
    char grade = 'A'; // character (single quotes)
    string name = "Rafa"; // string (double quotes)
    bool isStudent = true; // boolean

    cout << "My age is " << age << ", my height is " << height 
        << ", my grade is " << grade << ", my name is " << name
        << ", am I a student? " << isStudent << endl;

    // Input
    int x, y;
    cout << "Enter two integers: ";
    cin >> x >> y;

    cout << x << " " << y;

    int add = x + y;
    int mult = x * y;
    int sub = x - y;
    int div = x / y;
}