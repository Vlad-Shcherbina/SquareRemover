#include <cassert>
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <cstdlib>
#include <algorithm>
#include <iterator>
#include <inttypes.h>
#include <sys/time.h>

#include "pretty_printing.h"

using namespace std;

double TIME_LIMIT = 29.4;
const int NUM_MOVES = 10000;
int n = -1;
vector<int> buffer;


double get_time() {
    timeval tv;
    gettimeofday(&tv, 0);
    return tv.tv_sec + tv.tv_usec * 1e-6;
}


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


class Undoer;


struct State {
  vector<char> cells;
  int score;
  int connections;

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

  int find_block(int i1, int j1, int i2, int j2) {
    for (int i = i1; i < i2 - 1; i++) {
      for (int j = j1; j < j2 - 1; j++) {
        int idx = i * n + j;
        char c = cells[idx];
        if (c == cells[idx + 1] &&
            c == cells[idx + n] &&
            c == cells[idx + n + 1])
          return idx;
      }
    }
    return -1;
  }

  int naive_connections() const {
    int result = 0;
    for (int i = 1; i < n - 1; i++)
      for (int j = 1; j < n - 2; j++) {
        int idx = i * n + j;
        if (cells[idx] == cells[idx + 1])
          result++;
        idx = j * n + i;
        if (cells[idx] == cells[idx + n])
          result++;
      }
    return result;
  }

  void assign(int idx, char color) {
    if (cells[idx] == color)
      return;
    char *p = &cells[idx];
    if (p[0] == p[1])
      connections--;
    if (p[0] == p[-1])
      connections--;
    if (p[0] == p[n])
      connections--;
    if (p[0] == p[-n])
      connections--;

    p[0] = color;

    if (p[0] == p[1])
      connections++;
    if (p[0] == p[-1])
      connections++;
    if (p[0] == p[n])
      connections++;
    if (p[0] == p[-n])
      connections++;

    //assert(connections == naive_connections());
  }

  void make_move(Move move, Undoer &undoer);
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


struct Undoer {
  State *state;
  int score;
  int connections;
  vector<int> change_history;

  Undoer(State &state) : state(&state) {
    score = state.score;
    connections = state.connections;
  }

  void record_two_changes(int idx1, int value1, int idx2, int value2) {
    assert(idx1 >= 0 && idx1 < 512);
    assert(value1 >= 0 && value1 < 8);
    assert(idx2 >= 0 && idx2 < 512);
    assert(value2 >= 0 && value2 < 8);
    assert(idx1 != idx2);
    change_history.push_back(
        (idx1 * 8 + value1) * 4096 +
        (idx2 * 8 + value2));
  }

  ~Undoer() {
    for (int i = change_history.size() - 1; i >= 0; i--) {
      int v = change_history[i];
      assert(v >= 0 && v <= 4096 * 4096);
      int idx1 = v / (8*4096);
      int idx2 = v % 4096 / 8;
      assert(idx1 < state->cells.size());
      assert(idx2 < state->cells.size());
      state->cells[idx1] = v / 4096 % 8;
      state->cells[idx2] = v % 8;
    }
    state->score = score;
    state->connections = connections;
  }
};


void State::make_move(Move move, Undoer &undoer) {
  assert(undoer.state == this);

  int i1, j1, i2, j2;

  if (move != -1) {
    int idx = move & ~VERT;
    int idx2 = idx + 1;
    if (move & VERT) {
      idx2 = idx + n;
    }
    if (cells[idx] == cells[idx2])
      return;
    undoer.record_two_changes(idx, cells[idx], idx2, cells[idx2]);
    char t = cells[idx];
    assign(idx, cells[idx2]);
    assign(idx2, t);
    if (move & VERT) {
      if (cells[idx - n] != cells[idx] &&
          cells[idx] != cells[idx + n] &&
          cells[idx + n] != cells[idx + 2 * n])
        return;
      i1 = idx / n - 1;
      j1 = idx % n - 1;
      i2 = i1 + 4;
      j2 = j1 + 3;
    } else {
      if (cells[idx - 1] != cells[idx] &&
          cells[idx] != cells[idx + 1] &&
          cells[idx + 1] != cells[idx + 2])
        return;
      i1 = idx / n - 1;
      j1 = idx % n - 1;
      i2 = i1 + 3;
      j2 = j1 + 4;
    }
  } else {
    i1 = j1 = 1;
    i2 = j2 = n - 1;
  }

  while (true) {
    int idx = find_block(i1, j1, i2, j2);
    if (idx == -1)
      return;
    assert(score * 4 + 3 < buffer.size());
    auto *buf = &buffer[score * 4];
    undoer.record_two_changes(
        idx, cells[idx],
        idx + 1, cells[idx + 1]);
    undoer.record_two_changes(
        idx + n, cells[idx + n],
        idx + n + 1, cells[idx + n + 1]);
    assign(idx, buf[0]);
    assign(idx + 1, buf[1]);
    assign(idx + n, buf[2]);
    assign(idx + n + 1, buf[3]);
    score += 1;

    if (i1 > 1) i1--;
    if (j1 > 1) j1--;
    if (i2 < n - 1) i2++;
    if (j2 < n - 1) j2++;
  }
}


#include "patterns.h"


struct Step {
  float score;
  int state_index;
  const PatternInstance *pi;
  int prev_step_index;
};


void insert_new_step(
    const Step &new_step, const State &new_state,
    vector<Step> &steps, vector<State> &states,
    int beam_width) {
  assert(steps.size() == states.size());
  assert(beam_width >= 0);

  struct Comp {
    bool operator()(const Step &s1, const Step &s2) const {
      return s1.score > s2.score;
    }
  };
  auto insert_point = upper_bound(steps.begin(), steps.end(), new_step, Comp());

  if (steps.size() < beam_width) {
    steps.insert(insert_point, new_step)->state_index = states.size();
    states.push_back(new_state);
  } else {
    if (insert_point == steps.end())
      return;
    int t = steps.back().state_index;
    copy_backward(insert_point, steps.end() - 1, steps.end());
    *insert_point = new_step;
    insert_point->state_index = t;
    states[t] = new_state;
  }
}


class SquareRemover{
public:
  vector<int> playIt(int colors, vector<string> board, int start_seed) {
    double start = get_time();
    ::n = board.size() + 2;

    bool scarce = colors == 6 && board.size() <= 12;
    float pi_depth = 2;
    if (scarce)
      pi_depth = board.size() == 8 ? 2.75 : 2.5;
    cerr << "# dict(pi_depth=" << pi_depth << ") #" << endl;

    vector<PatternInstance> pis;
    for (int i = 1; i < pi_depth + 1; i++) {
      PatternGenerator pg;
      pg.generate(i);
      cerr << pg.result.size() << " patterns" << endl;
      for (auto p : pg.result) {
        vector<PatternInstance> local_pis;
        p.instantiate(local_pis);
        for (auto pi : local_pis)
          if (i - 1 + rand() % 100 * 0.01 < pi_depth)
            pis.push_back(pi);
      }
    }
    generate_pseudo_pis(pis);
    cerr << "# dict(num_pis=" << pis.size() << ") #" << endl;

    State state;
    state.score = 0;
    state.cells = vector<char>(n, 9);

    for (string row : board) {
      assert(row.size() == board.size());
      state.cells.push_back(9);
      for (int c : row)
        state.cells.push_back(c - '0');
      state.cells.push_back(9);
    }
    fill_n(back_inserter(state.cells), n, 9);
    state.connections = state.naive_connections();

    uint64_t a = start_seed;
    for (int i = 0; i < NUM_MOVES * 4 * 10; i++) {
      buffer.push_back(a % colors);
      a = (a * (uint64_t)48271) % (uint64_t)2147483647;
    }

    State orig_state = state;
    vector<int> result;

    {Undoer global_undoer(state);

    state.make_move(-1, global_undoer);

    vector<vector<Step>> beam_steps(NUM_MOVES + 1);
    vector<vector<State>> beam_states(NUM_MOVES + 1);
    beam_states[0].push_back(state);
    Step start_step;
    start_step.score = 0.0;
    start_step.state_index = 0;
    start_step.pi = nullptr;
    start_step.prev_step_index = -1;
    beam_steps[0].push_back(start_step);

    int beam_area = 0;

    double t0 = get_time();
    for (int stage = 0; stage < NUM_MOVES; stage++) {
      assert(beam_steps[stage].size() == beam_states[stage].size());

      int recommended_beam_widht = 10;
      double t = get_time() - t0;
      if (t > 0.02) {
        recommended_beam_widht = rand() % 10 * 0.1 + 1.0 *
            beam_area * (start + TIME_LIMIT - t - t0) / t / (NUM_MOVES - stage);
        if (stage < 50 || stage % 500 == 0) {
          cerr << stage << " beam width " << recommended_beam_widht << endl;
        }
        recommended_beam_widht = min(max(1, recommended_beam_widht), 200);
      }

      for (int i = 0; i < beam_steps[stage].size(); i++) {
        beam_area++;
        State state = beam_states[stage][beam_steps[stage][i].state_index];
        bool had_proper_pis = false;
        for (const auto &pi : pis) {
          if (had_proper_pis && pi.is_pseudo())
            continue;
          if (pi.match(state)) {
            if (!pi.is_pseudo())
              had_proper_pis = true;

            Undoer u(state);

            bool precollapse = false;
            for (int i = 0; i < pi.moves.size(); i++) {
              if (state.score > u.score) {
                precollapse = true;
                break;
              }
              state.make_move(pi.moves[i], u);
            }
            if (precollapse)
              continue;

            Step new_step;
            float conn_weight = scarce ? 0.001 : 0.15;
            if (had_proper_pis)
              new_step.score = state.score + conn_weight * state.connections;
            else
              new_step.score = state.score + rand() % 1000 * 0.001;
            new_step.pi = &pi;
            new_step.prev_step_index = i;

            int new_stage = stage + pi.moves.size();
            if (new_stage > NUM_MOVES)
              continue;
            int beam_width = recommended_beam_widht;
            if (new_stage == NUM_MOVES)
              beam_width = 1;
            insert_new_step(
                new_step, state, beam_steps[new_stage], beam_states[new_stage],
                beam_width);
          }
        }
      }
    }
    cerr << "# dict(beam_area=" << beam_area << ") #" << endl;
    cerr << "best results:" << endl;
    for (auto step : beam_steps[NUM_MOVES]) {
      cerr << step.score << endl;
    }

    vector<Move> best_moves;
    int stage = NUM_MOVES;
    int idx = 0;
    while (stage > 0) {
      Step step = beam_steps[stage][idx];
      copy(step.pi->moves.rbegin(), step.pi->moves.rend(),
          back_inserter(best_moves));
      stage -= step.pi->moves.size();
      idx = step.prev_step_index;
    }
    reverse(best_moves.begin(), best_moves.end());

    assert(best_moves.size() == NUM_MOVES);
    for (Move best_move : best_moves) {
      state.make_move(best_move, global_undoer);
      result.push_back(move_y(best_move));
      result.push_back(move_x(best_move));
      result.push_back(move_dir(best_move));
    }

    cerr << "simulated score " << state.score << endl;

    } // global_undoer

    assert(orig_state.cells == state.cells);

    cerr << "# dict(time=" << get_time() - start << ") #" << endl;
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
