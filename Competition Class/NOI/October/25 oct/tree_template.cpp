/* Tree Input Template*/

#include <iostream>
#include <vector>
#include <queue>
using namespace std;

const int MAXN = 100005;
vector<int> adj[MAXN]; // adjacency list for the tree
int parent[MAXN];
int depth[MAXN];
int subtree_size[MAXN];
int n;

void dfs(int node, int par){
    parent[node] = par;
    for (int nxt : adj[node]){
        if (nxt == par) continue; // avoid going back to parent
        depth[nxt] = depth[node] + 1;
        dfs(nxt, node);
    }
}

int dfs_subtree(int node, int par){
    subtree_size[node] = 1; // count itself
    for (int nxt : adj[node]){
        if (nxt == par) continue;
        subtree_size[node] += dfs_subtree(nxt, node);
    }
    return subtree_size[node];
}

void bfs(int start){
    queue<int> q;
    q.push(start);
    parent[start] = 0;
    depth[start] = 0;

    while (!q.empty()){
        int node = q.front();
        q.pop();

        for (int nxt : adj[node]){
            if (nxt == parent[node]) continue;
            parent[nxt] = node;
            depth[nxt] = depth[node] + 1;
            q.push(nxt);
        }
    }
}

int main(){
    cin >> n; // Number of nodes
    for (int i = 0; i < n - 1; i++){
        int u, v;
        cin >> u >> v;
        adj[u].push_back(v);
        adj[v].push_back(u);
    }

    // // Print adjacency list for debugging
    // for (int i = 1; i <= n; i++){
    //     cout << "Node " << i << ": ";
    //     for (int nxt : adj[i]){
    //         cout << nxt << " ";
    //     }
    //     cout << endl;
    // }

    depth[1] = 0;
    dfs(1, 0);
    cout << "DFS method" << endl;
    // Example: parent and depth array
    for (int i = 1; i <= n; i++){
        cout << "Node " << i << " - Parent: " << parent[i]
            << ", Depth: " << depth[i] << endl;
    }

    bfs(1);
    cout << "\n" << "BFS method" << endl;
    // Example: parent and depth array
    for (int i = 1; i <= n; i++){
        cout << "Node " << i << " - Parent: " << parent[i]
            << ", Depth: " << depth[i] << endl;
    }

    dfs_subtree(1, 0);
    for (int i = 1; i <= n; i++){
        cout << "Node " << i << " - Subtree Size: " << subtree_size[i] << endl;
    }

}