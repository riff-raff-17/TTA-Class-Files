#include <iostream>

using namespace std;

int max_of_two(int a, int b){
    if (a > b){
        return a;
    } else {
        return b;
    }
}

void print_stars(int count){
    for (int i = 0; i < count; i++){
        cout << "*";
    }
    cout << endl;
}

int main(){
    int points;
    cout << "Enter your score (0-100)";
    cin >> points;

    if (points >= 90){
        cout << "Grade: A";
    } else if (points >= 80){
        cout << "Grade: B";
    } else if (points == 67){
        cout << "Grade: F-";
    } else {
        cout << "Grade: C";
    }

    // While loops
    cout << "While loop" << endl;
    int i = 0;
    while (i < 5){
        cout << i << endl;
        i++;
    }

    // For loops
    cout << "For loop" << endl;
    for (int i = 1; i <= 10; i++){
        cout << i << endl;
    }
}