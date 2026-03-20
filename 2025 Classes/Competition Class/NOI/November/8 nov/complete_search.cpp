#include <iostream>
#include <vector>
#include <algorithm>
#include <string>

using namespace std;

// Example 1: Generate all subsets
void subsets() {
    vector<int> elements = {2, 6, 10, 10};
    int n = elements.size();
    vector<int> subset;

    function<void(int)> search = [&](int k){
        if (k == n){
            cout << "{";
            for (int x : subset) cout << x << " ";
            cout << "}" << endl;
        } else {
            // Exclude this element
            search(k + 1);

            // Include this element
            subset.push_back(elements[k]);
            search(k + 1);
            subset.pop_back(); // backtrack
        }
    };
    search(0);
}

void permutations_rec(){
    string s;
    cout << "Enter a string: ";
    cin >> s;

    int char_count[26] = {0};
    for (char c : s) ++char_count[c - 'a'];

    vector<string> perms;

    function<void(string)> search = [&](string curr){
        if (curr.size() == s.size()){
            perms.push_back(curr);
            return;
        }
        for (int i = 0; i < 26; i++){
            if (char_count[i]){
                --char_count[i];
                search(curr + char('a' + i));
                ++char_count[i];
            }
        }
    };
    search("");
    cout << perms.size() << " permutations:\n";
    for (auto& p : perms) cout << p << "\n";
}

void permutations_stl(){
    string s;
    cout << "Enter a string: ";
    cin >> s;

    sort(s.begin(), s.end());
    vector<string> perms;
    do perms.push_back(s);
    while (next_permutation(s.begin(), s.end()));

    cout << perms.size() << " Permutations:\n";
    for (auto& p : perms) cout << p << '\n';
}

int main() {
    cout << "Choose:\n"
        << "1. Subsets\n"
        << "2. Recursive permutations\n"
        << "3. STL permutations\n";

    int choice;
    cin >> choice;

    switch (choice){
        case 1: subsets(); break;
        case 2: permutations_rec(); break;
        case 3: permutations_stl(); break;
        default: cout << "Invalid choice" << endl; break;
    }
}