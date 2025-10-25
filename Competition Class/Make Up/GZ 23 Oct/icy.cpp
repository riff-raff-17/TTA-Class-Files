# include <iostream>
# include <stack>
# include <string>

using namespace std;

const int MAX_N = 1000;

int grid[MAX_N][MAX_N];
bool visited[MAX_N][MAX_N];
int row_num, col_num;
int curr_area = 0;
int curr_perim = 0;

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
        curr_area++;

        // Push 4 neighbors
        for (int i = 0; i < 4; i++){
            int nr = r + R_CHANGE[i];
            int nc = c + C_CHANGE[i];
            if (nr < 0 || nr >= row_num || nc < 0 || nc >= col_num || grid[nr][nc] != color){
                curr_perim++;
            } else{
                if (!visited[nr][nc]){
                    frontier.push({nr, nc});
                }
            }
        }
    }
}

int main(){
    int N;
    cin >> N;
    row_num = col_num = N;

    // Read in grid values
    for (int i = 0; i < row_num; i++){
        string line;
        cin >> line;
        for (int j = 0; j < col_num; j++){
            grid[i][j] = line[j];
            visited[i][j] = false;
        }
    }

    int best_area = 0;
    int best_perim = 0;

    // Process components
    for (int i = 0; i < row_num; i++){
        for (int j = 0; j < col_num; j++){
            if (!visited[i][j] && grid[i][j] == '#'){
                curr_area = 0;
                curr_perim = 0;
                floodfill_dfs(i, j, grid[i][j]);

                if (curr_area > best_area || 
                    (curr_area == best_area && curr_perim < best_perim)){
                        best_area = curr_area;
                        best_perim = curr_perim;
                }
            }
        }
    }
    cout << best_area << " " << best_perim << endl;
}