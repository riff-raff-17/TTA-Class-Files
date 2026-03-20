# include <iostream>
# include <stack>
# include <queue>
using namespace std;

const int MAX_N = 1000;

int grid[MAX_N][MAX_N];
bool visited[MAX_N][MAX_N];
int row_num, col_num;
int curr_size = 0;

void floodfill(int r, int c, int color){
    if (r < 0 || r >= row_num || c < 0 || c >= col_num ||
        grid[r][c] != color || visited[r][c])
        return;

    visited[r][c] = true;
    curr_size++;

    floodfill(r, c + 1, color);
    floodfill(r + 1, c, color);
    floodfill(r, c - 1, color);
    floodfill(r - 1, c, color);
}

// Direction vectors
const int R_CHANGE[] = {0, 1, 0, -1};
const int C_CHANGE[] = {1, 0, -1, 0};

void floodfill_dfs(int start_r, int start_c, int color){
    stack<pair<int, int>> frontier;
    frontier.push({start_r, start_c});

    while (!frontier.empty()){
        int r = frontier.top().first;
        int c = frontier.top().second;
        frontier.pop();

        if (r < 0 || r >= row_num || c < 0 || c >= col_num ||
            grid[r][c] != color || visited[r][c])
            continue;

        visited[r][c] = true;
        curr_size++;

        // Push 4 neighbors
        for (int i = 0; i < 4; i++){
            int nr = r + R_CHANGE[i];
            int nc = c + C_CHANGE[i];
            frontier.push({nr, nc});
        }
    }
}

void floodfill_bfs(int start_r, int start_c, int color){
    queue<pair<int, int>> frontier;
    frontier.push({start_r, start_c});

    while (!frontier.empty()){
        int r = frontier.front().first;
        int c = frontier.front().second;
        frontier.pop();

        if (r < 0 || r >= row_num || c < 0 || c >= col_num ||
            grid[r][c] != color || visited[r][c])
            continue;

        visited[r][c] = true;
        curr_size++;

        // Push 4 neighbors
        for (int i = 0; i < 4; i++){
            int nr = r + R_CHANGE[i];
            int nc = c + C_CHANGE[i];
            frontier.push({nr, nc});
        }
    }
}

int main(){
    // Read in grid dimensions
    cin >> row_num >> col_num;

    // Read in grid values
    for (int i = 0; i < row_num; i++){
        for (int j = 0; j < col_num; j++){
            cin >> grid[i][j];
            visited[i][j] = false;
        }
    }

    int component_count = 0;

    // Process components
    for (int i = 0; i < row_num; i++){
        for (int j = 0; j < col_num; j++){
            if (!visited[i][j]){
                curr_size = 0;
                floodfill_bfs(i, j, grid[i][j]);
                component_count++;
            }
        }
    }
    cout << component_count << endl;
}