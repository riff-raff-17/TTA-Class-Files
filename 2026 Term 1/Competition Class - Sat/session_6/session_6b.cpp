#include <iostream>
#include <cmath>

using namespace std;

int main(){
    int x1 = 1;
    int y1 = 2;

    int x2 = 4;
    int y2 = 6;

    double distance = 0;

    int a = x2 - x1;
    int b = y2 - y1;
    distance = sqrt(a * a + b * b);

    cout << distance << endl;
}