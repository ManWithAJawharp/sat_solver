import random

from copy import deepcopy

from sudoku import load_example, load_games, draw_assignment


def create_clauses(*clauses):
    """
    Convert a set of clauses to a dictionary.
    """
    return {idx: clause for idx, clause in enumerate(clauses)}


def unit_propagate(clauses, literal):
    global assignment

    if literal < 0:
        value = not assignment[abs(literal)]
    else:
        value = assignment[literal]

    for idx in list(clauses.keys()):
        clause = clauses[idx]

        if literal in clause:
            if value:
                del clauses[idx]
            else:
                clause.remove(literal)
        elif -literal in clause:
            if not value:
                del clauses[idx]
            else:
                clause.remove(-literal)

    return clauses


def add_assignment(literal, value):
    global assignment

    if literal < 0:
        literal = abs(literal)
        value = not value

    assignment[literal] = value


def get_variables(clauses):
    variables = set()
    for idx in clauses.keys():
        variables = variables | clauses[idx]

    return variables


def dpll(clauses):
    global assignment

    # print(len(clauses))
    # print(get_variables(clauses))

    if len(clauses) is 0:
        return True

    for idx in clauses:
        if len(clauses[idx]) is 0:
            return False

    # Unit propagation.
    for idx in clauses:
        clause = clauses[idx]

        if len(clause) is 1:
            literal = list(clause)[0]
            add_assignment(literal, True)

            clauses_simplified = unit_propagate(deepcopy(clauses), literal)
            return dpll(clauses_simplified)

    # Split.
    literal = random.choice(list(get_variables(clauses)))
    assignment_ = deepcopy(assignment)
    add_assignment(literal, True)

    clauses_simplified = unit_propagate(deepcopy(clauses), literal)
    satisfied = dpll(clauses_simplified)

    if satisfied:
        return True

    assignment = assignment_
    add_assignment(literal, False)

    return dpll(unit_propagate(clauses, literal))


if __name__ == "__main__":
    assignment = {}

    clauses = create_clauses({1, -2}, {2, 3}, {-3, 1}, {-1, 2, 3, 1})
    print(dpll(clauses))
    print(assignment)
    assignment = {}

    clauses = create_clauses({5}, {1, -3}, {1, -2, 3}, {2, 3, -1}, {-3, -1, 2})
    print(dpll(clauses))
    print(assignment)
    assignment = {}

    example = load_example()
    example = create_clauses(*example)
    satisfied = dpll(example)
    print(draw_assignment(assignment))
    print(satisfied)
    assignment = {}

    for game in load_games():
        clauses = create_clauses(*game)
        satisfied = dpll(clauses)
        print(draw_assignment(assignment))
        assignment = {}
