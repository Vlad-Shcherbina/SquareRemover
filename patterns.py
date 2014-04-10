from copy import deepcopy
import collections



class Pattern(object):
    def __init__(self):
        self.points = {(0, 0), (0, 1), (1, 0), (1, 1)}
        self.affected = set()
        self.x1 = 0
        self.y1 = 0
        self.x2 = 2
        self.y2 = 2
        self.actions = []

    def move(self, x, y, vert):
        if self.actions and self.actions[-1] == (x, y, vert):
            return False
        if vert:
            x2 = x
            y2 = y + 1
        else:
            x2 = x + 1
            y2 = y
        if (x, y) in self.points:
            if (x2, y2) in self.points:
                return False
            self.points.remove((x, y))
            self.points.add((x2, y2))
        else:
            if (x2, y2) not in self.points:
                return False
            self.points.add((x, y))
            self.points.remove((x2, y2))

        self.affected.add((x, y))
        self.affected.add((x2, y2))

        self.x1 = min(self.x1, x, x2)
        self.x2 = max(self.x2, x + 1, x2 + 1)
        self.y1 = min(self.y1, y, y2)
        self.y2 = max(self.y2, y + 1, y2 + 1)
        self.actions.append((x, y, vert))
        return True

    def normalize(self):
        self.points = {(x - self.x1, y - self.y1) for x, y in self.points}
        self.affected = {(x - self.x1, y - self.y1) for x, y in self.affected}
        self.actions = [
            (x - self.x1, y - self.y1, vert) for x, y, vert in self.actions]
        self.x2 -= self.x1
        self.y2 -= self.y1
        self.x1 = 0
        self.y1 = 0

    def __str__(self):
        result = ''
        for y in range(self.y1, self.y2):
            for x in range(self.x1, self.x2):
                if (x, y) in self.points:
                    result += '* '
                elif (x, y) in self.affected:
                    result += '~ '
                else:
                    result += '. '
            result += '\n'
        result += repr(self.actions)
        return result

    def enum_moves(self):
        for x, y in self.points:
            yield x, y, False
            yield x, y, True
            yield x - 1, y, False
            yield x, y - 1, True


def gen_patterns(depth):
    patterns_by_points = {}
    def rec(depth, p):
        p = deepcopy(p)
        if depth == 0:
            p.normalize()
            k = frozenset(p.points), frozenset(p.affected)
            patterns_by_points[k] = p
            return

        for move in p.enum_moves():
            p2 = deepcopy(p)
            if p2.move(*move):
                rec(depth-1, p2)

    rec(depth, Pattern())
    return patterns_by_points.values()


if __name__ == '__main__':
    patterns = gen_patterns(4)
    for p in patterns:
        print p
        print '-' * 10
    print len(patterns), 'patterns)'
