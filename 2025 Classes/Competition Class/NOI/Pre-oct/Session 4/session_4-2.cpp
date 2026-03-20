#include <algorithm>
#include <iostream>
#include <vector>
#include <array>

using namespace std;

int main() {
    int N = 5;

    vector<pair<int,int>> adj[N + 1];

    adj[1].push_back({2, 5}); // edge = (1, 2), weight = 5
    adj[2].push_back({3, 7});
    adj[3].push_back({4, 6});
    adj[4].push_back({5, 2});
    adj[5].push_back({1, 4});

    int u = 1;

    // print entire adjacency list (the graph)
    for (int u = 1; u < N; u++) {
        cout << u << ": ";
        for (auto [v, w] : adj[u]) {
            cout << "(" << v << ", weight=" << w << ") ";
        }
        cout << "\n";
    }

    cout << "\nNodes connected to " << u << ":\n";

    // outgoing edges from u
    for (auto [v, w] : adj[u]) {
        cout << "(" << u << " -> " << v << ", weight=" << w << ")\n";
    }

    // incoming edges to u
    for (int x = 1; x < N; x++) {
        for (auto [v, w] : adj[x]) {
            if (v == u) {
                cout << "(" << x << " -> " << u << ", weight=" << w << ")\n";
            }
        }
    }
}
