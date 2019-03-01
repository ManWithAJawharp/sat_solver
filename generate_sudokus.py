from subprocess import check_output
import argparse

URL = "https://nine.websudoku.com/?level=1"
DIFFICULTY = ['simple', 'easy', 'intermediate', 'expert']


def generate(n, difficulty):
    """
    Generate a number of puzzles of a certain difficulty.

    Parameters
    ----------
    n : int
    difficulty : str
    """
    output = check_output([
        'qqwing',
        '--generate', str(n),
        '--difficulty', difficulty,
        '--one-line'
    ])

    return output.decode('utf-8')


def count_number(sudoku):
    number_count = 0

    for entry in sudoku:
        if entry in '123456789':
            number_count += 1

    return number_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a number of sudoku puzzle of a given "
                    "difficulty.")
    parser.add_argument('-o', '--output', dest='output', type=str,
                        help="File to write the puzzles to.")
    parser.add_argument('-n', type=int, default=1,
                        help="The number with puzzles to generate.")
    parser.add_argument('-d', '--difficulty', dest='difficulty', type=str,
                        default='simple',
                        help="Difficulty level of the puzzles. Select "
                             f"{[d for d in DIFFICULTY]}.")
    args = parser.parse_args()

    print(f"Generating {args.n} puzzles of {args.difficulty} difficulty")

    puzzles = {}

    sudokus = generate(args.n, args.difficulty)

    counts = [count_number(sudoku) for sudoku in sudokus]

    if args.output is None:
        title = f"{args.n}_{args.difficulty}.sdk.txt"
    else:
        title = args.output

    with open(title, 'w') as output:
        output.write(sudokus)
