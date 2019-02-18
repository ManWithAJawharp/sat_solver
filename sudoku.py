from copy import deepcopy

EXAMPLE_PATH = 'example.txt'
RULES_PATH = 'sudoku_rules.txt'
SUDOKU_PATH = '1000_sudokus.txt'


def load_raw_sudokus(path):
    """
    Generates raw encoded sudokus.
    """
    with open(path) as text:
        for line in text:
            yield line.strip()


def read_raw_sudoku(raw):
    """
    Convert a raw sudoku to a list of clauses.

    Parameters
    ----------
    raw : str
        A raw sudoku game. Consists of a single string where dots represent
        empty spaces.

    Returns
    -------
    list of set
        A list of clauses. Each clause is a set of variables.
    """
    clauses = []

    for idx, element in enumerate(raw):
        row = idx // 9 + 1
        col = idx % 9 + 1

        if element in '123456789':
            clauses.append({int(f"{row}{col}{element}")})

    return sorted(clauses)


def load_dimacs(path):
    """
    Load a DIMACS CNF format file.

    Returns
    -------
    list of set
        A list of clauses. Each clause is a set of variables.
    """
    clauses = []

    with open(path) as text:
        for line in text:
            if 'p' in line:
                continue

            line = line.strip("0 \n")

            variables = line.split()
            clause = {int(variable) for variable in variables}

            clauses.append(clause)

    return sorted(clauses)


def load_games(example=False):
    """
    Load sudoku games as lists of clauses from raw puzzles and the ruleset.

    Yields
    ------
    list of set
        A list of clauses. Each clause is a set of variables.
    """
    rules = load_dimacs(RULES_PATH)

    if example:
        example = load_dimacs(EXAMPLE_PATH)

        yield deepcopy(example + rules)

    for raw in load_raw_sudokus(SUDOKU_PATH):

        yield deepcopy(read_raw_sudoku(raw) + rules)


def load_example():
    """
    Load just the example with the sudoku ruleset.

    Returns
    -------
    list of set
        A list of clauses. Each clause is a set of variables.
    """
    for game in load_games(True):
        break

    return game


def draw_assignment(assignment):
    board = [['.' for col in range(9)] for row in range(9)]

    for key, value in assignment.items():
        if value:
            key = str(key)
            row, col, number = key
            row, col = int(row) - 1, int(col) - 1

            board[row][col] = number

    for idx, row in enumerate(board):
        for jdx, col in enumerate(row):
            if col == '.':
                literals = {str(-idx) + str(jdx) + str(i+1) for i in range(9)}

                for key, value in assignment.items():
                    if key in literals:
                        if value:
                            print(str(abs(key)))
                            literals.remove(str(abs(key)))
                        else:
                            board[idx][jdx] = key[1:]
                            break
                #print(literals)

    board = "\n".join(["|".join([board[row][col] for col in range(9)]) for row
                      in range(9)])

    return board


def create_assignment(game):
    """
    Convert a game into a truth assignment.
    """
    assignment = {}

    for clause in game:
        if len(clause) is 1:
            assignment[clause.pop()] = True

    return assignment


if __name__ == "__main__":
    example = load_example()

    assignment = create_assignment(example)
    print(draw_assignment(assignment))
