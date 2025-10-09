#include <iostream>
#include <vector>
#include <queue>
using namespace std;

void bfs(int start_node, vector<vector<int>> adj, vector<bool> visited){
    int n = adj.size();

    if (start_node < 0 || start_node >= n){
        cout << "Invalid node" << endl;
    }

    queue<int> q;
    q.push(start_node);
    visited[start_node] = true;

    while (!q.empty()){
        int current_node = q.front();
        q.pop();

        cout << "Visting node " << current_node << endl;

        for (int neighbor : adj[current_node]){
            if (!visited[neighbor]){
                visited[neighbor] = true;
                q.push(neighbor);
            }
        }
    }
}

int main(){
    int n = 6;
    vector<vector<int>> adj(n);
    vector<bool> visited(n);

    adj[0] = {1, 2};
    adj[1] = {0, 3, 4};
    adj[2] = {0, 3};
    adj[3] = {1, 2, 4};
    adj[4] = {1, 3};

    int start_node = 2;

    if (start_node < 0 || start_node >= n){
        cout << "Invalid node" << endl;
    }

    cout << "Starting BFS at node " << start_node << endl;

    bfs(start_node, adj, visited);
}