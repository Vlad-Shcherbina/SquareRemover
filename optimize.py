import sys
import multiprocessing
import random
import traceback

import runner
import run_db


def worker(task):
    return runner.run_solution(*task)


class Optimizer(object):
    def __init__(self, command, seeds, pool):
        self.command = command
        self.seeds = seeds
        self.pool = pool
        self.cache = {}

    def measure(self, arg):
        assert arg not in self.cache
        #cmd = '{} {}'.format(self.command, arg)
        cmd = ' '.join([self.command] + list(map(str, arg)))
        tasks = [(cmd, seed) for seed in self.seeds]

        try:
            s = 0.0
            for result in self.pool.imap(worker, tasks):
                s += result['score']
        except:
            traceback.print_exc()
            return -1

        result = s / len(self.seeds)
        self.cache[arg] = result
        return result

    def pick_arg(self):
        if self.cache:
            best = max(self.cache, key=self.cache.get)
        else:
            best = (2.0, 0.15)
        while True:
            a = (random.randrange(int(1.5 * 16), int(3.5) * 16 + 1) / 16.0,
                 random.randrange(16) / 32.0)
            if a in self.cache:
                continue
            if random.random() * (
                abs(a[0] - best[0]) +
                abs(a[1] - best[1])
                ) < 0.01:
                return a


def main():
    random.seed(42)
    assert len(sys.argv) == 2
    command = sys.argv[1]

    with open('by_problem_type.txt') as fin:
        by_problem_type = eval(fin.read())


    pool = multiprocessing.Pool(5)

    opts = []
    for n in range(8, 16 + 1):
        for colors in range(4, 6 + 1):
            seeds = by_problem_type[n, colors][10:20]
            opt = Optimizer(command, seeds, pool)
            opts.append(opt)

    for stage in range(1000):
        print('stage', stage)
        for opt in opts:
            a = opt.pick_arg()
            print('    ', a, opt.measure(a))

        print('optimal:')
        for idx in range(2):
            for i in range(0, len(opts), 3):
                for opt in opts[i:i + 3]:
                    if opt.cache:
                        print(max(opt.cache, key=opt.cache.get)[idx], end=', ')
                    else:
                        print('??', end=', ')
                print()
            print('---')


if __name__ == '__main__':
    main()
