#include <SFML/Graphics.hpp>
#include <deque>
#include <cstdlib>
#include <string>

// --- Constants ---
const int WIDTH = 800, HEIGHT = 600;
const int CELL = 20; // grid cell size in pixels
const float MOVE_INTERVAL = 0.12f; // seconds between snake moves

// --- Helper Functions ---
sf::Vector2i randomFood(const std::deque<sf::Vector2i>& snake){
    int cols = WIDTH / CELL, rows = HEIGHT / CELL;
    sf::Vector2i pos;
    do {
        pos = {std::rand() % cols, std::rand() % rows};
    } while ([&]{for (auto& s : snake) if (s == pos) return true; return false; }());
    return pos;
}

// --- Main Loop ---
int main(){
    std::srand(static_cast<unsigned>(std::time(nullptr))); // seed RNG
    //std::srand(1); // set seed

    sf::RenderWindow window(sf::VideoMode({WIDTH, HEIGHT}), "Snake");
    window.setFramerateLimit(60);

    // --- Snake ---
    std::deque<sf::Vector2i> snake;
    snake.push_back({WIDTH / CELL / 2, HEIGHT / CELL / 2}); // head
    snake.push_back({WIDTH / CELL / 2 - 1, HEIGHT / CELL / 2}); // body
    snake.push_back({WIDTH / CELL / 2 - 2, HEIGHT / CELL / 2}); // tail

    sf::Vector2i direction(1, 0); // moving right
    sf::Vector2i nextDir(1, 0); // direction queued from input

    // --- Food ---
    sf::Vector2i food = randomFood(snake);

    // --- State ---
    bool gameOver = false;
    float timer = 0.f;
    sf::Clock clock;

    auto resetGame = [&]() {
        snake.clear();
        snake.push_back({WIDTH / CELL / 2, HEIGHT / CELL / 2}); // head
        snake.push_back({WIDTH / CELL / 2 - 1, HEIGHT / CELL / 2}); // body
        snake.push_back({WIDTH / CELL / 2 - 2, HEIGHT / CELL / 2}); // tail
        direction = nextDir = {1, 0};
        food = randomFood(snake);
        gameOver = false;
        timer = 0.f;
    };

    // --- Reusable rectangle for drawing cells ---
    sf::RectangleShape cell(sf::Vector2f(CELL - 2.f, CELL - 2.f)); // 1px gap on each side

    while (window.isOpen()) {
        float dt = clock.restart().asSeconds();

        // --- Events ---
        while (const std::optional event = window.pollEvent()) {
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
            }
        }

        // --- Update ---
        timer += dt;
        if (timer >= MOVE_INTERVAL) {
            timer = 0.f;
            direction = nextDir; // commit the queued direction only on each step

            sf::Vector2i head = snake.front() + direction;
            snake.push_front(head);

            if (head == food) {
                food = randomFood(snake); // eat: spawn new food, don't pop tail
            } else {
                snake.pop_back(); // normal move: remove tail
            }
        }

        // --- Draw ---
        window.clear(sf::Color(20, 20, 20));

        // Draw faint vertical lines
        for (int x = 0; x < WIDTH; x += CELL){
            sf::RectangleShape line(sf::Vector2f(1, HEIGHT));
            line.setPosition(sf::Vector2f(x, 0));
            line.setFillColor(sf::Color(40, 40, 40));
            window.draw(line);
        }

        // Draw faint horizontal lines
        for (int y = 0; y < HEIGHT; y += CELL){
            sf::RectangleShape line(sf::Vector2f(WIDTH, 1));
            line.setPosition(sf::Vector2f(0, y));
            line.setFillColor(sf::Color(40, 40, 40));
            window.draw(line);
        }

        // Snake
        for (size_t i = 0; i < snake.size(); i++){
            float t = 1.f - (float)i / snake.size(); // 1.0 at head, ~0.0 at tail
            
            cell.setFillColor(sf::Color(
                static_cast<uint8_t>(50 + 180 * t), // red channel
                static_cast<uint8_t>(200), // green channel
                static_cast<uint8_t>(50) // blue channel
            ));
            cell.setPosition(sf::Vector2f(snake[i].x * CELL + 1.f, snake[i].y * CELL + 1.f));
            window.draw(cell);
        }

        // Food
        cell.setFillColor(sf::Color(220, 50, 50));
        cell.setPosition(sf::Vector2f(food.x * CELL + 1.f, food.y * CELL + 1.f));
        window.draw(cell);

        window.display();
    }
}
