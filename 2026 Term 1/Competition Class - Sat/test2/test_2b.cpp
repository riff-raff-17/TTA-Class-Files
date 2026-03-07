// good approach

#include <iostream>
#include <vector>

using namespace std;

int main() {
    int n;
    cin >> n;

    vector<int> a(n), b(n), pos(n + 1);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
        pos[a[i]] = i;
    }
    for (int i = 0; i < n; i++) cin >> b[i];

    int ans = 0;
    int mn = n;  // smallest original position seen to the right

    for (int i = n - 1; i >= 0; i--) {
        int p = pos[b[i]];
        if (p > mn) ans++;
        mn = min(mn, p);
    }

    cout << ans << '\n';
}