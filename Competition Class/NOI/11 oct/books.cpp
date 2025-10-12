#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main(){
    // Read number of elements (n) and max time (t)
    int n;
    int t;
    cin >> n >> t;

    // Read array of n elements
    vector<int> arr(n);
    for (auto &a: arr) cin >> a;

    // two pointers
    int r = -1; // right pointer
    int sum = 0; // current sum of the window
    int ans = 0; //max len of subarrays

    // move the left pointer first, then subtract the left value
    for (int l = 0; l < n; sum -= arr[l++]){
        // Expand right pointer as much as possible
        while (r + 1 < n && sum + arr[r + 1] <= t){
            r++; // move right pointer one step
            sum += arr[r]; // add element to sum
        }
        ans = max(ans, r - l + 1);
    }
    cout << ans << endl;
}