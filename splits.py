import random


def naive_split(solver):
    """
    Simply pick the first variable that comes up and set it to True.
    """
    variables = [key for key, value in solver.containment.items()
                 if len(value) > 0]
    literal = list(variable)[0]
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
