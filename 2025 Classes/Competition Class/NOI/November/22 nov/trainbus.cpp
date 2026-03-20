#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    int n;
    int total = 0;
    cin >> n;

    vector<int> train(n), bus(n);
    for (int i = 0; i < n; i++){
        cin >> train[i];
    }

    for (int i = 0; i < n; i++){
        cin >> bus[i];
    }

    for (int i = 0; i < n; i++){
        total += min(train[i], bus[i]);
    }

    cout << total << endl;
}