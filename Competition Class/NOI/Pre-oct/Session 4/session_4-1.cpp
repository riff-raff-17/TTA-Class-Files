#include <algorithm>
#include <iostream>
#include <vector>
#include <array>

using namespace std;

int main() {
    int N = 5;

    vector<vector<int>> adj(N);

    adj[1].push_back(2);
    adj[2].push_back(3);
    adj[2].push_back(4);
    adj[3].push_back(4);
    adj[4].push_back(1);

    int u = 2;

    // print number of vertices adjacent to u

    cout << "deg(u) = " << adj.at(u).size() << endl;

    // print all edges with u as an endpoint

    for (int v : adj.at(u)) cout << "{" << u << ", " << v << "}" << "\n";
}