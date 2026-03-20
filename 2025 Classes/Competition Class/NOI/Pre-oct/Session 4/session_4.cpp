#include <algorithm>
#include <iostream>
#include <vector>
#include <array>

using namespace std;

int main() {
    int N = 5;

    vector<vector<int>>adj(N);

    adj[1].push_back(2); // {1, 2}
    adj[2].push_back(3); // {2, 3}
    adj[2].push_back(4); // {2, 4}
    adj[3].push_back(4); // {3, 4}
    adj[4].push_back(1); // {4, 1}

    int u = 1; // node you want to check

    // print out number of vertices adjacent to u (the degree)
    cout << "deg(u) = " << adj.at(u).size() << endl;

    // print all edges with u as an endpoint
    for (int v : adj.at(u)) cout << "{" << u << ", " << v << "}" << "\n";

    for (int i = 0; i < N; i++){
        for (int v : adj[i]){
            if (v == u){
                cout << "{" << u << ", " << i << "}" << "\n";
            }
        }
    }
}