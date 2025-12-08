#include "vector"
#include "iostream"
#include <fstream>
#include <utility>
#include <vector>
using namespace std;


class Graph {
    vector<vector<int> > adj_matrix;

public:
    Graph (int n) {
        adj_matrix = vector<vector<int> >(n, vector<int>(n, -1));
    };

    void add_edge(int u, int v) {

        for (int i = 0; i < adj_matrix[0].size(); i ++) {
        if (adj_matrix[u][i] == -1 && adj_matrix[v][i] == -1) {
            adj_matrix[u][i] = v;
            adj_matrix[v][i] = u;
            return;
        }
    }
    int free_colour_1 = -1;
    int free_colour_2 = -1;


    for (int i = 0; i < adj_matrix[0].size(); i++) {
            if (adj_matrix[u][i] == -1 && free_colour_1 == -1) {
                free_colour_1 = i;
            }
            if (adj_matrix[v][i] == -1 && free_colour_2 == -1) {
                free_colour_2 = i;
            }
            if (free_colour_1 != -1 && free_colour_2 != -1) {
                break;
            }
        }


    invert_colours(v, free_colour_1, free_colour_2);
    adj_matrix[u][free_colour_1] = v;
    adj_matrix[v][free_colour_1] = u;

    }

    void print_result(bool full_display)
    {
        ofstream output("output.txt");
        int max_color_used = 0;

        if (full_display) {
            cout << "Edge List with Colors:" << endl;
            output << "Edge List with Colors:" << endl;
        }
        for (int u = 0; u < adj_matrix.size(); u++) {
            for (int colorur = 0; colorur < adj_matrix.size(); colorur++) {
                int v = adj_matrix[u][colorur];
                if (v != -1) {
                    if (colorur + 1 > max_color_used) max_color_used = colorur + 1;
                    if (u < v && full_display) {
                        cout << "Edge " << u << " - " << v << " : Color " << colorur + 1 << endl;
                        output << "Edge " << u << " - " << v << " : Color " << colorur + 1 << endl;
                    }
                }
            }
        }
        cout << "Total colors used: " << max_color_used << endl;
        output << "Total colors used: " << max_color_used << endl;
        output.close();
    }


void invert_colours(int strat_node, int colour_1, int colour_2) {
    int curr_node = strat_node;
    int current_colour = colour_1;
    int next_colour = colour_2;
    while (true) {
        int next_node  = adj_matrix[curr_node][current_colour];
        if (next_node == -1) {
            break;
        }

        adj_matrix[curr_node][current_colour] = -1;
        adj_matrix[next_node][current_colour] = -1;

        adj_matrix[curr_node][next_colour] = next_node;
        adj_matrix[next_node][next_colour] = curr_node;

        curr_node = next_node;

        swap(current_colour, next_colour);

    }
}
};




int main()
{
    ifstream file("test.txt");
    if (!file.is_open()){
        cout << "Error: File not found!" << endl;
        return 1;
    }

    vector<pair<int, int>> input_edges;
    int u, v;
    int max_vertex_id = 0;

    while (file >> u >> v) {
        input_edges.push_back({u, v});

        max_vertex_id = max(max_vertex_id, max(u,v));
        }
    int n = max_vertex_id + 1;

    Graph g(n);


    for (const auto& edge : input_edges) {
        g.add_edge(edge.first, edge.second);
    }

    g.print_result(true);


    return 0;
}