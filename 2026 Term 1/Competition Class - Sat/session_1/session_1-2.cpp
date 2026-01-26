// Variables, Data Types, and Input

#include <iostream>

using namespace std;

int main(){
    /* 
    When you name a variable:
    it can contain LETTERS (a-z, A-Z), DIGITS (0-9), UNDERSCORE (_)
    MUST start with a letter or _

    it CANNOT:
    Contain spaces or symbols (-, @, #, etc.)
    */ 

    // Integer variables
    int age = 28; // whole number
    int year = 2026; // happy new year

    // Double (decimal)
    double height = 172.2;

    // Character (single quotes!)
    char grade = 'A';

    // String (double quotes!)
    string name = "Rafa";

    // Boolean
    bool isStudent = true;

    cout << "Age: " << age << endl
    << "Year: " << year << endl
    << "Height: " << height << endl
    << "Grade: " << grade << endl
    << "Name: " << name << endl
    << "Student?: " << isStudent << endl;

    cout << "-------------------------" << endl;

    // Input
    cout << "Enter your name: ";
    cin >> name; // reads ONE WORD!

    
    double x;
    double y;

    cin >> x >> y;
    cout << "+: " << x + y << endl
    << "-: " << x - y << endl
    << "* : " << x * y << endl
    << "/: " << x / y << endl;
}