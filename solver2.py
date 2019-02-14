import copy
import random

from sudoku import load_example, draw_assignment


def create_clauses(*clauses):
    return {idx: clause for idx, clause in enumerate(clauses)}


def add_assignment(assignment, literal, value):
    if literal < 0:
        literal = abs(literal)
        value = not value

    assignment[literal] = value

    return assignment


def del_assignment(assignment, literal):
    del assignment[abs(literal)]
    return assignment


def get_assignment(assignment, literal):
    value = assignment[abs(literal)]

    if literal < 0:
        return not value
    else:
        return value


def assign_literal(clauses, solved, assignment, literal):
    value = get_assignment(assignment, literal)

    for idx in list(clauses.keys()):
        clause = clauses[idx]

        if literal in clause:
            if value:
                solved[idx] = clauses[idx]
                del clauses[idx]
            else:
                clauses[idx].remove(literal)
        elif -literal in clause:
            if not value:
                solved[idx] = clauses[idx]
                del clauses[idx]
            else:
                clauses[idx].remove(-literal)

    return clauses, solved


def remove_tautologies(clauses, solved):
    for idx in list(clauses.keys()):
        clause = clauses[idx]
        for literal in clause:
            if -literal in clause:
                solved[idx] = clause
                del clauses[idx]
                break

    return clauses


def detect_pure(clauses):
    variables = set()
    for idx in list(clauses.keys()):
        variables = variables | clauses[idx]

    for variable in variables:
        if -variable not in variables:
            yield variable


def assign_pure_literals(clauses, solved, assignment):
    for literal in detect_pure(clauses):
        assignment = add_assignment(assignment, literal, value=True)
        clauses, solved = assign_literal(
            clauses, solved, assignment, literal)

    return clauses, solved, assignment


def unit_propagate(clauses, solved, assignment):
    for idx in list(clauses.keys()):
        clause = clauses[idx]
        if len(clauses) is 1:
            literal = list(clause)[0]

            assignment = add_assignment(assignment, literal, value=True)
            clauses, solved = assign_literal(
                clauses, solved, assignment, literal)

    return clauses, solved, assignment


def choose_literal(clauses):
    variables = set()
    for idx in list(clauses.keys()):
        variables = variables | clauses[idx]

    # TODO: Count positive
    # TODO: Count negeative

    return random.choice(list(variables)), True


def split(clauses, solved, assignment):
    literal, value = choose_literal(clauses)

    assignment = add_assignment(assignment, literal, value)
    clauses_, solved_ = assign_literal(
        copy.deepcopy(clauses),
        copy.deepcopy(solved),
        assignment, literal)
    satisfied, assignment_ = dll(clauses_, solved_, copy.deepcopy(assignment))

    if satisfied:
        return satisfied, assignment_

    assignment = del_assignment(assignment, literal)
    assignment = add_assignment(assignment, literal, not value)
    clauses, solved = assign_literal(
        clauses, solved, assignment, literal)

    return dll(clauses, solved, assignment)


def dll(clauses, solved, assignment, tautologies=False):
    print(f"Clauses: {len(clauses)}")
    if len(clauses) is 0:
        print("Empty set")
        return True, assignment

    for idx in clauses.keys():
        if len(clauses[idx]) is 0:
            return False, assignment

    if tautologies:
        clauses = remove_tautologies(clauses, solved)

    clauses, solved, assignment = unit_propagate(clauses, solved, assignment)

    clauses, solved, assignment = assign_pure_literals(
        clauses, solved, assignment)

    if len(clauses) is 0:
        print("Empty set")
        return True, assignment

    return split(clauses, solved, assignment)


clauses = create_clauses({1, -2}, {2, 3}, {-3, 1}, {-1, 2, 3, 1})
print(dll(clauses, {}, {}, True))
print()

clauses = create_clauses({1, -3}, {1, -2, 3}, {2, 3, -1}, {-3, -1, 2})
print(dll(clauses, {}, {}, True))
print()

example = load_example()
example = create_clauses(*example)
satisfied, assignment = dll(example, {}, {}, True)
print(draw_assignment(assignment))
print(satisfied)
