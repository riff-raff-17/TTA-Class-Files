#include <iostream>
#include <vector>
// ALL binary search functions: binary_search, lower_bound, upper_bound, equal_range
#include <algorithm> 

using namespace std;

int main() {
    vector<int> v = {1, 2, 4, 4, 4, 5, 7, 9};

    int target = 4;

    if (binary_search(v.begin(), v.end(), target)){
        cout << target << " found with binary search" << endl;
    } else {
        cout << target << " not found" << endl;
    }

    auto lb = lower_bound(v.begin(), v.end(), target);
    cout << "lower bound is at index " << (lb - v.begin()) << endl;

    auto ub = upper_bound(v.begin(), v.end(), target);
    cout << "upper bound is at index " << (ub - v.begin()) << endl;

    // equal_range returns a PAIR of iterators: (lower bound, upper bound)
    auto range = equal_range(v.begin(), v.end(), target);
    cout << "spans indices [" << (range.first - v.begin()) << "," 
        << (range.second - v.begin())  << ")" << endl;
}