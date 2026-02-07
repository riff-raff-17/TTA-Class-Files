#include <iostream>

using namespace std;

int main(){
    // n = number of frames
    int n;
    cin >> n;
    int largest_seen = 0;

    for (int i = 0; i < n; i++){
        int w, h;
        cin >> w >> h;
        int area = w * h;
        largest_seen = max(area, largest_seen);
    }

    cout << largest_seen << endl;
}