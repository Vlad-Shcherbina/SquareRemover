import os
import re
import subprocess
import collections
from timeit import default_timer
import multiprocessing
import pprint


RunResult = collections.namedtuple(
    'RunResult',
    'score n colors data_points time')


def run_solution(command, seed):
    try:
        start = default_timer()
        p = subprocess.Popen(
            'java -jar SquareRemoverVis.jar -exec "{}" '
            '-novis -seed {}'.format(command, seed),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = p.communicate()
        out = out.decode('ascii')

        p.wait()
        assert p.returncode == 0

        score = None
        data_points = []
        colors = None
        n = None
        for line in out.splitlines():
            m = re.match(r'Score  = (\d+)$', line)
            if m is not None:
                score = int(m.group(1))
            m = re.match(r'# (.*) #$', line)
            if m is not None:
                dp = eval(m.group(1))
                data_points.append(dp)
                if dp.get('type') == 'size':
                    colors = dp['colors']
                    n = dp['n']

        assert score is not None, '\n' + out

        return RunResult(score, n, colors, data_points, default_timer() - start)
    except Exception as e:
        raise Exception('seed={}, out={}'.format(seed, out)) from e


def grouping_task(seed):
    sol = run_solution('python3 -u trivial.py', seed)
    return seed, sol.n, sol.colors


def main():
    pool = multiprocessing.Pool(6)
    by_problem_type = {
        (n, colors):[] for n in range(8, 16 + 1) for colors in (4, 5, 6)}
    for seed, n, colors in pool.imap_unordered(grouping_task, range(1, 2000)):
        by_problem_type[n, colors].append(seed)
        print(seed, n, colors)

    #pprint.pprint(by_problem_type)
    with open('by_problem_type.txt', 'w') as fout:
        pprint.pprint(by_problem_type, width=1000, stream=fout)
    shortest = min(map(len, by_problem_type.values()))
    print('shortest', shortest)


if __name__ == '__main__':
    main()
