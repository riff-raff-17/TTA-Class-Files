#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;

    vector<long long> days(n);
    // for (int i = 0; i < n; i++){cin >> days[i]}
    for (long long &d : days){cin >> d;}

    long long last_day = days[0];
    long long cost = k + 1; // Starting subscription
    for (long long d : days){
        // Should I continue my subscription, or cancel and restart on the next day?

        // Continuous
        if (d - last_day < k + 1){
            cost += d - last_day;
        } else{
            // Start a new one
            cost += k + 1;
        }

        // Store the date of the last subscription
        last_day = d;

    }
    cout << cost << endl;
}