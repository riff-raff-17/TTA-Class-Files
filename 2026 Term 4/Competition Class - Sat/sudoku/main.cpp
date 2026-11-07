#include <array>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>

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

std::optional<std::pair<int, int>> findEmptyCell(const Board& board) {
    for (int row = 0; row < 9; row++) {
        for (int col = 0; col < 9; col++) {
            if (board.cells[row][col] == 0) return std::make_pair(row, col);
        }
    }
    return std::nullopt;
}

struct SolveStats {
    long long calls = 0;
    long long callLimit = 1'000'000'000;
    bool gaveUp = false;
};

bool solve(Board& board, SolveStats& stats) {
    if (stats.calls >= stats.callLimit) {
        stats.gaveUp = true;
        return false;
    }
    ++stats.calls;

    std::optional<std::pair<int, int>> empty = findEmptyCell(board);
    if (!empty) return true;  // no empty cells left: solved

    auto [row, col] = *empty;
    for (int value = 1; value <= 9; value++) {
        if (!isValid(board, row, col, value)) continue;

        board.cells[row][col] = value;
        if (solve(board, stats)) return true;
        board.cells[row][col] = 0;  // backtrack
        if (stats.gaveUp) return false;
    }
    return false;
}

bool isSolvedBoard(const Board& board) {
    for (int row = 0; row < 9; row ++) {
        for (int col = 0; col < 9; col++) {
            int value = board.cells[row][col];
            if (value == 0) return false;
            if (!isValid(board, row, col, value)) return false;
        }
    }
    return true;
}

int countClues(const Board& board) {
    int clues = 0;
    for (const auto& row : board.cells) {
        for (int value : row) {
            if (value != 0) clues++;
        }
    }
    return clues;
}

int main() {
    Board board = Board::fromString(
        "53......."
        "6..195..."
        ".98....6."
        "8.......3"
        "4....3..1"
        "7...2...6"
        ".6....2.."
        "...4.9..5"
        "....8..79"
    );

    std::cout << "Puzzle:\n";
    board.print();
    std::cout << '\n';

    auto start = std::chrono::steady_clock::now();
    bool solved = solve(board);
    auto end = std::chrono::steady_clock::now();
    double elapsedMs = std::chrono::duration<double, std::milli>(end - start).count();

    if (!solved) {
        std::cout << "No solution found.\n";
        return 1;
    }

    std::cout << "Solved in " << elapsedMs << " ms:\n";
    board.print();
    std::cout << '\n';

    bool verified = isSolvedBoard(board);
    std::cout << "Verification: " << (verified ? "PASS (valid completed Sudoku)" : "FAIL") << '\n';

    return verified ? 0 : 1;
}
