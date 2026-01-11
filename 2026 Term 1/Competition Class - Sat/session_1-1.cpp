// How C++ runs and Hello World

/* This is a longer comment
It can go across multiple lines
*/

// This line includes the input/output library
#include <iostream>

// This allows us to use names like cout without writing std::xx
using namespace std;

// Every C++ program MUST have a main function
int main() {

    // Print text to the console
    // MUST end with ;
    cout << "Hello, my name is Teacher Rafa" << endl; // endl is endline

    cout << "This is a C++ program" << endl;

    // You can also print numbers
    cout << "123" << endl;
    cout << 123 << endl;

    // \n is the newline command!
    cout << "This\nis\nall\non\nnewlines" << endl;

    // (Somewhat) optional
    return 0;
}
