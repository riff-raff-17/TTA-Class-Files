#include <algorithm>
#include <iostream>
#include <vector>
#include <array>

using namespace std;

int main(){
    // undirected weighted graph

    int N = 5; // 5 nodes; can change as needed

    vector<pair<int, int>> adj[N+1];

    adj[1].push_back({2, 5}); // edge = (1, 2), weight = 5
    adj[2].push_back({3, 7});
    adj[3].push_back({4, 6});
    adj[4].push_back({5, 2});
    adj[5].push_back({1, 4});


    int u = 1;

    // print entire adjacency list
    for (int u = 1; u <= N; u++){
        cout << u << ": ";
        for (auto [v, w] : adj[u]){
            cout << "(" << v << ", weight=" << w << ")";
        }
        cout << "\n";
    }

    // outgoing edges from node
    for (auto [v, w] : adj[u]){
        cout << "(" << u << " -> " << v << ", weight=" << w << ")\n"; // (1 -> 2, weight=5)
    }

    // incoming edges to node
    for (int i = 1; i <= N; i++){
        for (auto [v, w] : adj[i]){
            if (v == u){
                cout << "(" << i << " -> " << u << ", weight=" << w << ")\n"; 
            }
        }
    }
}
