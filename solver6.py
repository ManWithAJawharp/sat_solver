clauses = {}
assignment = {}
contain = {}  # All clauses that contain a certain literal.


def create_clauses(*clauses):
    clauses = {idx: clause for idx, clause in enumerate(clauses)}


def add_assignment(literal, value):
    global assignment

    if literal < 0:
        literal = abs(literal)
        value = not value

    assignment[literal] = value


def del_assignment(literal):
    global assignment

    del assignment[abs(literal)]


def get_assignment(literal):
    global assignment

    value = assignment[abs(literal)]

    if literal < 0:
        return not value
    else:
        return value


def assign_literal(literal):
    value = get_assignment(literal)


clauses = create_clauses()
