#include <iostream>
#include <vector>

using namespace std;

int main(){
    ios::sync_with_stdio(0);
    cin.tie(0);

    int n, d;
    cin >> n >> d;

    vector<long long> buttons(n);
    for (int i = 0; i < n; ++i){
        cin >> buttons[i];
    }

    // printing for debugging
    // cout << n << " " << d << "\n";
    // for (int x : buttons) cout << x << " ";

    long long largest = 0;
    long long moves = 0;

    while (!buttons.empty()){
        // 1) Get the last element
        long long last = buttons.back();

        buttons.pop_back();

        if (last > largest){
            moves += ((last - largest) * (buttons.size()));
            largest = last;
        }
    }

    cout << moves << "\n";
}