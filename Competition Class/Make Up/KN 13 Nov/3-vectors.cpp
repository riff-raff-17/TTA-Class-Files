#include <iostream>
#include <vector>
using namespace std;

int main(){
    vector<int> v; // v = {}
    v.push_back(3); // v = {3}
    v.push_back(2); // v = {3, 2}
    v.push_back(5); // v = {3, 2, 5}
    v.pop_back(); // v = {3, 2}
    
    cout << v.at(4); // safe
    cout << v[4]; // unsafe (but fast)
}