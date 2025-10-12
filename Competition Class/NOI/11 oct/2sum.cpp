#include <iostream>
#include <vector>
#include <utility>

using namespace std;

pair<int, int> twosum(vector<int>& arr, int target){
    int left = 0;
    int right = (arr.size()) - 1;

    sort(arr.begin(), arr.end());

    while (left < right){
        int sum = arr[left] + arr[right];

        if (sum == target){
            return {left, right}; // found it
        }

        else if (sum < target){
            left++; // increase the sum
        }

        else {
            right--; // decrease the sum
        }
    }
    return {-1, -1};
}

int main(){
    vector<int> arr = {2, 7, 11, 15};
    int target = 9;

    auto result = twosum(arr, target);
    if (result.first == -1){
        cout << "No pair found" << endl;
    } else{
        cout << "Indices: " << result.first << ", " << result.second << endl;
    }
}