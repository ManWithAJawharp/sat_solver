from tqdm import tqdm
from copy import deepcopy

EXAMPLE_PATH = 'example.txt'
RULES_PATH = 'sudoku-rules.txt'
# SUDOKU_PATH = '1000_sudokus.txt'
# SUDOKU_PATH = 'damnhard.sdk.txt'
SUDOKU_PATH = 'subig20.sdk.txt'
PATHS = ['damnhard.sdk.txt', 'top91.sdk.txt', 'top95.sdk.txt',
         'top100.sdk.txt', 'top870.sdk.txt', 'top2365.sdk.txt',
         '1000_sudokus.txt', 'top2365.sdk.txt', 'subig20.sdk.txt']


def load_raw_sudokus(path):
    """
    Loads raw encoded sudokus from a file.

    Yields
    ------
    str
        A description of a sudoku puzzle.
        The puzzle is laid out in a single line and contains periods (.)
        for empty fields and numbers otherwise.
    """
    with open(path) as text:
        for line in text:
            yield line.strip()


def txt2dimacs(raw, name):
    """
    Save a raw sudoku game to a DIMACS file.
    """
    with open(name, 'w') as output:
        for idx, character in enumerate(raw):
            if character != '.':
                col = idx % 9
                row = (idx - col) // 9

                line = f"{row}{col}{character} 0\n"
                output.write(line)

        with open(RULES_PATH) as rule_file:
            for rule in rule_file:
                output.write(rule)


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


def load_games(path):
    """
    Load sudoku games as lists of clauses from raw puzzles and the ruleset.

    Yields
    ------
    list of set
        A list of clauses. Each clause is a set of variables.
    """
    rules = load_dimacs(RULES_PATH)

    for raw in load_raw_sudokus(path):
        sudoku = read_raw_sudoku(raw)

        yield deepcopy(sudoku + rules)


def load_all_games():
    for path in PATHS:
        with open(path) as lines:
            for idx, line in enumerate(lines):
                pass

            lines = idx + 1

        print(f"Loading {path} ({lines}) lines)")

        for game in tqdm(load_games(path), total=lines):
            yield game


def load_example():
    """
    Load just the example with the sudoku ruleset.

    Returns
    -------
    list of set
        A list of clauses. Each clause is a set of variables.
    """
    rules = load_dimacs(RULES_PATH)
    example = load_dimacs(EXAMPLE_PATH)

    return deepcopy(example + rules)


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


def check_sudoku(entries):
    """
    Check if a sudoku was solved correctly.

    Parameters
    ----------
    entries : iterable
    """
    template = {idx + 1 for idx in range(9)}

    for idx in range(9):
        row = entries[9*idx:9*idx+9]
        if set(row) != template:
            print(f"Row {idx+1}: {row} is incorrect.")
            return False

    for idx in range(9):
        col = entries[idx::9]
        if set(col) != template:
            print(f"Column {idx+1}: {col} is incorrect.")
            return False

    for idx in range(3):
        for jdx in range(3):
            block = []
            for kdx in range(3):
                start = 3 * jdx + 3 * 9 * idx + 9 * kdx
                block.append(entries[start:start+3])

            block = [inner for outer in block for inner in outer]

            if set(block) != template:
                print(f"Block {idx+1}: {block} is incorrect.")
                return False

    return True


if __name__ == "__main__":
    for idx, raw in enumerate(load_raw_sudokus(PATHS[-1])):
        txt2dimacs(raw, f"sudoku_nr_{idx+1}")
