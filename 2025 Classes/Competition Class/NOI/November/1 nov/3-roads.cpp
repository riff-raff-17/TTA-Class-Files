#include <iostream>
#include <vector>

using namespace std;

int n, m;
vector<vector<int>> adj;
vector<bool> visited;

void dfs(int current_node){
    if (visited[current_node]) return;    
    visited[current_node] = true;
    for (int neighbor : adj[current_node]){
        dfs(neighbor);
    }
}

int main(){
    cin >> n >> m;
    adj.assign(n + 1, {});
    visited.assign(n + 1, false);

    // Read undirected edges
    for (int i = 0; i < m; i++){
        int a, b;
        cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
}