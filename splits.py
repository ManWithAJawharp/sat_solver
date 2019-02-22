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
    literal = variables[0]
    value = True

    return literal, value


def random_split(solver):
    """
    Pick a random literal and set it either to True or False.
    """
    variables = [key for key, value in solver.containment.items()
                 if len(value) > 0]
    literal = random.choice(variables)
    value = random.choice([True, False])

    return literal, value


def jeroslow_lang(solver):
    clauses = solver.clauses

    j_values = {}

    for literal, indices in solver.containment.items():
        print(literal, indices)
        J = sum([2 ** -len(clauses[idx]) for idx in indices])
        print(J)

        j_values[literal] = J
