/*
Optimal approach: Stores a new ordering vector p, and checks if that order 
is strictly increasing.

Counts how many cows break the original order, and "move them left".
*/

#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main(){
    int n;
    cin >> n;

    vector<int> a(n), b(n), pos(n + 1);
    for (int i = 0; i < n; i++){
        cin >> a[i];
        pos[a[i]] = i;
    }

    for (int i = 0; i < n; i++) cin >> b[i];

    int ans = 0;
    int mn = n; // smallest original position seen to the right

    for (int i = n - 1; i >= 0; i--){
        int p = pos[b[i]];
        if (p > mn) ans++;
        mn = min(mn, p);
    }

    cout << ans << endl;
}