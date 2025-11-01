#include <iostream>
#include <vector>

using namespace std;

int n = 8;
vector<vector<int>> adj(n);
vector<bool> visited(n);

void dfs(int current_node){
    if (visited[current_node]) return;    
    visited[current_node] = true;

    cout << "Visiting node " << current_node << endl;

    for (int neighbor : adj[current_node]){
        dfs(neighbor);
    }
}

int main() {
    // Adjacency list
    adj[0] = {1, 2, 4};
    adj[1] = {0, 3, 4};
    adj[2] = {0, 5};
    adj[3] = {1};
    adj[4] = {0, 1};
    adj[5] = {2};

    adj[6] = {7};
    adj[7] = {6};

    int start_node = 2;

    if (start_node < 0 || start_node >= n){
        cout << "Invalid node number!" << endl;
    }

    cout << "Starting DFS at node " << start_node << endl;
    dfs(start_node);
}