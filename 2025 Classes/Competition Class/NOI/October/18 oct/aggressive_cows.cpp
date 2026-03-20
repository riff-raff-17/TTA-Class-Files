#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

bool can_place_cows(vector<int>& stalls, int cows, int dist){
    int placed = 1; // first cow at the first stall
    int last_pos = stalls[0];

    for (int i = 1; i < stalls.size(); i++){
        if (stalls[i] - last_pos >= dist){
            ++placed;
            last_pos = stalls[i];
            if (placed == cows) return true;
        }
    }
    return false;
}

int main() {
    // n = number of stalls, c = cows
    int n, c;
    cin >> n >> c;

    vector<int> stalls(n);
    for (int i = 0; i < n; i++) cin >> stalls[i];
    
    sort(stalls.begin(), stalls.end());

    int low = 1; // minimum possible distance
    int high = stalls.back() - stalls.front(); // maximum possible distance
    int best = 0;

    while (low <= high){
        int mid = low + (high - low) / 2;
        if (can_place_cows(stalls, c, mid)){
            // mid works, increase lower bound
            best = mid;
            low = mid + 1;
        } else{
            // mid doesn't work, decrease upper bound
            high = mid - 1;
        }
    }

    cout << best << endl;
}