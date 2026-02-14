#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

int main{
    int n;
    cin >> n;

    vector<int> x(n), y(n);

    for (int i = 0; i < n; i++){
        cin >> x[i];
    }
    for (int i = 0; i < n; i++){
        cin >> y[i];
    }

    int max_squared = 0;
    for (int i = 0; i < n; i++){
        for (int j = i + 1; j < n; j++){
            int a = x[i] - x[j];
            int b = y[i] - y[j];
            int square = a * a + b * b;

            max_squared = max(square, max_squared);
        }
    }

    cout << max_squared << endl;
}