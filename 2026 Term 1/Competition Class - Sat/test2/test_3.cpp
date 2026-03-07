#include <iostream>
using namespace std;

int main() {
	// read in counts for bronze
	int bronzeBefore, bronzeAfter;
	cin >> bronzeBefore >> bronzeAfter;

	// read in counts for silver
	int silverBefore, silverAfter;
	cin >> silverBefore >> silverAfter;

	// read in counts for gold
	int goldBefore, goldAfter;
	cin >> goldBefore >> goldAfter;

	// read in counts for platinum
	int platinumBefore, platinumAfter;
	cin >> platinumBefore >> platinumAfter;

	// do the computations
	int goldToPlatinum = platinumAfter - platinumBefore;
	int silverToGold = goldAfter - goldBefore + goldToPlatinum;
	int bronzeToSilver = silverAfter - silverBefore + silverToGold;

	// print the answers
	cout << bronzeToSilver << "\n" << silverToGold << "\n" << goldToPlatinum;

	return 0;
}