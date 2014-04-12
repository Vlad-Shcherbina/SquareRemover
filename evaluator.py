import sys
import multiprocessing
import runner
import pickle
from math import sqrt
import collections


def worker(task):
    return runner.run_solution(*task)


def list_stats(xs):
    xs = list(xs)
    if not xs:
        return 'empty'
    if len(xs) == 1:
        return str(xs[0])
    sx = sum(xs)
    sx2 = sum(x * x for x in xs)
    ave = 1.0 * sx / len(xs)
    sigma = sqrt((sx2 - 2 * sx * ave + len(xs) * ave * ave) / (len(xs) - 1))
    return '<span title="{}..{}">{:.3f} &plusmn; <i>{:.3f}</i></span>'.format(
        min(xs), max(xs), ave, sigma)


def main():
    assert len(sys.argv) == 2
    command = sys.argv[1]

    with open('by_problem_type.txt') as fin:
        by_problem_type = eval(fin.read())

    types = [(n, colors) for colors in (4, 5, 6) for n in range(8, 16 + 1)]

    tasks = [(command, by_problem_type[t][i]) for t in types for i in range(2)]

    map = multiprocessing.Pool(5).imap

    results = []
    for result in map(worker, tasks):
        print(result.colors, result.n, result.score)
        results.append(result)

    with open('results.pickle', 'wb') as fout:
        pickle.dump(results, fout)

    with open('results.pickle', 'rb') as fin:
        results = pickle.load(fin)

    with open('stats.html', 'w') as fout:
        fout.write('<table>')
        fout.write('<tr> <th></th>')
        for colors in None, 4, 5, 6:
            fout.write('<th>colors = {}</th>'.format(colors or '*'))
        fout.write('</tr>')
        for n in [None] + list(range(8, 16 + 1)):
            fout.write('<tr>')
            fout.write('<th>n = {}</th>'.format(n or '*'))
            for colors in None, 4, 5, 6:
                fout.write('<td align="right">')

                scores = []
                values = collections.defaultdict(list)
                for result in results:
                    if n and n != result.n:
                        continue
                    if colors and colors != result.colors:
                        continue
                    for dp in result.data_points:
                        for k, v in dp.items():
                            if k != 'type':
                                values[k].append(v)
                    scores.append(result.score)
                fout.write('<b>score = {}</b>'.format(list_stats(scores)))
                for k, xs in sorted(values.items()):
                    fout.write('<br>{} = {}'.format(k, list_stats(xs)))

                fout.write('</td>')
            fout.write('</tr>')
        fout.write('</table>')

    print('score:', list_stats(result.score for result in results))


if __name__ == '__main__':
    main()
