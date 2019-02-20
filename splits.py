import random


def naive_split(solver):
    """
    Simply pick the first variable that comes up and set it to True.
    """
    literal = list(solver.get_variables())[0]
    value = True

    return literal, value


def random_split(solver):
    """
    Pick a random literal and set it either to True or False.
    """
    literal = random.choice(list(solver.get_variables()))
    value = random.choice([True, False])

    return literal, value
