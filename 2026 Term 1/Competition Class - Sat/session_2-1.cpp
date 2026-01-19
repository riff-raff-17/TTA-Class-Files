#include <iostream>

using namespace std;

int main() {
    int a = 10;
    int b = 3;

    // Arithmetic
    cout << "a + b = " << a + b << endl;
    cout << "a - b = " << a - b << endl;
    cout << "a * b = " << a * b << endl;
    cout << "a / b = " << a / b << endl; // integer division
    cout << "a % b = " << a % b << endl;

    cout << "------------------------" << endl;


    int score;
    cout << "Enter your score (0 - 100): ";
    cin >> score;

    // Simple if
    if (score > 100 || score < 0){
        cout << "Invalid score!" << endl;
    }
    else if (score >= 50){
        cout << "You passed!" << endl;
    } else{
        cout << "You failed :(" << endl;
    }

    // Multiple conditions
    int age;
    cout << "Enter your age: ";
    cin >> age;

    if (!(age <= 13) && !(age >= 19)){
        cout << "You are a teenager" << endl;
    }

    // Short Hand If...Else (Ternary Operator)
    int time = 20;
    string result = (time < 18) ? "Good day." : "Good evening.";
    cout << result;


    if (time < 18){
        result = "Good day.";
    }
    else {
        result = "Good evening.";
    }
    cout << result;

}