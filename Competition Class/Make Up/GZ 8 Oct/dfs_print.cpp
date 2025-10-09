#include <iostream>
#include <vector>
using namespace std;

int n = 6; //nodes
vector<vector<int>> adj(n);
vector<bool> visited(n);

void dfs(int current_node){
    if (visited[current_node]) return;
    visited[current_node] = true;

    // For debugging
    cout << "Visiting node " << current_node << endl;

    for (int neighbor : adj[current_node]){
        dfs(neighbor);
    }
}

int main(){
    adj[0] = {1, 2};
    adj[1] = {0, 3, 4};
    adj[2] = {0, 3};
    adj[3] = {1, 2, 4};
    adj[4] = {1, 3};

    int start_node = 2;

    if (start_node < 0 || start_node >= n){
        cout << "Invalid node" << endl;
    }

    // Debugging
    cout << "Starting DFS at node " << start_node << endl;
    dfs(start_node);
}