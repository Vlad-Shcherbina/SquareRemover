from __future__ import print_function
import sys

if __name__ == '__main__':
    colors = int(input())
    n = int(input())
    for i in range(n):
        input()

    start_seed = int(input())

    print('# dict(type="size", n={}, colors={}) #'.format(n, colors), file=sys.stderr)

    for _ in range(30000):
        print(1)
