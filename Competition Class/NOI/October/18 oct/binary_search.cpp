#include <iostream>
using namespace std;

// Binary search function
int binary_search(int arr[], int size, int target){
    int left = 0;
    int right = size - 1;

    while (left <= right){
        int mid = left + (right - left) / 2; // Avoid overflow errors

        if (arr[mid] == target) 
            return mid; // Target found

        if (arr[mid] < target) 
            left = mid + 1;

        else
            right = mid - 1;
    }
    return -1; // Target not found
}

int main() {
    int arr[] = {2, 4, 6, 8, 10, 12, 14, 16, 18, 67};
    int size = sizeof(arr) / sizeof(arr[0]);
    int target1 = 12;
    int target2 = 3;

    int result = binary_search(arr, size, target1);

    if (result != -1)
        cout << "Element found at index " << result << endl;
    else
        cout << "Element not found" << endl;
    
}