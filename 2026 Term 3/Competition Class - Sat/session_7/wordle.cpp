#include <array>
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

} // namespace wordle

// Test it out

namespace
{

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
    std::cout << "---Feedback---" << std::endl;

    // Examples
    check("crane", "grape", "BGGBG");
    check("sassy", "abyss", "YYBGY");
    check("world", "world", "GGGGG");
    check("chimp", "world", "BBBBB");
    check("robot", "moose", "BGBYB");
    check("silks", "songs", "GBBBG");
}