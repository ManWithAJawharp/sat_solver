import os

from tqdm import tqdm
from copy import deepcopy

EXAMPLE_PATH = 'example.txt'
RULES_PATH = 'sudoku-rules.cnf'
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


def raw2dimacs(raw):
    """
    Convert a raw one-line sudoku to DIMACS CNF rules.

    Parameters
    ----------
    raw : str
        A single lined representation of a sudoku puzzle.

    Returns
    -------
    list of str
        List of all the CNF lines.
    """
    lines = []

    for idx, character in enumerate(raw):
        if character in '123456789':
            col = idx % 9
            row = (idx - col) // 9

            lines.append(f"{row+1}{col+1}{character} 0\n")

    return lines


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
        lines = [line for line in text if 'c' not in line and 'p' not in line]

    lines = ''.join(lines)
    lines = lines.replace('\n', ' ')
    lines = lines.replace('\t', ' ')
    lines = lines.replace('\r', ' ')
    lines = lines.split(' 0')

    for line in lines:
        variables = line.split()

        if len(variables) is 0:
            continue

        # variables = [variable for variable in variables if variable != '0']

        clause = {
            int(variable)
            for variable in variables
        }

        clauses.append(clause)

        '''
        for line in text:
            if 'p' in line or 'c' in line:
                continue

            line = line.strip("0 \n")

            variables = line.split()
            clause = {
                int(variable)
                for variable in variables
            }

            if clause != set():
                clauses.append(clause)
        '''

    return clauses


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


def save_sudoku_cnf(path, rules, name, output_location=''):
    """
    Loads a raw sudoku file, converts each puzzle into clausal normal
    form and saves them as DIMACS CNF files.

    Parameters
    ----------
    path : str
        Path to the sudoku file.
    rules : str
        Path to the DIMACS rule file.
    name : str
        Name of the output file. Note that if the input file contains
        multiple puzzles, an index will be added to each saved file.
    output_location : str, optional
        Directory to write the output files to.
    """
    for idx, raw in enumerate(load_raw_sudokus(path)):
        dimacs = raw2dimacs(raw)

        with open(os.path.join(
            output_location, f"{name}_{idx:05d}.cnf"), 'w'
                ) as output:
            # Write comments.
            output.write(f"c Sudoku {name}_{idx:05d}.cnf with rules.\n")
            output.write("c\n")

            # Write problem line.
            output.write(f"p cnf 999 12016\n")

            # Write puzzle facts.
            for line in dimacs:
                output.write(line)

            # Write sudoku rules.
            with open(rules, 'r') as rules_file:
                for line in rules_file:
                    output.write(line)


def check_sudoku(entries):
    """
    Check if a sudoku was solved correctly.

    Parameters
    ----------
    entries : iterable

    Returns
    -------
    bool
        True if the sudoku was solved correctly, False otherwise.
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
    save_sudoku_cnf('simple_100.sdk.txt', 'sudoku-rules.cnf', 'simple',
                    'simple/')
    save_sudoku_cnf('easy_100.sdk.txt', 'sudoku-rules.cnf', 'easy', 'easy/')
    save_sudoku_cnf('intermediate_100.sdk.txt', 'sudoku-rules.cnf',
                    'intermediate', 'intermediate/')
    save_sudoku_cnf('expert_100.sdk.txt', 'sudoku-rules.cnf', 'expert',
                    'expert/')

    clauses = load_dimacs('puzzles/test_00000.cnf')
    print(clauses)
    print(len(clauses))
