#include <iostream>
#include <vector>

using namespace std;

int main(){
    // n = number of cows which is the length of string
    int cow_num;
    cin >> cow_num;

    // Vector a = characters of cows (H or G)
    vector<char> a(cow_num);
    // for (int i=0; i < cow_num : i++) {cin >> a[i];}
    for (char &c : a) {cin >> c;}

    // Vector b
    vector<char> b(cow_num);
    for (char &c : b) {cin >> c;}

    // diff[i] is true if the cows differ at the ith position
    vector<bool>diff(cow_num + 1);
    for (int i = 0; i < cow_num; i++) {diff[i + 1] = a[i] != b[i];}

    int min_flips = 0;
    for (int i = 0; i < cow_num; i++){
        if (!diff[i] && diff[i + 1]) {min_flips++;}
    }

    cout << min_flips << endl;
}