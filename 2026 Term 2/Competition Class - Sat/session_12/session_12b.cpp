#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main(){
    vector<int> nums = {2, 5, 8, 12, 16, 23, 38, 45, 68, 91};
    sort(nums.begin(), nums.end());
    int target = 2;

    // lower_bound returns an iterator to the first element >= target
    auto it = lower_bound(nums.begin(), nums.end(), target);

    // Check that we didn't go past the end, and that the element is actually the target
    // (lower_bound only guarantees >= target, not == target!)
    if (it != nums.end() && *it == target){
        cout << "Found " << target << " at index " << (it - nums.begin()) << "\n";
    } else {
        cout << target << " not found\n";
    }
}