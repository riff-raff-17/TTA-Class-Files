#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main(){
    ios::sync_with_stdio(0);
    cin.tie(0);

    int n;
    cin >> n;

    cout << n;

    vector<int> train(n), bus(n);
    for (int i=0; i < n; i++){
        cin >> train[i];
    }
    for (int i=0; i < n; i++){
        cin >> bus[i];
    }

    int total_t = 0;
    for (int i=0; i < n; i++){
        total_t += min(train[i], bus[i]);
    }
}