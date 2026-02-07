#include <iostream>
#include <vector>
#include <algorithm> // vector functions: sort, reverse, find, count, removing

using namespace std;

void printVector(const vector<int>& v, const string& label){
    cout << label << "(size=" << v.size() << ", capacity=" << v.capacity() << "): " ;
    for (int x : v) cout << x << " ";
    cout << endl;
}

// Adds a value to every element (pass by reference)
void addToAll (vector<int>& v, int add){
    for (int& x : v) x += add;
}

// Sums elements (pass by const reference)
int sumVector(const vector<int>& v){
    int total = 0;
    for (int x : v) total += x;
    return total;
}

int main(){
    cout << "--- 7) Remove all occurences of a value (erase-remove idiom) ---\n";
    vector<int> r = {1, 2, 2, 3, 2, 4};
    printVector(r, "r");

    // remove moves "kept" elements forward and returns new logical end
    r.erase(remove(r.begin(), r.end(), 2), r.end());
    printVector(r, "r after removing 2");

    cout << "--- 8) Searching and counting ---\n";
    vector<int> s = {5, 1, 5, 2, 5, 3, 2};
    printVector(s, "s");

    int target = 2;
    auto it = find(s.begin(), s.end(), target);
    
    if (it != s.end()){
        int index = (int)distance(s.begin(), it);
        cout << "Found " << target << " at index " << index << endl;
    } else {
        cout << target << " not found" << endl;
    }

    cout << "--- 9) Sorting and reversing ---\n";
    vector<int> t = {9, 3, 7, 1, 4};
    printVector(t, "t");

    sort(t.begin(), t.end()); // ascending
    printVector(t, "t after ascending");

    reverse(t.begin(), t.end()); // descending
    printVector(t, "t after reverse (descending)");

    cout << "--- 10) 2D vectors (matrix / grid) ---\n";
    int rows = 3, cols = 4;
    vector<vector<int>> grid(rows, vector<int>(cols, 0)); // 3x4 filled with 0s

    // Set a few values
    grid[0][1] = 5;
    grid[2][3] = 9;

    cout << "grid:\n";
    for (int r = 0; r < rows; r++){
        for (int c = 0; c < cols; c++){
            cout << grid[r][c] << " ";
        }
        cout << endl;
    }

    return 0;
}

