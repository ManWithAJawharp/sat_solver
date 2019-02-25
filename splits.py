"""
Splitting methods and heuristics for the David Putnam solver.

Each method takes a Solver instance as argument and returns a literal
and the value to set it to.
"""
import random


def naive_split(solver):
    """
    Simply pick the first variable that comes up and set it to True.
    """
    variables = [key for key, value in solver.containment.items()
                 if len(value) > 0]
    literal = variables[-1]
    value = True

    return literal, value


def random_split(solver):
    """
    Pick a random literal and set it either to True or False.
    """
    variables = [key for key, value in solver.containment.items()
                 if len(value) > 0]
    literal = random.choice(variables)
    # value = random.choice([True, False])
    value = True

    return literal, value


def max_occurrence(solver):
    occurrences = {}

    for clause in solver.clauses.values():
        for literal in clause:
            if literal not in occurrences:
                occurrences[literal] = 1
            else:
                occurrences[literal] += 1

    literal = max(occurrences, key=lambda key: occurrences[key])

    value = occurrences[abs(literal)] < occurrences[-abs(literal)]

    return abs(literal), value


def jeroslow_lang(solver):
    clauses = solver.clauses

    j_values = {}

    for literal, indices in solver.containment.items():
        J = 0
        for idx in indices:
            if idx not in clauses:
                continue

            J += 2 ** -len(clauses[idx])

        # print(J)
        j_values[literal] = J

    literal = max(
        j_values, key=lambda key: j_values[key] + j_values[-key])

    value = j_values[literal] < j_values[-literal]

    return literal, value
