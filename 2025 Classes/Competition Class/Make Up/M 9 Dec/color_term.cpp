#include <iostream>
using namespace std;

int main() {
    cout << "\033[32mThis is green text!\033[0m" << endl;
    cout << "\033[33mThis is yellow text!\033[0m" << endl;
    cout << "\033[31mThis is red text!\033[0m" << endl;

    cout << "\033[1m\033[34mThis is bold blue text!\033[0m" << endl;

    return 0;
}