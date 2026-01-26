#include <iostream>

using namespace std;

void changeValue(int x) {
    x = 10;   // modifies only the copy
}

int add(int a, int b){
    return a + b;
}

int main() {
    // int a = 5;
    // changeValue(a);
    // cout << a;   // Output: 5
    // return 0;

    int x = 10;
    int y = 11;

    cout << add(x, y) << endl;
}