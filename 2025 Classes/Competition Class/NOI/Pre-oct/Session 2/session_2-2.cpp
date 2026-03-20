#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main(){
    vector<int> v{3, 1, 4, 1, 5};

    int ones = count(v.begin(), v.end(), 1); // count elements in a vector

    // Sorting and rearranging
    sort(v.begin(), v.end()); // 1 1 3 4 5
    sort(v.begin(), v.end(), greater<int>()); // 5 4 3 1 1

    vector<int> v{3, 1, 4, 1, 5};
    reverse(v.begin(), v.end()); // 5 1 4 1 3

    vector<int> v{3, 3, 1, 1, 1, 2, 2, 5};
    auto last = unique(v.begin(), v.end()); // 3 1 2 5 ?
    v.erase(last, v.end());                 // 3 1 2 5

    int mn = *min_element(v.begin(), v.end());
    int mx = *max_element(v.begin(), v.end());

    auto it = find(v.begin(), v.end(), 3);

    if (it != v.end()){
        int index = distance(v.begin(), it);
        cout << "found it at " << index << "\n";
    } else {
        cout << "didn't find it\n";
    }
}