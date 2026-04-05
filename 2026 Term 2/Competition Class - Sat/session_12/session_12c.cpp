#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int findRotated(vector<int>& nums, int target){
    int lo = 0;
    int hi = nums.size() - 1;

    while (lo <= hi){
        int mid = lo + (hi - lo) / 2;

        if (nums[mid] == target) return mid;

        if (nums[lo] <= nums[mid]){
            // left half is sorted
            if (nums[lo] <= target && target < nums[mid]){
                hi = mid - 1; // target is in the sorted left half
            } else {
                lo = mid + 1; // target is in the sorted right half
            }
        } else {
            // right half
            if (nums[mid] < target && target <= nums[hi]){
                lo = mid + 1; // target is in the sorted right half
            } else {
                hi = mid -1; // target is in the left half
            }
        }
    }
    return -1;
}

int main(){
    vector<int> nums = {619, 724, 835, 946, 1050, 101, 204, 317, 408, 512};
    int target = 946;

    int result = findRotated(nums, target);
    if (result != -1){
        cout << "Found " << target << " at index " << result << "\n";
    } else{
        cout << target << " not found\n";
    }
}