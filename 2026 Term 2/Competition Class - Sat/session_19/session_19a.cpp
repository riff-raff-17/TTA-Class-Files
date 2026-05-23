// Conway's Game of Life - SFML

#include <SFML/Graphics.hpp>
#include <vector>
#include <cstdlib>
#include <string>

const int WIDTH = 800, HEIGHT = 600;

// --- Grid helpers ---
using Grid = std::vector<std::vector<bool>>;

Grid makeGrid(int cols, int rows)
{
    return Grid(cols, std::vector<bool>(rows, false));
}

void randomize(Grid &g, int cols, int rows)
{
    for (int x = 0; x < cols; x++)
        for (int y = 0; y < rows; y++)
            g[x][y] = (std::rand() % 4 == 0); // ~25% alive
}

int countNeighbors(const Grid &g, int x, int y, int cols, int rows)
{
    int count = 0;
    for (int dx = -1; dx <= 1; dx ++) // outer loop
    {
        for (int dy = -1; dy <= 1; dy++) // inner loop
        {
            if (dx == 0 && dy == 0)
                continue;
            int nx = (x + dx + cols) % cols; // wrap edges
            int ny = (y + dy + rows) % rows;
            if (g[nx][ny])
                count++;
        }
    }
    return count;
}

Grid step(const Grid &current, int cols, int rows)
{
    Grid next = makeGrid(cols, rows);
    for (int x = 0; x < cols; x++)
    {
        for (int y = 0; y < rows; y++)
        {
            int n = countNeighbors(current, x, y, cols, rows);
            if (current[x][y])
                next[x][y] = (n == 2 || n == 3); // survive
            else
                next[x][y] = (n == 3); // born
        }
    }
    return next;
}