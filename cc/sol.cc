#include <iostream>
#include <string>
#include <vector>
#include <cassert>

#include "pretty_printing.h"

using namespace std;


class SquareRemover{
public:
  vector<int> playIt(int colors, vector<string> board, int start_seed) {
    cerr << __GNUC__ << '.' << __GNUC_MINOR__ << '.' << __GNUC_PATCHLEVEL__ << endl;
    return vector<int>(30000, 1);
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
  for (int i = 0; i < result.size(); i++)
    cout << result[i] << endl;

  return 0;
}
