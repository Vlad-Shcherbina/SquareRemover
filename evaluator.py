import sys
import multiprocessing

import runner
import run_db


def worker(task):
    return runner.run_solution(*task)


def main():
    assert len(sys.argv) == 2
    command = sys.argv[1]

    with open('by_problem_type.txt') as fin:
        by_problem_type = eval(fin.read())

    types = [(n, colors) for colors in (4, 5, 6) for n in range(8, 16 + 1)]

    tasks = [(command, by_problem_type[t][i]) for i in range(3) for t in types]

    map = multiprocessing.Pool(5).imap

    with run_db.RunRecorder() as run:
        for result in map(worker, tasks):
            print(result['colors'], result['n'], result['score'])
            run.add_result(result)
            run.save()


if __name__ == '__main__':
    main()
