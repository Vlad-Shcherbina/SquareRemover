#include <iostream>
#include <string>
#include <vector>
#include <cassert>
#include <cstdlib>
#include <algorithm>
#include <iterator>
#include <inttypes.h>

#include "pretty_printing.h"

using namespace std;

const int NUM_MOVES = 10000;
int n = -1;
vector<int> buffer;


const int VERT = 1024;
typedef int Move;

int move_x(Move m) {
  return (m & ~VERT) % n - 1;
}

int move_y(Move m) {
  return (m & ~VERT) / n - 1;
}

int move_dir(Move m) {
  if (m & VERT)
    return 2;
  return 1;
}

Move pack_move(int y, int x, bool vert) {
  if (vert)
    return VERT | (y * n + x + n + 1);
  return y * n + x + n + 1;
}


struct State {
  vector<char> cells;
  int score;

  friend std::ostream& operator<<(std::ostream &out, const State &s);

  vector<Move> possible_moves() {
    vector<Move> result;
    for (int i = 0; i < n - 2; i++) {
      for (int j = 0; j < n - 3; j++) {
        result.push_back(pack_move(i, j, false));
        result.push_back(pack_move(j, i, true));
      }
    }
    return result;
  }

  int find_block() {
    for (int i = 1; i < n - 2; i++) {
      for (int j = 1; j < n - 2; j++) {
        int idx = i * n + j;
        char c = cells[idx];
        if (c == cells[idx + 1] &&
            c == cells[idx + n] &&
            c == cells[idx + n + 1]) {
          return idx;
        }
      }
    }
    return -1;
  }

  void collapse() {
    while (true) {
      int idx = find_block();
      if (idx == -1)
        return;
      cells[idx] = buffer[score * 4];
      cells[idx + 1] = buffer[score * 4 + 1];
      cells[idx + n] = buffer[score * 4 + 2];
      cells[idx + n + 1] = buffer[score * 4 + 3];
      score += 1;
    }
  }

  void make_move(Move move) {
    int idx = move & ~VERT;
    int idx2 = idx + 1;
    if (move & VERT)
      idx2 = idx + n;
    swap(cells[idx], cells[idx2]);
    collapse();
  }
};

std::ostream& operator<<(std::ostream &out, const State &s) {
  for (int i = 1; i < n - 1; i++) {
    for (int j = 1; j < n - 1; j++)
      out << (int)s.cells[i * n + j] << ' ';
    out << endl;
  }
  out << "score = " << s.score << endl;
  return out;
}


class SquareRemover{
public:
  vector<int> playIt(int colors, vector<string> board, int start_seed) {
    ::n = board.size() + 2;
    State state;
    state.score = 0;
    state.cells = vector<char>(n, 9);

    for (string row : board) {
      assert(row.size() == board.size());
      state.cells.push_back(9);
      //copy(row.begin(), row.end(), back_inserter(state.cells));
      for (int c : row)
        state.cells.push_back(c - '0');
      state.cells.push_back(9);
    }
    fill_n(back_inserter(state.cells), n, 9);

    uint64_t a = start_seed;
    for (int i = 0; i < NUM_MOVES * 4 * 10; i++) {
      buffer.push_back(a % colors);
      a = (a * (uint64_t)48271) % (uint64_t)2147483647;
    }

    state.collapse();

    vector<int> result;

    for (int i = 0; i < NUM_MOVES; i++) {
      vector<Move> moves = state.possible_moves();
      Move move = moves[rand() % moves.size()];
      state.make_move(move);

      result.push_back(move_y(move));
      result.push_back(move_x(move));
      result.push_back(move_dir(move));
    }
    cerr << "simulated score = " << state.score << endl;
    return result;
  }
};


int main(int argc, char *argv[]) {
  int colors, n, start_seed;
  cin >> colors;
  cin >> n;
  cerr << "# dict(type='size', n=" << n << ", colors=" << colors << ") #" << endl;
  vector<string> board(n);
  for (int i = 0; i < n; i++) {
    cin >> board[i];
    assert(board[i].length() == n);
  }
  cin >> start_seed;

  vector<int> result = SquareRemover().playIt(colors, board, start_seed);
  for (int i : result)
    cout << i << endl;

  return 0;
}
