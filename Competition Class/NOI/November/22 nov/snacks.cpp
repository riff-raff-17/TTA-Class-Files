#include <iostream>
#include <vector>
#include <map>

using namespace std;
using ll = long long;

int main(){
    ll n, q;
    cin >> n >> q;

    ll sum = 0;

    vector<ll> snacks(n);
    for (ll i = 0; i < n; i++){
        cin >> snacks[i];
        sum += snacks[i];
    }
    cout << sum << endl;

    map<ll, ll> freq;
    for (ll v: snacks) freq[v]++;

    while (q--){
        ll x, y, z;
        cin >> x >> y >> z;

        // iterate over all keys in [x, y]
        auto it = freq.lower_bound(x);
        vector<pair<ll, ll>> to_update;
        while (it != freq.end() && it -> first <= y){
            if (it -> first != z) to_update.emplace_back(it->first, it->second);
            ++it;
        }

        for (auto [val, cnt]: to_update){
            sum += (z - val) * cnt;
            freq[z] += cnt;
            freq.erase(val);
        }
        cout << sum << endl;
    }
}