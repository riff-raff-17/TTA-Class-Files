#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main(){
    vector<int> v = {10, 3, 27, 14, 9};

    int mx = *max_element(v.begin(), v.end());

    cout << mx;

    auto it = max_element(v.begin(), v.end());

    if (it != v.end()){
        int mx = *it;
        int idx = it - v.begin();
    }

    
}