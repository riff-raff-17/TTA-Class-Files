#include <iostream>
using namespace std;

int main() {
    // read in bronze before and after
    int bronze_b, bronze_a;
    cin >> bronze_b >> bronze_a;

    // read in silver before and after
    int silver_b, silver_a;
    cin >> silver_b >> silver_a;

    // read in gold before and after
    int gold_b, gold_a;
    cin >> gold_b >> gold_a;

    // read in platinum before and after
    int plat_b, plat_a;
    cin >> plat_b >> plat_a;

    // do the compuations
    int gold_to_plat = plat_a - plat_b;
    int silver_to_gold = gold_a - gold_b + gold_to_plat;
    int bronze_to_silver = silver_a - silver_b + silver_to_gold;

    cout << bronze_to_silver << endl << silver_to_gold 
    << endl << gold_to_plat << endl;
}