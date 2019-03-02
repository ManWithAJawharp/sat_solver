import os
import argparse
import time
import json
import numpy as np

from tqdm import tqdm

from solver import run

DIFFICULTY = ['simple', 'easy', 'intermediate', 'expert']


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped


def run_exp_1(strategy=1):
    results = {}
    for difficulty in DIFFICULTY:
        print(f"Difficulty: {difficulty}")
        results[difficulty] = {
            'idx': [],
            'splits': [],
            'runtime': [],
        }

        files = sorted(os.listdir(difficulty))

        for idx, file in enumerate(tqdm(files)):
            path = os.path.join(difficulty, file)

            start = time.time()
            solver = run(path, strategy=strategy, output=False, silent=True)
            end = time.time()

            results[difficulty]['idx'].append(idx)
            results[difficulty]['splits'].append(solver.splits)
            results[difficulty]['runtime'].append(end - start)

        results[difficulty]['mean_splits'] = np.mean(
            results[difficulty]['splits'])
        results[difficulty]['mean_runtime'] = np.mean(
            results[difficulty]['runtime'])

    with open(f"experiment_{strategy}.json", 'w') as file:
        json.dump(results, file)


def run_exp_2(strategy=2, repeats=10):
    results = {}
    for difficulty in DIFFICULTY:
        print(f"Difficulty: {difficulty}")
        results[difficulty] = {
            'idx': [],
            'splits': [],
            'runtime': [],
        }

        files = sorted(os.listdir(difficulty))

        for idx, file in enumerate(tqdm(files)):
            path = os.path.join(difficulty, file)

            runtimes = []
            splits = []

            for i in range(repeats):
                start = time.time()
                solver = run(path, strategy=strategy, output=False,
                             silent=True)
                end = time.time()

                runtimes.append(end - start)
                splits.append(solver.splits)

            results[difficulty]['idx'].append(idx)
            results[difficulty]['splits'].append(np.mean(splits))
            results[difficulty]['runtime'].append(np.mean(runtimes))

        results[difficulty]['mean_splits'] = np.mean(
            results[difficulty]['splits'])
        results[difficulty]['mean_runtime'] = np.mean(
            results[difficulty]['runtime'])

    with open(f"experiment_{strategy}.json", 'w') as file:
        json.dump(results, file)


def run_exp_3(strategy=3, repeats=1):
    results = {}

    try:
        for difficulty in DIFFICULTY:
            print(f"Difficulty: {difficulty}")
            results[difficulty] = {
                'idx': [],
                'flips': [],
                'restarts': [],
                'runtime': [],
            }

            files = sorted(os.listdir(difficulty))

            for idx, file in enumerate(tqdm(files)):
                path = os.path.join(difficulty, file)

                runtimes = []
                flips = []
                restarts = []

                for i in range(repeats):
                    start = time.time()
                    solver = run(path, strategy=strategy, output=False,
                                 silent=True)
                    end = time.time()

                    runtimes.append(end - start)
                    flips.append(solver.flips)
                    restarts.append(solver.restarts)

                results[difficulty]['idx'].append(idx)
                results[difficulty]['flips'].append(np.mean(flips))
                results[difficulty]['restarts'].append(np.mean(restarts))
                results[difficulty]['runtime'].append(np.mean(runtimes))

            results[difficulty]['mean_splits'] = np.mean(
                results[difficulty]['flips'])
            results[difficulty]['mean_runtime'] = np.mean(
                results[difficulty]['runtime'])
    except KeyboardInterrupt:
        pass

    with open(f"experiment_5.json", 'w') as file:
        json.dump(results, file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the report experiments")
    parser.add_argument(metavar='E', dest='experiment', type=int,
                        help="The experiment to run.")
    args = parser.parse_args()

    if args.experiment is 1:
        print("Naive DPLL")
        run_exp_1(args.experiment)
    elif args.experiment is 2:
        print("DPLL with random split")
        run_exp_2(args.experiment)
    elif args.experiment is 3:
        print("WalkSAT")
        run_exp_3(args.experiment)
