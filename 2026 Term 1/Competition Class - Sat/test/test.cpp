#include <iostream>
#include <vector>
using namespace std;

int main() {
	int N, M;
	cin >> N >> M;
	vector<vector<int>> adj(N);
	for (int i = 0; i < M; ++i) {
		int u, v;
		cin >> u >> v;
		adj.at(u).push_back(v);
		adj.at(v).push_back(u);
	}
	{
		int u = 1;
		// print number of vertices adjacent to u
		cout << "deg(u) = " << adj.at(u).size() << endl;
		// print all edges with u as an endpoint
		for (int v : adj.at(u)) cout << "{" << u << ", " << v << "}" << "\n";
	}
}