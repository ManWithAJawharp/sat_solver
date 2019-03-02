import json
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

DIFFICULTY = ['simple', 'easy', 'intermediate', 'expert']


def find_rank(data, correct=False):
    m = len(data)

    # Test whether any two samples are from the same distribution.
    p_values = np.zeros(m - 1)

    for idx in range(m - 1):
        try:
            U, p = stats.mannwhitneyu(data[idx], data[idx + 1], correct,
                                      'less')
            p_values[idx] = p
        except ValueError:
            continue

    # Test whether all samples are from the same distribution.
    f, p = stats.kruskal(*data)

    # Compute the correlation of the sample means and the difficulty scale.
    rho, rho_p = stats.pearsonr(np.arange(len(data)), np.mean(data, 1))

    return p_values, p, rho, rho_p


def anaylze_experiment(experiment):
    experiment = "experiment_2.json"
    print(experiment)
    with open(experiment) as file:
        data = json.load(file)

    runtimes = []
    splits = []

    for difficulty in DIFFICULTY:
        runtimes.append(data[difficulty]['runtime'])
        splits.append(data[difficulty]['splits'])

    p_values, p, rho, rho_p = find_rank(runtimes)
    print("Run times", p_values, p, rho, rho_p)

    '''
    plt.figure()
    plt.suptitle("Runtime")
    plt.bar(DIFFICULTY, np.mean(runtimes, 1))

    plt.xlabel("Difficulty level")
    plt.ylabel("Seconds")
    plt.show()
    '''

    p_values, p, rho, rho_p = find_rank(splits, True)
    print("Splits: ", p_values, p, rho, rho_p)

    '''
    plt.figure()
    plt.suptitle("Splits")
    plt.bar(DIFFICULTY, np.mean(splits, 1))

    plt.xlabel("Difficulty level")
    plt.ylabel("n")
    plt.show()
    '''

    return np.mean(runtimes, 1), np.mean(splits, 1)


def anaylze_walksat():
    with open("experiment_3.json") as file:
        data1 = json.load(file)

    with open("experiment_4.json") as file:
        data2 = json.load(file)

    runtimes = []
    flips = []
    restarts = []

    for difficulty in DIFFICULTY:
        runtimes.append(data1[difficulty]['runtime'] +
                        data2[difficulty]['runtime'])
        flips.append(data1[difficulty]['flips'] +
                     data2[difficulty]['flips'])
        restarts.append(data1[difficulty]['restarts'] +
                        data2[difficulty]['restarts'])

    p_values, p, rho, rho_p = find_rank(runtimes)
    print("Run times", p_values, p, rho, rho_p)

    '''
    plt.figure()
    plt.suptitle("Runtime")
    plt.bar(DIFFICULTY, np.mean(runtimes, 1))

    plt.xlabel("Difficulty level")
    plt.ylabel("Seconds")
    plt.show()
    '''

    p_values, p, rho, rho_p = find_rank(flips, True)
    print("Flips: ", p_values, p, rho, rho_p)

    '''
    plt.figure()
    plt.suptitle("Splits")
    plt.bar(DIFFICULTY, np.mean(flips, 1))

    plt.xlabel("Difficulty level")
    plt.ylabel("n")
    plt.show()
    '''

    p_values, p, rho, rho_p = find_rank(restarts, True)
    print("Restarts: ", p_values, p, rho, rho_p)

    '''
    plt.figure()
    plt.suptitle("Splits")
    plt.bar(DIFFICULTY, np.mean(restarts, 1))

    plt.xlabel("Difficulty level")
    plt.ylabel("n")
    plt.show()
    '''

    return np.mean(runtimes, 1), np.mean(flips, 1), np.mean(restarts, 1)


if __name__ == "__main__":
    runtime1, splits1 = anaylze_experiment("experiment_1.json")
    runtime2, splits2 = anaylze_experiment("experiment_2.json")
    runtime3, flips, restarts = anaylze_walksat()

    # Runtimes
    plt.figure()
    plt.subplot(131)
    plt.title("Basic DP")
    plt.bar(DIFFICULTY, runtime1)
    plt.xticks(DIFFICULTY, DIFFICULTY, rotation=30)
    plt.ylabel("Time (s)")

    plt.subplot(132)
    plt.title("Random Split DP")
    plt.bar(DIFFICULTY, runtime2)
    plt.xticks(DIFFICULTY, DIFFICULTY, rotation=30)

    plt.subplot(133)
    plt.title("WalkSAT")
    plt.bar(DIFFICULTY, runtime3)
    plt.xticks(DIFFICULTY, DIFFICULTY, rotation=30)

    plt.tight_layout()
    plt.show()

    # Splits/flips
    plt.figure()
    plt.subplot(131)
    plt.title("Basic DP")
    plt.bar(DIFFICULTY, splits1)
    plt.xticks(DIFFICULTY, DIFFICULTY, rotation=30)
    plt.ylabel("Splits/flips")

    plt.subplot(132)
    plt.title("Random Split DP")
    plt.bar(DIFFICULTY, splits2)
    plt.xticks(DIFFICULTY, DIFFICULTY, rotation=30)

    plt.subplot(133)
    plt.title("WalkSAT")
    plt.bar(DIFFICULTY, flips)
    plt.bar(DIFFICULTY, restarts)
    plt.xticks(DIFFICULTY, DIFFICULTY, rotation=30)

    plt.tight_layout()
    plt.show()
