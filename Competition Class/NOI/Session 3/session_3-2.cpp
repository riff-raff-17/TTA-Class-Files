// Mixing Milk solution USACO

#include <algorithm>
#include <iostream>
#include <vector>
#include <array>

using namespace std;

int main() {
    ios::sync_with_stdio(0);
    cin.tie(0);

    // Read (capacity, milk) for the 3 buckets
    vector<array<long long,2>> b(3);
    for (int i = 0; i < 3; ++i) {
        long long c, m;
        cin >> c >> m;
        b[i] = {c, m}; // b[i][0] = capacity, b[i][1] = milk
    }

    // Perform 100 cyclic pours: 1->2, 2->3, 3->1, repeat
    for (int step = 0; step < 100; ++step) {
        int from = step % 3;
        int to   = (step + 1) % 3;

        long long can_take = b[to][0] - b[to][1];             // free space in 'to'
        long long pour = min(b[from][1], can_take);           // how much we actually pour

        b[from][1] -= pour;
        b[to][1]   += pour;
    }

    cout << b[0][1] << '\n' << b[1][1] << '\n' << b[2][1] << '\n';
    return 0;
}
