#include <iostream>
#include <vector>
#include <algorithm>
#include <map>

using namespace std;

// Lambda expression
const vector<string> cows = [](){
    vector<string> temp{"Beatrice", "Sue", "Belinda", 
        "Bessie", "Betsy", "Blue", "Bella", "Buttercup"};
    
    sort(begin(temp), end(temp));
    return temp;
}();

int main(){
    map<string, int> cow_inds;
    for (int i = 0; i < cows.size(); i++){
        cow_inds[cows[i]] = i;
    }

    int req_num;
    cin >> req_num;

    vector<vector<int>> neighbors(cows.size());

    for (int i = 0; i < req_num; i++){
        string cow1, cow2, trash;
        cin >> cow1 >>  trash >> trash >> trash >> trash >> cow2;

        // Convert the names to their index in the vector
        int c1 = cow_inds[cow1];
        int c2 = cow_inds[cow2];
        neighbors[c1].push_back(c2);
        neighbors[c2].push_back(c1);
    }

    // order = the output ordering
    // added = whether cow i is in order
    vector<int> order;
    vector<bool> added(cows.size(), false);

    for (int i = 0; i < cows.size(); i++){
        if (!added[i] && neighbors[i].size() <= 1){
            added[i] = true;
            order.push_back(i);

            if (neighbors[i].size() == 1){
                int prev = i;
                int at = neighbors[i][0];
            }
        }
    }
}