#include <iostream>
#include <vector>
#include <algorithm>
#include <string>

using namespace std;

template <typename A, typename B>
ostream& operator<<(ostream& os, const pair<A, B>& p){
    return os << '(' << p.first << ',' << p.second << ')';
}

template <typename T>
void printVector(const vector<T>& v){
    for (const T& x : v){
        cout << x << " ";
    }
    cout << endl;
}

bool comp(string a, string b){
    if (a.size() != b.size()) return a.size() < b.size();
    return a < b;
}

int main(){
    vector<int> v1 = {4,2,5,3,5,8,3};
    sort(v1.begin(), v1.end());
    // reverse(v1.begin(), v1.end());
    printVector(v1);

    string s = "an electron";
    sort(s.begin(), s.end());
    cout << s << endl;

    vector<pair<int, int>> v2;
    v2.push_back({1, 2});
    v2.push_back({6, 7});
    v2.push_back({12, 4});
    v2.push_back({7, 8});
    v2.push_back({7, 9});
    sort(v2.begin(), v2.end()); 

    printVector(v2);

    vector<string> v3 = {"banana", "apple", "pear", "kiwi", "grape", "cherry", "fig", "watermelon", "durian"};
    sort(v3.begin(), v3.end(), comp);
    printVector(v3);
}