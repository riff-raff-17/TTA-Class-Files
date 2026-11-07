#include <array>
#include <iostream>
#include <stdexcept>
#include <string>

struct Board {
    std::array<std::array<int, 9>, 9> cells{};

    // 81 characters. '.' or '0' means empty, '1'-'9' is a clue.
    // We fill in each row from a string, e.g. "800042915"
    static Board fromString(const std::string& text) {
        Board board;
        int index = 0;
        for (char ch : text) {
            if (ch == ' ' || ch == '\n' || ch == '\t') continue;
            if (index >= 81) throw std::invalid_argument("too many characters for a 9x9 board");

            int value;
            if (ch == '.' || ch == '0') { 
                value = 0;
            } else if (ch >= '1' && ch <= '9') {
                value = ch - '0';
            } else {
                throw std::invalid_argument("invalid character in board string: " + std::string(1, ch));
            }

            board.cells[index / 9][index % 9] = value;
            ++index;
        }
        if (index != 81) throw std::invalid_argument("not enough characters for a 9x9 board");
        return board;
    }

    void print(std::ostream& out = std::cout) const {
        for (int row = 0; row < 9; row++) {
            if (row != 0 && row % 3 == 0) out << "------+-------+------\n";
            for (int col = 0; col < 9; col++) {
                if (col != 0 && col % 3 == 0) out << "| ";
                int value = cells[row][col];
                out << (value == 0 ? '.' : static_cast<char>('0' + value)) << ' ';
            }
            out << '\n';
        }
    }
};

// True if 'value' could legally go at (row, col): not already present in
// that row, column, or 3x3 box. 
bool isValid(const Board& board, int row, int col, int value) {
    for (int i = 0; i < 9; i++){
        if (i != col && board.cells[row][i] == value) return false;
        if (i != row && board.cells[i][col] == value) return false;
    }

    int boxRow = (row / 3) * 3;
    int boxCol = (col / 3) * 3;
    for (int r = boxRow; r < boxRow + 3; r++) {
        for (int c = boxCol; c < boxCol + 3; c++) {
            if ((r != row || c != col) && board.cells[r][c] == value) return false;
        }
    }
    return true;
}

struct Check {
    int row, col, value;
    bool expectedValid;
    const char* reason;
};

int main() {
    Board board = Board::fromString(
        "2.34....5"
        "8.916.7.4"
        "..6.3..19"
        "7.2..3.6."
        "..825...."
        "..16.7..2"
        "..7..5926"
        "93.72...."
        "6...9.47."
    );
    board.print();
    std::cout << '\n';

    const Check checks[] = {
        {0, 6, 2, false, "2 in the same row"},
        {0, 1, 1, true, "No 1 in row 0, column 1, or in the top left box"},
        {4, 6, 6, false, "6 in the same box"}
    };

    bool allPassed = true;

    for (const Check& check : checks) {
        bool actual = isValid(board, check.row, check.col, check.value);
        bool pass = actual == check.expectedValid;
        allPassed &= pass;
        std::cout << (pass ? "PASS" : "FAIL") << "  (" << check.row << ',' << check.col
                  << ")=" << check.value << "  expected " << (check.expectedValid ? "valid" : "invalid")
                  << ", got " << (actual ? "valid" : "invalid") << "  -- " << check.reason << '\n';
    }

    return allPassed ? 0 : 1;
}
