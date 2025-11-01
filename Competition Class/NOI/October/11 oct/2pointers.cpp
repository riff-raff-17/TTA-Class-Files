#include <iostream>
#include <vector>

using namespace std;

bool SubarrayWithSum(vector<int>& arr, int target){
    int left = 0;
    int right = 0;
    int current_sum = 0;

    for (; right < (arr.size()); right++){
        current_sum += arr[right]; // Expands the window

        // While sum is too big move left pointer
        while (current_sum > target && left <= right){
            current_sum -= arr[left];
            left++;
        }

        // Check if we found the target sum
        //Debugging
        if (current_sum == target){
            cout << "Subarray between indices " << left << ", " << right << endl;
            cout << "{";
            for (int i = left; i <= right; i++){
                cout << arr[i] << " ";
            }
            cout << "}" << endl;
        // Debugging
            return true;
        }
    }
    return false;
}

int main(){
    vector<int> arr = {1, 3, 4, 5, 1, 1, 2, 3};
    int target = 100;

    if (!SubarrayWithSum(arr, target)){
        cout << "No subarray found" << endl;
    }
}