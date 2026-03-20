#include <iostream>
#include <vector>
#include <algorithm> // sorting
#include <numeric> // accumulate
#include <string>

using namespace std;

// Print a vector
template <typename T>
void print_vec(vector<T> v, string label=""){
    if (!label.empty()) cout << label << ": ";
    cout << "[ ";
    for (auto x : v) cout << x << " ";
    cout << "]" << endl;
}

void vector_basics(){
    vector<int> a; // empty vector
    vector<int> b = {13, 7, 8, 4}; // with values
    vector<int> c(5, 0); // {0, 0, 0, 0, 0}

    print_vec(a);
    print_vec(b);
    print_vec(c);

    // Get first element
    cout << "First element: " << b[0] << endl;
    cout << "Size: " << b.size() << endl;
    cout << "Empty? " << (b.empty() ? "yes" : "no") << endl;
}

void vector_modifying(){
    vector<int> v;

    v.push_back(10); // v = {10}
    v.push_back(20); // v = {10, 20}
    v.push_back(30); // v = {10, 20, 30}
    print_vec(v, "After push_back");

    v.pop_back(); // v = {10, 20}
    print_vec(v, "After pop_back");

    v.insert(v.begin() + 1, 99); // at index 1: v = {10, 99, 20}
    print_vec(v, "After insert");

    v.erase(v.begin()); // at index 0: v = {99, 20}
    print_vec(v, "After erase");
}

void vector_interation(){
    vector<int> v = {5, 10, 15};

    cout << "Index loop: ";
    for (size_t i = 0; i < v.size(); i++){
        cout << v[i] << " ";
    }
    cout << endl;

    cout << "Range loop: ";
    for (int x : v)
        cout << x << " ";
    cout << endl;
}

void vector_algorithms(){
    vector<int> v = {7, 3, 9, 1, 5};
    print_vec(v, "Original");

    sort(v.begin(), v.end());
    print_vec(v, "Sorted (low -> high)");

    reverse(v.begin(), v.end());
    print_vec(v, "Sorted (high -> low)");

    int sum = accumulate(v.begin(), v.end(), 0);
    cout << "Sum = " << sum << endl;
}

void vector_average(){
    int n;
    cout << "How many grades? ";
    cin >> n;

    vector<double> grades;
    grades.reserve(n); // reserves memory for the vector

    cout << "Enter " << n << " grades: ";
    for (int i = 0; i < n; i++){
        double g;
        cin >> g;
        grades.push_back(g);
    }
    print_vec(grades, "Grades");

    double sum = accumulate(grades.begin(), grades.end(), 0.0);
    double average = sum / grades.size();
    cout << "Average = " << average << endl;
}

int main(){
    vector_basics();
    vector_modifying();
    vector_interation();
    vector_algorithms();
    vector_average();
}