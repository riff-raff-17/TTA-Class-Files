#include <iostream>
#include <vector>

using namespace std;

int main(){
    ios::sync_with_stdio(0);
    cin.tie(0);

    vector<int> nums(5, 10);

    cout << nums.front() << "\n"; // Get the first element
    cout << nums.back() << "\n"; // Get the last element

    nums.at(2) = 30;

    cout << nums.size() << "\n"; // number of elements in vector

    cout << nums.empty() << "\n"; // Empty: 1, Full: 0
    
    for (int num : nums){
        cout << num << " ";
    }
}