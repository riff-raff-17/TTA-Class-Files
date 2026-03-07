/* initial approach: go from left to right, and swap elements all the way 
to the left if needed
*/

#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main(){
    int n;
    cin >> n;

    vector<int> a(n), b(n);

    for (int i = 0; i < n; i++) cin >> a[i];
    for (int i = 0; i < n; i++) cin >> b[i];

    /*
    vector<int> a, b;

    for (int i = 0; i < n; i++){
        int x;
        cin >> x;
        a.push_back(x)
    }
    for (int i = 0; i < n; i++){
        int x;
        cin >> x;
        b.push_back(x)
    }
    */

    int ans = 0;
    for (int i = 0; i < n; i++){
        // Check if b[i] is correct
        if (b[i] != a[0]) ans++;
        a.erase(find(a.begin(), a.end(), b[i]))
    }

    cout << ans;
}