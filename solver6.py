import random

from tqdm import tqdm

from sudoku import load_games, load_example, draw_assignment

RC = 0  # 'Remove Clause'
RL = 1  # 'Remove Literal'
AA = 2  # 'Add Assignment'
AC = 3  # 'Add Clause'

clauses = {}
change_log = [[]]
assignment = {}
contain = {}  # All clauses that contain a certain literal.


def create_clauses(*clauses):
    """
    Convert a list of clauses to a dictionary where each entry's key
    is the clause's index.
    """
    clauses = {idx: clause for idx, clause in enumerate(clauses)}

    return clauses


def add_assignment(literal, value):
    """
    Add an assignment
    """
    global assignment

    if literal < 0:
        literal = abs(literal)
        value = not value

    assignment[literal] = value

    change_log[-1].append((AA, literal, literal))


def get_assignment(literal):
    global assignment

    value = assignment[abs(literal)]

    if literal < 0:
        return not value
    else:
        return value


def delete_clause(idx):
    global clauses, change_log

    clause = clauses[idx]

    change_log[-1].append((RC, idx, clause))
    del clauses[idx]


def delete_literal(idx, literal):
    global clauses, change_log

    clauses[idx].remove(literal)
    change_log[-1].append((RL, idx, literal))


def assign_literal(literal):
    global clauses

    # print(clauses)

    value = get_assignment(literal)

    for idx in list(clauses.keys()):
        clause = clauses[idx]

        if literal in clause:
            if value:
                delete_clause(idx)
            else:
                delete_literal(idx, literal)
        elif -literal in clause:
            if not value:
                delete_clause(idx)
            else:
                delete_literal(idx, -literal)


def restore():
    global clauses, change_log

    # print("Restoring")

    log_entry = change_log.pop()

    while len(log_entry) > 0:
        action, idx, content = log_entry.pop()

        if action is RC:
            clauses[idx] = content
        elif action is RL:
            clauses[idx].add(content)
        elif action is AA:
            del assignment[abs(content)]
        else:
            print("Cannot restore, action not recognized.")
            print(f"({action}, {idx}, {content}")


def remove_tautologies():
    global clauses

    for idx in list(clauses.keys()):
        clause = clauses[idx]

        for literal in clause:
            if -literal in clause:
                delete_clause(idx)
                break


def unit_propagate():
    global clauses

    for idx in list(clauses.keys()):
        clause = clauses[idx]

        if len(clause) is 1:
            literal = list(clause)[0]

            add_assignment(literal, value=True)
            assign_literal(literal)

            return dpll()


def get_variables():
    global variables

    variables = set()

    for idx in clauses:
        variables = variables | clauses[idx]

    return variables


def dpll():
    global clauses, change_log, assignment

    # print(len(clauses))

    if len(clauses) is 0:
        # Set of clauses is empty.
        return True

    for idx in clauses:
        if len(clauses[idx]) is 0:
            # Set of clauses contains an empty clause.
            # print(f"Found empty clause: {idx}: {clauses[idx]}")
            return False

    for idx in list(clauses.keys()):
        clause = clauses[idx]

        if len(clause) is 1:
            # print(f"Found unit clause {clause}")
            literal = list(clause)[0]

            add_assignment(literal, value=True)
            assign_literal(literal)

            return dpll()

    literal = random.choice(list(get_variables()))

    change_log.append([])

    # print(f"Set {literal} to True")
    add_assignment(literal, True)
    assign_literal(literal)

    satisfied = dpll()

    if satisfied:
        return True

    restore()
    change_log.append([])

    # print(f"Set {literal} to False")
    add_assignment(literal, False)

    return dpll()


# clauses = create_clauses({1, -2}, {2, 3}, {-3, 1}, {-1, 2, 3, 1})

example = load_example()
clauses = create_clauses(*example)

try:
    satisfied = dpll()
except RecursionError:
    satisfied = False

print(satisfied)
print(draw_assignment(assignment))

successes = []
for idx, game in tqdm(enumerate(load_games())):
    clauses = create_clauses(*game)
    change_log = [[]]
    assignment = {}
    contain = {}  # All clauses that contain a certain literal.

    try:
        satisfied = dpll()
    except RecursionError:
        print("Uh oh")
        state = 'recursion_error'
    else:
        if satisfied:
            state = 'success'
        else:
            state = 'failure'

    successes.append(state)

    if idx > 100:
        break

success_rate = sum([state == 'success' for state in successes]) / (idx + 1)
failure_rate = sum([state == 'failure' for satisfied in successes]) / (idx + 1)

print(f"Success rate: {success_rate * 100:0.1f}% | "
      f"Failure rate: {failure_rate * 100:0.1f}%")
