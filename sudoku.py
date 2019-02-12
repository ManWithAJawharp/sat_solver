EXAMPLE_PATH = 'example.txt'
RULES_PATH = 'sudoku_rules.txt'
SUDOKU_PATH = '1000_sudokus.txt'


def load_raw_sudokus(path):
    with open(path) as text:
        for line in text:
            yield line.strip()


def read_raw_sudoku(raw):
    clauses = []

    for idx, element in enumerate(raw):
        row = idx // 9 + 1
        col = idx % 9 + 1

        if element in '123456789':
            clauses.append({int(f"{row}{col}{element}")})

    return sorted(clauses)


def load_dimacs(path):
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
    rules = load_dimacs(RULES_PATH)

    if example:
        example = load_dimacs(EXAMPLE_PATH)

        yield example + rules

    for raw in load_raw_sudokus(SUDOKU_PATH):
        yield read_raw_sudoku(raw) + rules


if __name__ == "__main__":
    for game in load_games(True):
        print(len(game))
        break
