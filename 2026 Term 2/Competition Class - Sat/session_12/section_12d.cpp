#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int atMost(vector<int>& bales, int target){
    int lo = 0;
    int hi = bales.size() - 1;
    int result = 0;

    while (lo <= hi){
        int mid = lo + (hi - lo) / 2;

        if (bales[mid] <= target){
            result = mid + 1;
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    return result;
}

int main(){
    int N, Q;
    cin >> N >> Q;

    vector<int> bales(N);
    for (int& b : bales) cin >> b;
    sort(bales.begin(), bales.end());

    for (int i = 0; i < Q; i++){
        int a, b;
        cin >> a >> b;
        cout << atMost(bales, b) - atMost(bales, a - 1) << "\n";
    }
}