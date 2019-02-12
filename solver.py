import random

from sudoku import load_example, draw_assignment


def remove_tautologies(clauses):
    new_clauses = []
    for clause in clauses:
        for variable in clause:
            if -variable in clause:
                # Clause contains `P v -P`
                break
            else:
                new_clauses.append(clause)
                break

    return new_clauses


def remove_unit_clauses(clauses, assignment):
    """
    Clear out all unit clauses in a set, removing any redundant clauses
    as a result.
    """
    new_clauses = clauses

    for clause in new_clauses:
        if len(clause) is 1:
            literal = list(clause)[0]
            assignment[literal] = True

            new_clauses = set_literal(clauses, assignment, literal)

    return new_clauses, assignment


def remove_literal(clauses, literal):
    """
    Remove a literal from a set of clauses.
    """
    new_clauses = []

    for clause in clauses:
        new_clauses.append(clause - {literal})

    return new_clauses


def set_literal(clauses, assignment, literal):
    """
    Update the set of clauses given the value of a single literal.
    """
    value = assignment[literal]

    new_clauses = []

    for clause in clauses:
        if literal in clause:
            if not value:
                new_clauses.append(clause - set([literal]))
        else:
            new_clauses.append(clause)

    return new_clauses


def detect_pure_literals(clauses, shuffle=True):
    """
    Find all pure literals.
    """
    variables = set()
    for clause in clauses:
        variables = variables | clause

    if shuffle:
        random.shuffle(list(variables))
        variables = set(variables)

    for variable in variables:
        if -variable not in variables:
            # Pure literal detected.
            yield variable


def count_positive(clauses, literal):
    """
    Count the number of times a literal appears as positive.
    """
    count = 0

    for clause in clauses:
        if literal in clause:
            count += 1

    return count


def count_negative(clauses, literal):
    """
    Count the number of times a literal appears as negative.
    """
    count = 0

    for clause in clauses:
        if -literal in clause:
            count += 1

    return count


def davis_putnam(clauses, assignment, check_tautology=False):
    print(f"\rclauses: {len(clauses)} | assignment: {len(assignment)}")

    # Check if set of clauses is empty and therefore satisfied.
    if len(clauses) is 0:
        print("Set of clauses is empty.")
        return True, assignment

    # Check is set of clauses contains the empty clause.
    for clause in clauses:
        if len(clause) is 0:
            print("Set of clauses contains empty clause.")
            return False, assignment

    # Check for tautologies and remove them.
    if check_tautology:
        clauses_no_taut = remove_tautologies(clauses)
        if clauses != clauses_no_taut:
            print("Removed tautologies")
            return davis_putnam(clauses_no_taut, assignment)

    # Check for unit clauses.
    clauses_no_units, assignment = remove_unit_clauses(clauses, assignment)
    if clauses != clauses_no_units:
        print("Found unit clauses")
        return davis_putnam(clauses_no_units, assignment)

    '''
    # Split at pure literals.
    for pure_literal in detect_pure_literals(clauses):
        print(f"Set {pure_literal} to True")
        assignment[pure_literal] = True

        clauses_no_pure = set_literal(
            clauses, assignment, pure_literal)
        satisfied, assignment_ = davis_putnam(clauses_no_pure, assignment)

        if satisfied:
            return satisfied, assignment_
        else:
            print(f"Set {pure_literal} to False")
            assignment[pure_literal] = False

            clauses_no_pure = set_literal(
                clauses, assignment, pure_literal)
            return davis_putnam(clauses_no_pure, assignment)
    '''

    # Perform random split.
    variables = set()
    for clause in clauses:
        variables = variables | clause

    cp = {literal: count_positive(clauses, literal) for literal in variables}
    cn = {literal: count_negative(clauses, literal) for literal in variables}

    return False, assignment


if __name__ == "__main__":
    clauses = [{1, -2}, {2, 3}, {-3, 1}]
    print(davis_putnam(clauses, {}, check_tautology=True))

    clauses = [{1, -3}, {1, -2, 3}, {2, 3, -1}, {-3, -1, 2}]
    print(davis_putnam(clauses, {}, check_tautology=True))

    '''
    example = load_example()
    print(len(example))

    try:
        satisfied, assignment = davis_putnam(example, {})
    except RecursionError:
        pass
    '''
