// Shell game solution USACO

#include <algorithm>
#include <iostream>
#include <vector>
#include <array>

using namespace std;

int main() {
    ios::sync_with_stdio(0);
    cin.tie(0);

    int n;
    cin >> n;

    vector<array<int,3> > moves(n);
    for (int i = 0; i < n; ++i) {
        int a, b, g;
        cin >> a >> b >> g;
        moves[i] = {a, b, g};
    }

    int best = 0;
    for (int start = 1; start <= 3; ++start) {
        int peb = start;
        int score = 0;
        for (auto m : moves) {
            int a = m[0], b = m[1], g = m[2];
            if (peb == a) peb = b;
            else if (peb == b) peb = a;
            if (g == peb) ++score;
        }
        best = max(best, score);
    }

    cout << best << '\n';
    return 0;
}