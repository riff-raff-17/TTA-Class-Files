#include <iostream>
#include <vector>

using namespace std;

int main(){
    // N = number of nodes, M = number of edges
    int N, M;
    cin >> N >> M;

    // Adjacency list: {{n1, n2}, {n2, n3}, ...}
    vector<vector<int>> adj(N);

    // Read in all of the edges
    for (int i = 0; i < M; i++){
        // temp variable to hold the nodes
        int u, v;
        cin >> u >> v;
        adj.at(u).push_back(v);
        adj.at(v).push_back(u);
    }

    // inspecting a specific node
    {
        int u = 1;
        // print number of nodes adjacent to u
        cout << "deg(u) = " << adj.at(u).size() << endl;
        // print all edges with u as an endpoint
        for (int v : adj.at(u)) cout << "{" << u << ", " << v << "}" << endl; // {u, v}
    }

}