#include <iostream>
#include <vector>

using namespace std;

int main(){
    vector<int> nums = {5, 2, 8, 12, 16, 23, 38, 45, 68, 91};
    sort(nums.begin(), nums.end());
    int target = 68;

    int lo = 0;
    int hi = nums.size() - 1; // both lo and hi are inclusive!

    while (lo <= hi){
        int mid = lo + (hi - lo) / 2;

        if (nums[mid] == target){
            cout << "Found " << target << " at index " << mid << "\n";
            break;
        } else if (nums[mid] < target){
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
}