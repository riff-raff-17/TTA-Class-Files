#include <iostream> // input/output stream
#include <vector>
using namespace std;

int main(){
    ios::sync_with_stdio(0);
    cin.tie(0);

    vector<int> nums; 
    vector<int> nums(3); // [0, 0, 0]
    vector<int> nums(3, 100); // [100, 100, 100]

    nums.push_back(20); // [100, 100, 100, 20]
    nums.push_back(30); // [100, 100, 100, 20, 30]

    vector<int> nums;
    nums.push_back(20);
    nums.push_back(30); 

    cout << nums[2];
    cout << nums.at(2);

    vector<int> v1 = {1, 2, 3, 4, 5};

    for (int i : v1){
        cout << i << " ";
    }

    for (int i = 0; i < v1.size(); i++){
        cout << "Index: " 
        << i 
        << "Value: " 
        << v1[i]
        << " ";
    }

    v1.pop_back();
}