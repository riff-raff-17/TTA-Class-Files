#include <algorithm>
#include <iostream>
#include <vector>
#include <array>

using namespace std;

int main() {
    int N = 5;

    vector<tuple<int, int, int>> edges;

    edges.push_back({1, 2, 5});
    edges.push_back({2, 3, 7});
    edges.push_back({2, 4, 6});
    edges.push_back({3, 4, 5});
    edges.push_back({4, 1, 2});

    int u = 4;

    cout << "Edges starting from " << u << ":\n";
    for (const tuple<int, int, int>& e : edges){
        int from = get<0>(e);
        int to = get<1>(e);
        int w = get<2>(e);

        if (from == u){
            cout << from << " -> " << to << " (weight=" << w << ")\n";
        }
    }
}