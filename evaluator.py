import multiprocessing
import runner
import pickle


def worker(task):
    return runner.run_solution(*task)

def main():
    with open('by_problem_type.txt') as fin:
        by_problem_type = eval(fin.read())

    types = [(n, colors) for colors in (4, 5, 6) for n in range(8, 16 + 1)]
    #types.reverse()

    command = 'python -u sol.py 11.0'
    tasks = [(command, by_problem_type[t][0]) for t in types]

    map = multiprocessing.Pool(6).imap

    results = []
    for result in map(worker, tasks):
        print(result.colors, result.n, result.score)
        results.append(result)

    with open('results.pickle', 'wb') as fout:
        pickle.dump(results, fout)

    with open('results.pickle', 'rb') as fin:
        results = pickle.load(fin)

    sum_score = sum(result.score for result in results)
    print('average score: {:.3f}'.format(sum_score / len(results)))


if __name__ == '__main__':
    main()