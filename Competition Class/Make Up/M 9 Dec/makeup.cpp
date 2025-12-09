#include <iostream>
#include <string>
#include <vector>
#include <cctype>

using namespace std;

int WORD_LENGTH = 5;
int MAX_TRIES = 6;

// Returns a string of length with:
// 'G' = correct letter and position
// 'Y' = letter exisits but wrong position
// '_' = letter not in word
string checkGuess(const string &secret, const string &guess){
    string result(WORD_LENGTH, '_'); // result = _ _ _ _ _ _
    vector<int> usedSecret(WORD_LENGTH, 0);
    vector<int> usedGuess(WORD_LENGTH, 0);

    // First pass: exact matches (greens)
    for (int i = 0; i < WORD_LENGTH; i++){
        if (guess[i] == secret[i]){
            result[i] = 'G';
            usedSecret[i] = 1;
            usedGuess[i] = 1;
        }
    }

    // Second pass: letters in word but in wrong position (yellows)
    for (int i = 0; i < WORD_LENGTH; i++){
        if (usedGuess[i]) continue; // already matched as green

        for (int j = 0; j < WORD_LENGTH; j++){
            if (!usedSecret[j] && guess[i] == secret[j]){
                result[i] = 'Y';
                usedSecret[j] = 1;
                usedGuess[i] = 1;
                break;
            }
        }
    }

    return result;
}

// Print a single colored tile like Wordle
void printColoredTile(char letter, char resultCode){
    letter = static_cast<char>(toupper(static_cast<unsigned char>(letter)));

    if (resultCode == 'G'){
        // Green background, black text
        cout << "\033[42m\033[30m " << letter << " \033[0m";
    } else if (resultCode == 'Y'){
        // Yellow background, black text
        cout << "\033[43m\033[30m " << letter << " \033[0m";
    } else {
        // Gray background, black text
        cout << "\033[47m\033[30m " << letter << " \033[0m";
    }
}

// Show which letters are known green or yellow
void printKnownLetters(const bool green[26], const bool yellow[26]){
    string greenLetters;
    string yellowLetters;

    for (int i = 0; i < 26; i++){
        char c = 'a' + i;
        if (green[i]) {
            greenLetters += c;
            greenLetters += ' ';
        }
        if (yellow[i]){
            yellowLetters += c;
            yellowLetters += ' ';
        }
    }

    cout << "Known green letters: ";
    if (greenLetters.empty()) cout << "(none)";
    else cout << greenLetters;
    cout << endl;

    cout << "Known yellow letters: ";
    if (yellowLetters.empty()) cout << "(none)";
    else cout << yellowLetters;
    cout << endl;
}

int main() {
    string secret = "apple";

    // Track which letters are known green or yellow
    bool green[26] = {false};
    bool yellow[26] = {false};

    cout << "===== WORDLE (C++ Version) =====\n";
    cout << "Guess the " << WORD_LENGTH << "-letter word in " << MAX_TRIES << " tries!\n";
    cout << "Feedback uses colors like Wordle:" << endl;
    cout << " Green = correct letter & position" << endl;
    cout << " Yellow = in word, wrong position" << endl;
    cout << " Gray = not in word" << endl << endl;

    for (int attempt = 1; attempt <= MAX_TRIES; ++attempt){
        string guess;
        cout << "Try " << attempt << "/" << MAX_TRIES
            << " - Enter a " << WORD_LENGTH << "-letter word: ";
        cin >> guess;

        // basic validation
        if ((int)guess.size() != WORD_LENGTH){
            cout << "Please enter exactly " << WORD_LENGTH << " letters." << "\n\n";
            --attempt; // don't count this as a used try
            continue;
        }

        // convert guess to lowercase
        for (char &c : guess){
            c = static_cast<char>(tolower(static_cast<unsigned char>(c)));
        }
        
        cout << "You entered: " << guess << "\n";

        string feedback = checkGuess(secret, guess);

        cout << "Feedback: ";

        // Print colored tiles
        for (int i = 0; i < WORD_LENGTH; i++){
            printColoredTile(guess[i], feedback[i]);
        }
        cout << endl;

        // Update known green/yellow letters
        for (int i = 0; i < WORD_LENGTH; i++){
            char ch = guess[i];
            if (ch < 'a' || ch > 'z') continue;
            int idx = ch - 'a';

            if (feedback[i] == 'G'){
                green[idx] = true; // green overrides yellow
                yellow[idx] = false;
            } else if (feedback[i] == 'Y'){
                if (!green[idx]) {
                    yellow[idx] = true;
                }
            }
        }
        // Show what letters we have that are green or yellow
        printKnownLetters(green, yellow);
        if (guess == secret){
            cout << "You got it in " << attempt << " tries!" << endl;
        }
    }
    cout << "Out of tries! The word was: " << secret << endl;
}