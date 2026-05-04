#include <SFML/Graphics.hpp>
#include <deque>
#include <cstdlib>
#include <string>

// --- Constants ---
const int WIDTH = 800, HEIGHT = 600;

// -----------------------------------------------------------------------
// Config - replaces the old compile-time constants CELL/MOVE_INTERVAL
// -----------------------------------------------------------------------
struct Config
{
    int cell = 20;
    float moveInterval = 0.06f;
    bool wrapWalls = false;
    // Snake color: r/g/b channels for the head (tail fades toward darker)
    uint8_t r = 50, g = 200, b = 50;
};

// -----------------------------------------------------------------------
// Game state machine
// -----------------------------------------------------------------------
enum class GameState
{
    Menu,
    Playing,
    GameOver
};

// --- Helper Functions ---
sf::Vector2i randomFood(const std::deque<sf::Vector2i> &snake, const Config &cfg)
{
    int cols = WIDTH / cfg.cell, rows = HEIGHT / cfg.cell;
    sf::Vector2i pos;
    do
    {
        pos = {std::rand() % cols, std::rand() % rows};
    } while ([&]
             { for (auto& s : snake) if (s == pos) return true; return false; }());
    return pos;
}

// -----------------------------------------------------------------------
// Simple button helper
// -----------------------------------------------------------------------
struct Button
{
    sf::RectangleShape box;
    sf::Text label;

    Button(const sf::Font &font, const std::string &text,
            sf::Vector2f pos, sf::Vector2f size, unsigned charSize = 22)
        : label(font)
    {
        box.setSize(size);
        box.setPosition(pos);
        box.setFillColor(sf::Color(60, 60, 60));
        box.setOutlineThickness(2.f);
        box.setOutlineColor(sf::Color(100, 100, 100));
        
        label.setString(text);
        label.setCharacterSize(charSize);
        // Center text inside the box
        auto b = label.getLocalBounds();
        label.setPosition({pos.x + size.x / 2.f - b.size.x / 2.f,
                            pos.y + size.y / 2.f - b.size.y / 2.f - 2.f});
    }

    // Highlight when selected
    void setSelected(bool selected)
    {
        box.setFillColor(selected ? sf::Color(80, 130, 80) : sf::Color(60, 60, 60));
        box.setOutlineColor(selected ? sf::Color::Green : sf::Color(100, 100, 100));
    }

    // Hover effect
    void setHovered(bool hovered)
    {
        if (hovered) box.setOutlineColor(sf::Color::White);
    }

    bool contains(sf::Vector2f point) const
    {
        return box.getGlobalBounds().contains(point);
    }

    void draw(sf::RenderWindow &window) const
    {
        window.draw(box);
        window.draw(label);
    }
};

// --- Main Loop ---
int main()
{
    std::srand(static_cast<unsigned>(std::time(nullptr))); // seed RNG
    // std::srand(1); // set seed

    sf::RenderWindow window(sf::VideoMode({WIDTH, HEIGHT}), "Snake");
    window.setFramerateLimit(60);

    // --- Font & Text ---
    sf::Font font;
    if (!font.openFromFile("FiraCodeNerdFont-Regular.ttf"))
        return -1;

    // -----------------------------------------------------------------------------------------
    // Menu buttons
    // Each row has mutually exclusive options; clicking one selects it and deselects the other.
    // -----------------------------------------------------------------------------------------
    // Speed row
    std::vector<Button> speedBtns = {
        Button(font, "Slow", {160.f, 160.f}, {120.f, 44.f}),
        Button(font, "Normal", {300.f, 160.f}, {120.f, 44.f}),
        Button(font, "Fast", {440.f, 160.f}, {120.f, 44.f}),
    };
    int speedSel = 1; // default: Normal

    // Grid size row
    std::vector<Button> gridBtns = {
        Button(font, "Small", {160.f, 260.f}, {120.f, 44.f}),
        Button(font, "Medium", {300.f, 260.f}, {120.f, 44.f}),
        Button(font, "Large", {440.f, 260.f}, {120.f, 44.f}),
    };
    int gridSel = 1; // default: Medium

    // Color row
    std::vector<Button> colorBtns = {
        Button(font, "Green", {160.f, 360.f}, {120.f, 44.f}),
        Button(font, "Blue", {300.f, 360.f}, {120.f, 44.f}),
        Button(font, "Fire", {440.f, 360.f}, {120.f, 44.f}),
    };
    int colorSel = 0; // default: Green

    // Wall mode row
    std::vector<Button> wallBtns = {
        Button(font, "Hard", {160.f, 460.f}, {120.f, 44.f}),
        Button(font, "Wrap", {300.f, 460.f}, {120.f, 44.f}),
    };
    int wallSel = 0; // default: Hard

    // Play button
    Button playBtn(font, "PLAY", {330.f, 530.f}, {140.f, 50.f}, 28);

    // Menu labels
    auto makeLabel = [&](const std::string &text, float y) 
    {
        sf::Text t(font);
        t.setString(text);
        t.setCharacterSize(20);
        t.setFillColor(sf::Color(180, 180, 180));
        t.setPosition({60.f, y + 12.f});
        return t;
    };
    sf::Text titleText(font);
    titleText.setString("SNAKE");
    titleText.setCharacterSize(56);
    titleText.setFillColor(sf::Color::Green);
    {
        auto b = titleText.getLocalBounds();
        titleText.setPosition({WIDTH / 2.f - b.size.x / 2.f, 60.f});
    };

    auto labelSpeed = makeLabel("Speed", 160.f);
    auto labelGrid = makeLabel("Grid", 260.f);
    auto labelColor = makeLabel("Color", 360.f);
    auto labelWalls = makeLabel("Walls", 460.f);

    // Game variables
    Config cfg;
    GameState state = GameState::Menu;

    std::deque<sf::Vector2i> snake;
    sf::Vector2i dir(1, 0), nextDir(1, 0);
    sf::Vector2i food;
    int score = 0;
    float timer = 0.f;
    sf::Clock clock;

    sf::Text scoreText(font);
    scoreText.setCharacterSize(24);
    scoreText.setFillColor(sf::Color::White);
    scoreText.setPosition({10.f, 10.f});

    sf::Text msgText(font);
    msgText.setCharacterSize(36);
    msgText.setFillColor(sf::Color::Yellow);

    // --- Snake ---
    std::deque<sf::Vector2i> snake;
    snake.push_back({WIDTH / CELL / 2, HEIGHT / CELL / 2});     // head
    snake.push_back({WIDTH / CELL / 2 - 1, HEIGHT / CELL / 2}); // body
    snake.push_back({WIDTH / CELL / 2 - 2, HEIGHT / CELL / 2}); // tail

    sf::Vector2i direction(1, 0); // moving right
    sf::Vector2i nextDir(1, 0);   // direction queued from input

    // --- Food ---
    sf::Vector2i food = randomFood(snake);

    // --- State ---
    int score = 0;
    bool gameOver = false;
    float timer = 0.f;
    sf::Clock clock;

    auto resetGame = [&]()
    {
        snake.clear();
        snake.push_back({WIDTH / CELL / 2, HEIGHT / CELL / 2});     // head
        snake.push_back({WIDTH / CELL / 2 - 1, HEIGHT / CELL / 2}); // body
        snake.push_back({WIDTH / CELL / 2 - 2, HEIGHT / CELL / 2}); // tail
        direction = nextDir = {1, 0};
        food = randomFood(snake);
        score = 0;
        gameOver = false;
        timer = 0.f;
    };

    // --- Reusable rectangle for drawing cells ---
    sf::RectangleShape cell(sf::Vector2f(CELL - 2.f, CELL - 2.f)); // 1px gap on each side

    while (window.isOpen())
    {
        float dt = clock.restart().asSeconds();

        // --- Events ---
        while (const std::optional event = window.pollEvent())
        {
            if (event->is<sf::Event::Closed>())
                window.close();

            if (const auto *key = event->getIf<sf::Event::KeyPressed>())
            {
                if (key->code == sf::Keyboard::Key::W && direction.y == 0)
                    nextDir = {0, -1};
                if (key->code == sf::Keyboard::Key::S && direction.y == 0)
                    nextDir = {0, 1};
                if (key->code == sf::Keyboard::Key::A && direction.x == 0)
                    nextDir = {-1, 0};
                if (key->code == sf::Keyboard::Key::D && direction.x == 0)
                    nextDir = {1, 0};
                if (key->code == sf::Keyboard::Key::Up && direction.y == 0)
                    nextDir = {0, -1};
                if (key->code == sf::Keyboard::Key::Down && direction.y == 0)
                    nextDir = {0, 1};
                if (key->code == sf::Keyboard::Key::Left && direction.x == 0)
                    nextDir = {-1, 0};
                if (key->code == sf::Keyboard::Key::Right && direction.x == 0)
                    nextDir = {1, 0};

                if (key->code == sf::Keyboard::Key::R && gameOver)
                    resetGame();
            }
        }

        // --- Update ---
        if (!gameOver)
        {
            timer += dt;
            if (timer >= MOVE_INTERVAL)
            {
                timer = 0.f;
                direction = nextDir; // commit the queued direction only on each step

                sf::Vector2i head = snake.front() + direction;

                // Wall collision
                if (head.x < 0 || head.x >= WIDTH / CELL ||
                    head.y < 0 || head.y >= HEIGHT / CELL)
                    gameOver = true;

                // Self collision
                for (auto &s : snake)
                    if (s == head)
                    {
                        gameOver = true;
                        break;
                    }

                if (!gameOver)
                {
                    snake.push_front(head);
                    if (head == food)
                    {
                        score++;
                        food = randomFood(snake); // eat: spawn new food, don't pop tail
                    }
                    else
                    {
                        snake.pop_back(); // normal move: remove tail
                    }
                }
            }
        }

        // --- Draw ---
        window.clear(sf::Color(20, 20, 20));

        // Draw faint vertical lines
        for (int x = 0; x < WIDTH; x += CELL)
        {
            sf::RectangleShape line(sf::Vector2f(1, HEIGHT));
            line.setPosition(sf::Vector2f(x, 0));
            line.setFillColor(sf::Color(40, 40, 40));
            window.draw(line);
        }

        // Draw faint horizontal lines
        for (int y = 0; y < HEIGHT; y += CELL)
        {
            sf::RectangleShape line(sf::Vector2f(WIDTH, 1));
            line.setPosition(sf::Vector2f(0, y));
            line.setFillColor(sf::Color(40, 40, 40));
            window.draw(line);
        }

        // Snake
        for (size_t i = 0; i < snake.size(); i++)
        {
            float t = 1.f - (float)i / snake.size(); // 1.0 at head, ~0.0 at tail

            cell.setFillColor(sf::Color(
                static_cast<uint8_t>(50 + 180 * t), // red channel
                static_cast<uint8_t>(200),          // green channel
                static_cast<uint8_t>(50)            // blue channel
                ));
            cell.setPosition(sf::Vector2f(snake[i].x * CELL + 1.f, snake[i].y * CELL + 1.f));
            window.draw(cell);
        }

        // Food
        cell.setFillColor(sf::Color(220, 50, 50));
        cell.setPosition(sf::Vector2f(food.x * CELL + 1.f, food.y * CELL + 1.f));
        window.draw(cell);

        // Score
        scoreText.setString("Score: " + std::to_string(score));
        window.draw(scoreText);

        // Game over overlay
        if (gameOver)
        {
            // Semi-transparent dark overlay
            sf::RectangleShape overlay(sf::Vector2f(WIDTH, HEIGHT));
            overlay.setFillColor(sf::Color(0, 0, 0, 150));
            window.draw(overlay);

            // Centered message
            msgText.setString("GAME OVER  |  R to restart");
            sf::FloatRect bounds = msgText.getLocalBounds();
            msgText.setPosition({WIDTH / 2.f - bounds.size.x / 2.f,
                                HEIGHT / 2.f - bounds.size.y / 2.f});
            window.draw(msgText);
        }

        window.display();
    }
}
