#include <array>
#include <cctype>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace wordle
{

    // A single tile's result. Gray = letter not in word, Yellow = in word but
    // wrong spot, Green = correct letter in the correct spot.
    enum class Color
    {
        Gray,
        Yellow,
        Green
    };
    using Feedback = std::array<Color, 5>;

    // Computes the feedback pattern Wordle would show for `guess` if the
    // secret word were `answer`. Handles duplicate letters the way the real
    // game does: greens are claimed first, then yellows use what's left.
    Feedback computeFeedback(const std::string &guess, const std::string &answer)
    {
        Feedback result{};
        result.fill(Color::Gray);

        std::array<bool, 5> answerLetterUsed{};
        answerLetterUsed.fill(false);

        // Pass 1: exact position matches (greens) claim their letter first.
        for (int i = 0; i < 5; i++)
        {
            if (guess[i] == answer[i])
            {
                result[i] = Color::Green;
                answerLetterUsed[i] = true;
            }
        }

        // Pass 2: remaining letters get yellow if unclaimed in the answer.
        for (int i = 0; i < 5; i++)
        {
            if (result[i] == Color::Green)
                continue;
            for (int j = 0; j < 5; j++)
            {
                if (!answerLetterUsed[j] && guess[i] == answer[j])
                {
                    result[i] = Color::Yellow;
                    answerLetterUsed[j] = true;
                    break;
                }
            }
        }

        return result;
    }

    bool isConsistent(const std::string &candidate, const std::string &guess,
                    const Feedback &feedback)
    {
        return computeFeedback(guess, candidate) == feedback;
    }

    // Returns the subset of `candidates` still consistent with a guess/feedback pair.
    std::vector<std::string> filterCandidates(const std::vector<std::string> &candidates,
                                            const std::string &guess,
                                            const Feedback &feedback)
    {
        std::vector<std::string> result;
        result.reserve(candidates.size());
        for (const auto &word : candidates)
        {
            if (isConsistent(word, guess, feedback))
            {
                result.push_back(word);
            }
        }
        return result;
    }

    // Reads one word per line from 'path', keeping only clean 5-letter
    // entries (lowercased, trailing whitespace stripped).
    std::vector<std::string> loadWords(const std::string &path)
    {
        std::vector<std::string> words;
        std::ifstream in(path);
        std::string line;
        while (std::getline(in, line))
        {
            while (!line.empty() && !std::isalpha(static_cast<unsigned char>(line.back())))
            {
                line.pop_back();
            }
            if (line.size() == 5)
            {
                std::transform(line.begin(), line.end(), line.begin(), ::tolower);
                words.push_back(line);
            }
        }
        return words;
    }

    // Picks the best next guess using letter-position frequency scoring.
    std::string bestGuess(const std::vector<std::string> &candidates)
    {
        if (candidates.empty())
            return "";
        
        std::array<std::array<int, 26>, 5> freq{};
        for (const auto &word : candidates)
        {
            for (int i = 0; i < 5; i++)
            {
                freq[i][word[i] - 'a']++;
            }
        }

        auto scoreWord = [&](const std::string &word)
        {
            double score = 0.0;
            std::array<bool, 26> seenLetter{};
            for (int i = 0; i < 5; i++)
            {
                int letter = word[i] - 'a';
                score += freq[i][letter];
                if (seenLetter[letter])
                    score *= 0.5; // repeats add less info
                seenLetter[letter] = true;
            }
            return score;
        };

        std::string best = candidates[0];
        double bestScore = -1.0;
        for (const auto &word : candidates)
        {
            double s = scoreWord(word);
            if (s > bestScore)
            {
                bestScore = s;
                best = word;
            }
        }
        return best;
    }

} // namespace wordle

namespace
{

    wordle::Feedback parseFeedback(const std::string &input)
    {
        wordle::Feedback fb{};
        for (int i = 0; i < 5; i++)
        {
            switch (std::tolower(static_cast<unsigned char>(input[i])))
            {
                case 'g':
                    fb[i] = wordle::Color::Green;
                    break;
                case 'y':
                    fb[i] = wordle::Color::Yellow;
                    break;
                default:
                    fb[i] = wordle::Color::Gray;
                    break;
            }
        }
        return fb;
    }

    std::string feedbackToString(const wordle::Feedback &fb)
    {
        std::string s;
        for (auto c : fb)
        {
            s += (c == wordle::Color::Green) ? 'G' : (c == wordle::Color::Yellow) ? 'Y'
                                                                                : 'B';
        }
        return s;
    }

    void check(const std::string &guess, const std::string &answer, const std::string &expected)
    {
        std::string actual = feedbackToString(wordle::computeFeedback(guess, answer));
        bool pass = (actual == expected);
        std::cout << (pass ? "PASS   " : "FAIL   ")
                    << guess << " vs " << answer
                    << "  expected " << expected << "  got " << actual << std::endl;
    }

    void printWords(const std::vector<std::string> &words)
    {
        for (const auto &w : words)
        std::cout << "  " << w << std::endl;
    }
    
} // namespace

int main() 
{ 
    std::cout << "Loading words.txt... \n\n";

    auto words = wordle::loadWords("words.txt");
    if (words.empty())
    {
        std::cerr << "Could not load words.txt. Make sure it's in this directory,\n"
                        "one 5-letter word per line.\n";
        return 1;
    }
    std::cout << "Loaded " << words.size() << " words from words.txt\n\n";

    std::vector<std::string> candidates = words;

    std::cout << "=== Wordle Solver ===\n";
    std::cout << "Play Wordle! After each guess write what you guessed\n";
    std::cout << "and the feedback colors (G=green, Y=yellow, B=gray).\n";
    std::cout << "Example: guessed 'crane', got gray/gray/green/yellow/gray -> type BBGYB\n\n";

    std::cout << "Suggested first guess: " << wordle::bestGuess(candidates) << "\n\n";

    while (candidates.size() > 1)
    {
        std::string guess, feedbackStr;

        std::cout << "Word you guessed: ";
        if (!(std::cin >> guess))
            break;
        std::cout << "Feedback (5 letters G/Y/B): ";
        if (!(std::cin >> feedbackStr))
            break;

        std::transform(guess.begin(), guess.end(), guess.begin(), ::tolower);
        if (guess.size() != 5 || feedbackStr.size() != 5)
        {
            std::cout << "Please enter exactly 5 characters for both.\n\n";
            continue;
        }

        wordle::Feedback fb = parseFeedback(feedbackStr);
        candidates = wordle::filterCandidates(candidates, guess, fb);

        std::cout << candidates.size() << " word(s) still possible.\n";
        if (candidates.size() <= 10 && !candidates.empty())
        {
            std::cout << "  ";
            for (const auto &w : candidates)
                std::cout << w << " ";
            std::cout << "\n";
        }

        if (candidates.empty())
        {
            std::cout << "No candidates left. The answer might not be in words.txt.\n";
            break;
        }
        if (candidates.size() > 1)
        {
            std::cout << "Suggested next guess: " << wordle::bestGuess(candidates) << "\n\n";
        }
    }

    if (candidates.size() == 1)
    {
        std::cout << "Solved! The word is: " << candidates.front() << "\n";
    }
}
