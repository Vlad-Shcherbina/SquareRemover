import sys
import random
import itertools
from timeit import default_timer

import collections

from patterns import *


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


buffer = []

def extend_buffer():
    global buffer, _a
    buffer.append(int(_a % colors))
    _a = (_a * 48271) % 2147483647


class Simulator(object):
    def __init__(self, board):
        self.score = 0
        self.board = board[:]
        self.connections = 0.0

        self.prev_scores = []
        self.prev_boards = []
        self.prev_connections = []

        # To stabilize stuff
        self.make_move(None)
        self.prev_scores = []
        self.prev_boards = []
        self.prev_connections = []

    def make_move(self, move):
        self.prev_scores.append(self.score)
        self.prev_boards.append(self.board)
        self.prev_connections.append(self.connections)
        board = self.board[:]

        def assign(idx, color):
            self.connections -= connection_cost(board, idx, board[idx])
            board[idx] = color
            self.connections += connection_cost(board, idx, color)

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
                c1 = board[idx]
                c2 = board[idx + 1]
                assign(idx, c2)
                assign(idx + 1, c1)
                i2 = i1 + 2
                j2 = j1 + 3
            else:
                c1 = board[idx]
                c2 = board[idx + n]
                assign(idx, c2)
                assign(idx + n, c1)
                i2 = i1 + 3
                j2 = j1 + 2

        while True:
            idx = find_square_in_range(board, i1, j1, i2, j2)
            if idx is None:
                break

            if len(buffer) <= 4 * self.score:
                for _ in range(4):
                    extend_buffer()

            assign(idx, buffer[self.score * 4])
            assign(idx + 1, buffer[self.score * 4 + 1])
            assign(idx + n, buffer[self.score * 4 + 2])
            assign(idx + n + 1, buffer[self.score * 4 + 3])
            self.score += 1
            i1 -= 1
            j1 -= 1
            i2 += 1
            j2 += 1

        self.board = board

    def undo_move(self):
        self.score = self.prev_scores.pop()
        self.board = self.prev_boards.pop()
        self.connections = self.prev_connections.pop()


PatternInstance = collections.namedtuple(
    'PatternInstance',
    'idxs moves')


def instantiate_pattern(p):
    result = []
    for i in range(1, n - p.y2):
        for j in range(1, n - p.x2):
            idxs = [(y + i) * n + x + j for x, y in p.points]
            moves = []
            for x, y, vert in reversed(p.actions):
                idx = (y + i) * n + x + j
                moves.append(2 * idx + int(vert))
            result.append(PatternInstance(idxs, moves))

    return result


def pattern_match(pi, board):
    i1, i2, i3, i4 = pi.idxs
    return board[i1] == board[i2] == board[i3] == board[i4]


class SquareRemover(object):
    @staticmethod
    def playIt(colors_, board, start_seed):
        global colors
        global n
        global _a

        start = default_timer()

        colors = colors_
        n = len(board)
        print>>sys.stderr, '# dict(type="size", n={}, colors={}) #'.format(n, colors)
        n += 2
        board = [9] * n + [int(c) for row in board for c in '9' + row + '9'] + [9] * n
        assert len(board) == n*n

        _a = start_seed

        random.seed(42)
        result = []
        sim = Simulator(board)

        pattern_instances = []
        for i in 1, 2, 3:
            for p in gen_patterns(i):
                pattern_instances.extend(instantiate_pattern(p))

        print>>sys.stderr, len(pattern_instances), 'pattern instances'

        while len(result) // 3 < NUM_MOVES:
            if default_timer() > start + TIME_LIMIT:
                print>>sys.stderr, 'timeout!'
                print>>sys.stderr, len(result) // 3
                break
            remaining = NUM_MOVES - len(result) // 3
            ms = None
            for pi in pattern_instances:
                if pattern_match(pi, sim.board) and remaining >= len(pi.moves):
                    ms = pi.moves
                    break
            else:
                print>>sys.stderr, 'no match', len(result) // 3
                move, _, _ = random.choice(list(enum_moves(sim.board)))
                ms = [move]

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
    global TIME_LIMIT
    if len(sys.argv) == 2:
        TIME_LIMIT = float(sys.argv[1])

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
