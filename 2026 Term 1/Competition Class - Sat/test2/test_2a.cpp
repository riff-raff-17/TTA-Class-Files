// naive approach

#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
        int n;
        cin >> n;

        vector<int> a(n), b(n);
        for(auto& it: a) cin >> it;
        for(auto& it: b) cin >> it;

        int ans = 0;
        for(int bi: b) {
                if(bi!=a[0]) ans++;
                a.erase(find(a.begin(), a.end(), bi));
        }

        cout << ans;
}