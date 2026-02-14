#include <iostream>

using namespace std;

int main(){
    // n = number of frames
    int n;
    cin >> n;

    // Stores largest value seen so far
    int largest = 0;

    for (int i = 0; i < n; i++){
        // w = width, h = height
        int w, h;
        cin >> w >> h;
        largest = max(w * h, largest);

        // current = w * h;
        // if (current > largest){
        //     largest = current;
        // }
    }

    cout << largest << endl;
}