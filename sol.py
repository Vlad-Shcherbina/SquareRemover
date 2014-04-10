import sys
import random
import itertools
from timeit import default_timer


NUM_MOVES = 10000
TIME_LIMIT = 28.0

n = None
colors = None


def find_square_in_range(board, i1, j1, i2, j2):
    if i1 < 1:
        i1 = 1
    if j1 < 1:
        j1 = 1
    if i2 > n - 2:
        i2 = n - 2
    if j2 > n - 2:
        j2 = n - 2
    for i in range(i1 * n, i2 * n, n):
        for idx in range(i + j1, i + j2):
            if board[idx] == board[idx + 1] == board[idx + n] == board[idx + n + 1]:
                return idx
    return None


DIAG = 0.4
def connection_cost(board, idx, color):
    result = 0
    if board[idx - 1] == color:
        result += 1
    if board[idx + 1] == color:
        result += 1
    if board[idx - n] == color:
        result += 1
    if board[idx - n] == color:
        result += 1

    if board[idx - 1 - n] == color:
        result += DIAG
    if board[idx + 1 - n] == color:
        result += DIAG
    if board[idx - 1 + n] == color:
        result += DIAG
    if board[idx + 1 + n] == color:
        result += DIAG
    return result


def enum_moves(board):
    for i in range(1, n - 1):
        for j in range(1, n - 2):
            idx = i * n + j
            idx2 = idx + 1
            if board[idx] != board[idx2]:
                cut_cost = (
                    connection_cost(board, idx, board[idx]) +
                    connection_cost(board, idx2, board[idx2]))
                add_cost = (
                    connection_cost(board, idx, board[idx2]) +
                    connection_cost(board, idx2, board[idx]))
                yield idx * 2, cut_cost, add_cost
            idx = j * n + i
            idx2 = idx + n
            if board[idx] != board[idx2]:
                cut_cost = (
                    connection_cost(board, idx, board[idx]) +
                    connection_cost(board, idx2, board[idx2]))
                add_cost = (
                    connection_cost(board, idx, board[idx2]) +
                    connection_cost(board, idx2, board[idx]))
                yield idx * 2 + 1, cut_cost, add_cost


class Simulator(object):
    def __init__(self, board, start_seed):
        self.score = 0
        self.board = board[:]

        self.prev_scores = []
        self.prev_boards = []

        self.future = []
        self.a = start_seed

        # To stabilize stuff
        self.make_move(None)
        self.prev_scores = []
        self.prev_boards = []

    def make_move(self, move):
        self.prev_scores.append(self.score)
        self.prev_boards.append(self.board)
        board = self.board[:]

        if move is None:
            i1 = 1
            j1 = 1
            i2 = n - 2
            j2 = n - 2
        else:
            idx = move // 2
            i1 = idx // n - 1
            j1 = idx % n - 1
            if move % 2 == 0:
                t = board[idx]
                board[idx] = board[idx + 1]
                board[idx + 1] = t
                i2 = i1 + 2
                j2 = j1 + 3
            else:
                t = board[idx]
                board[idx] = board[idx + n]
                board[idx + n] = t
                i2 = i1 + 3
                j2 = j1 + 2

        while True:
            idx = find_square_in_range(board, i1, j1, i2, j2)
            if idx is None:
                break

            if len(self.future) <= 4 * self.score:
                for _ in range(4):
                    self.future.append(int(self.a % colors))
                    self.a = (self.a * 48271) % 2147483647

            board[idx] = self.future[self.score * 4]
            board[idx + 1] = self.future[self.score * 4 + 1]
            board[idx + n] = self.future[self.score * 4 + 2]
            board[idx + n + 1] = self.future[self.score * 4 + 3]
            self.score += 1
            i1 -= 1
            j1 -= 1
            i2 += 1
            j2 += 1

        self.board = board

    def undo_move(self):
        self.score = self.prev_scores.pop()
        self.board = self.prev_boards.pop()

def filter_move_candidates(candidates):
    filtered_candidates = [
        (m, c, a)
        for m, c, a in candidates
        if a - c > 0 or a >= 2 + DIAG]

    if not filtered_candidates:
        filtered_candidates = candidates
    return filtered_candidates


def find_best_moves(depth, sim):
    """Return pair (score, list of optimal moves)"""

    best_score = [-1]
    best_moves = []

    moves = []

    def rec(depth):
        if depth == 0:
            s = sim.score + random.random()*0.01
            if s > best_score[0]:
                best_score[0] = s
                best_moves[:] = moves
            return
        for move, c, a in filter_move_candidates(list(enum_moves(sim.board))):
            delta = a - c
            sim.make_move(move)
            moves.append(move)
            sim.score += 0.01 * delta
            rec(depth - 1)
            sim.score -= 0.01 * delta
            moves.pop()
            sim.undo_move()

    rec(depth)

    #assert len(best_moves) == depth
    return best_score, best_moves


class SquareRemover(object):
    @staticmethod
    def playIt(colors_, board, start_seed):
        global colors
        global n

        start = default_timer()

        colors = colors_
        n = len(board)
        print>>sys.stderr, 'colors={}, n={}'.format(colors, n)
        n += 2
        board = [9] * n + [int(c) for row in board for c in '9' + row + '9'] + [9] * n
        assert len(board) == n*n

        random.seed(42)
        result = []
        sim = Simulator(board, start_seed)

        step = 1
        for i in range(0, NUM_MOVES, step):
            if default_timer() > start + TIME_LIMIT:
                print>>sys.stderr, 'timeout!'
                print>>sys.stderr, i, s, ms
                break
            depth = min(NUM_MOVES - i, step)
            s, ms = find_best_moves(depth, sim)
            if not ms:
                print>>sys.stderr, 'something strange!'
                break
            if (i + 1) % 1000 == 0:
                print>>sys.stderr, i, s, ms
                sys.stderr.flush()
            for move in ms:
                sim.make_move(move)
                result += [move // (2*n) - 1, move // 2 % n - 1, move % 2 + 1]

        for _ in range(len(result) // 3, NUM_MOVES):
            i = random.randrange(n - 3)
            j = random.randrange(n - 3)
            d = random.randrange(1, 2 + 1)
            sim.make_move(((i + 1) * n + j + 1) * 2 + d - 1)
            result += [i, j, d]

        print>>sys.stderr, 'it took', default_timer() - start
        print>>sys.stderr, 'simulated score', sim.score
        sys.stderr.flush()
        return result


def main():
    global n
    colors = int(raw_input())
    n = int(raw_input())
    board = []
    for i in range(n):
        row = raw_input().strip()
        board.append(row)

    start_seed = int(raw_input())
    for x in SquareRemover.playIt(colors, board, start_seed):
        print x


if __name__ == '__main__':
    main()
