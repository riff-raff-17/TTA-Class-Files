#include <array>
#include <chrono>
#include <iomanip>
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

struct MrvCell {
    int row;
    int col;
    int candidates;
};

std::optional<MrvCell> findMrvCell(const Board& board, const CandidateMasks& masks) {
    std::optional<MrvCell> best;
    int bestCount = 10;
    for (int row = 0; row < 9; row++) {
        for (int col = 0; col < 9; col++) {
            if (board.cells[row][col] != 0) continue;

            int candidates = masks.candidatesAt(row, col);
            int count = __builtin_popcount(candidates);
            if (count < bestCount) {
                best = MrvCell{row, col, candidates};
                bestCount = count;
                if (count <= 1) return best;
            }
        }
    }
    return best;
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

// 69175317 -> "69,175,317", so call counts that differ by orders of
// magnitude are readable.
std::string withThousandsSeparators(long long number) {
    std::string digits = std::to_string(number);
    std::string result;
    for (std::size_t i = 0; i < digits.size(); i++) {
        if (i != 0 && (digits.size() - i) % 3 == 0) result += ',';
        result += digits[i];
    }
    return result;
}

struct Puzzle {
    std::string name;
    std::string text;
};

struct PuzzleResult {
    std::string name;
    int clues = 0;
    SolveStats stats;
    double elapsedMs = 0;
    bool solved = false;
    bool verified = false;
};

PuzzleResult runPuzzle(const Puzzle& puzzle) {
    Board board = Board::fromString(puzzle.text);

    PuzzleResult result;
    result.name = puzzle.name;
    result.clues = countClues(board);

    std::cout << "=== " << puzzle.name << " (" << result.clues << " clues) ===\n";
    board.print();
    std::cout << '\n';

    auto start = std::chrono::steady_clock::now();
    result.solved = solve(board, result.stats);
    auto end = std::chrono::steady_clock::now();
    result.elapsedMs = std::chrono::duration<double, std::milli>(end - start).count();

    if (result.stats.gaveUp) {
        std::cout << "Gave up after " << withThousandsSeparators(result.stats.calls) << " calls )"
                    << result.elapsedMs << " ms).\n\n";
        return result;
    }
    if (!result.solved) {
        std::cout << "No solution found.\n\n";
        return result;
    }

    std::cout << "Solved in " << result.elapsedMs << " ms, " << withThousandsSeparators(result.stats.calls)
                << " calls:\n";
    board.print();

    result.verified = isSolvedBoard(board);
    std::cout << "Verification: " << (result.verified ? "PASS (valid completed Sudoku)" : "FAIL") << "\n\n";
    return result;
}

void printSummary(const std::vector<PuzzleResult>& results) {
    std::cout << "=== Summary ===\n";
    std::cout << std::left << std::setw(30) << "Puzzle" << std::right << std::setw(6) << "Clues"
                << std::setw(16) << "Calls" << std::setw(14) << "Time (ms)" << "  Result\n";
    
    for (const PuzzleResult& result : results) {
        std::string outcome;
        if (result.stats.gaveUp) {
            outcome = "GAVE UP";
        } else if (!result.solved) {
            outcome = "NO SOLUTION";
        } else {
            outcome = result.verified ? "PASS" : "FAIL";
        }

    std::cout << std::left << std::setw(30) << result.name << std::right << std::setw(6) << result.clues
                << std::setw(16) << withThousandsSeparators(result.stats.calls) << std::setw(14) 
                << std::fixed << std::setprecision(1) << result.elapsedMs << std::defaultfloat <<
                "  " << outcome << '\n';
    }
}

int main() {
    std::vector<Puzzle> puzzles = {
        {"Normal",
        "53......."
        "6..195..."
        ".98....6."
        "8.......3"
        "4....3..1"
        "7...2...6"
        ".6....2.."
        "...4.9..5"
        "....8..79"},
        {"AI Escargot",
        "1....7.9."
        ".3..2...8"
        "..96..5.."
        "..53..9.."
        ".1..8...2"
        "6....4..."
        "3......1."
        ".4......7"
        "..7...3.."},
        {"Inkala 2012",
        "8........"
        "..36....."
        ".7..9.2.."
        ".5...7..."
        "....457.."
        "...1...3."
        "..1....68"
        "..85...1."
        ".9....4.."},
        {"Anti-brute-force (Wikipedia)",
        "........."
        ".....3.85"
        "..1.2...."
        "...5.7..."
        "..4...1.."
        ".9......."
        "5......73"
        "..2.1...."
        "....4...9"},
    };

    std::vector<PuzzleResult> results;
    for (const Puzzle& puzzle : puzzles) {
        results.push_back(runPuzzle(puzzle));
    }
    printSummary(results);

    for (const PuzzleResult& result : results) {
        if (result.stats.gaveUp) continue;
        if (!result.solved || !result.verified) return 1;
    }
}
