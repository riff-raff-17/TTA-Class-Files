#include <iostream>
#include <vector>
using namespace std;

vector<vector<int>> adj;
vector<bool> visited;

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
    int n, m;

    adj.assign(n, {});
    visited.assign(n, false);

    cin >> n >> m;

    for (int i = 0; i < m; ++i){
        int x, y;
        cin >> x >> y;
        adj[x].push_back(y);
        adj[y].push_back(x);
    }

    dfs(0);

    // Check if connected
    bool connected = true;
    for (bool v : visited){
        if (!v) {
            connected = false;
            break;
        }
    }

    cout << (connected ? "Connected" : "Not connected") << endl;
}