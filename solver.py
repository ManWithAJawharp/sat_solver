import random

from tqdm import tqdm

from splits import random_split
from sudoku import load_games, load_example, draw_assignment, check_sudoku

RC = 0  # 'Remove Clause'
RL = 1  # 'Remove Literal'
AA = 2  # 'Add Assignment'
CC = 3  # 'Clean Containment'


class Solver():
    def __init__(self, clauses, split=random_split):
        self.clauses = self.create_clauses(*clauses)
        self.change_log = [[]]
        self.assignment = {}
        self.containment = self.get_containment()

        self.split = random_split
        self.splits = 0

    def solve(self):
        self.remove_tautologies()
        return self.dpll()

    def create_clauses(self, *clauses):
        """
        Convert a list of clauses to a dictionary where each entry's key
        is the clause's index.
        """
        clauses = {idx: clause for idx, clause in enumerate(clauses)}

        return clauses

    def add_assignment(self, literal, value):
        """
        Add an assignment
        """
        if literal < 0:
            literal = abs(literal)
            value = not value

        self.assignment[literal] = value

        self.change_log[-1].append((AA, literal, literal))

    def get_assignment(self, literal):
        """
        Retrieve the assignment of a literal.
        """
        value = self.assignment[abs(literal)]

        if literal < 0:
            return not value
        else:
            return value

    def delete_clause(self, idx):
        """
        Delete a clause from the set of clauses by its index.
        """
        clause = self.clauses[idx]

        self.change_log[-1].append((RC, idx, clause))
        del self.clauses[idx]

    def delete_literal(self, idx, literal):
        """
        Delete a literal from a clause.

        The clause is addressed by its index.
        """
        self.clauses[idx].remove(literal)
        self.change_log[-1].append((RL, idx, literal))

    def clean_containment(self, idx, literal):
        """
        Make a literal not point to a certain clause anymore through
        the containment dictionary.
        """
        self.containment[literal].remove(idx)

        self.change_log[-1].append((CC, idx, literal))

    def assign_literal(self, literal):
        """
        Simplify the set of clauses by removing references to a assigned
        literal and its negations.
        """
        value = self.get_assignment(literal)

        if -literal in self.containment:
            not_clauses = set(self.containment[-literal])

            for idx in not_clauses:
                self.clean_containment(idx, -literal)

                if idx not in self.clauses:
                    continue

                if not value:
                    self.delete_clause(idx)
                else:
                    self.delete_literal(idx, -literal)

        clauses = set(self.containment[literal])

        for idx in clauses:
            self.clean_containment(idx, literal)

            if idx not in self.clauses:
                continue

            if value:
                self.delete_clause(idx)
            else:
                self.delete_literal(idx, literal)

        # del self.contain[literal]

    def restore(self):
        """
        Undo the most recent stack of changes in the change log.

        The change log is a stack of stacks; the top element of this
        stack is removed and its operations are reversed.
        """
        log_entry = self.change_log.pop()

        while len(log_entry) > 0:
            action, idx, content = log_entry.pop()

            if action is RC:
                # Recover a clause.
                self.clauses[idx] = content
            elif action is RL:
                # Recover a literal.
                self.clauses[idx].add(content)
            elif action is AA:
                # Undo a variable assignment.
                del self.assignment[abs(content)]
            elif action is CC:
                self.containment[content].add(idx)
            else:
                raise ValueError(
                    f"Cannot restore, action not recognized."
                    f"({action}, {idx}, {content}")

    def remove_tautologies(self):
        for idx in list(self.clauses.keys()):
            clause = self.clauses[idx]

            for literal in clause:
                if -literal in clause:
                    self.delete_clause(idx, -literal)
                    self.clean_containment(idx, -literal)
                    break

    def unit_propagate(self):
        global clauses

        for idx in list(self.clauses.keys()):
            clause = self.clauses[idx]

            if len(clause) is 1:
                literal = list(clause)[0]

                self.add_assignment(literal, value=True)
                self.assign_literal(literal)

                return self.dpll()

    def get_variables(self):
        variables = set()

        for idx in self.clauses:
            # clause = {abs(literal) for literal in self.clauses[idx]}
            clause = self.clauses[idx]
            variables = variables | clause

        return variables

    def get_containment(self):
        """
        Construct a dictionary mapping each literal to a list of
        clauses that contain it.
        """
        containment = {}

        for idx in self.clauses:
            clause = self.clauses[idx]

            for literal in clause:
                if literal in containment:
                    containment[literal].add(idx)
                else:
                    containment[literal] = {idx}

        return containment

    def dpll(self):
        # print(len(self.clauses))

        unfinished = True
        while unfinished:
            unfinished = False

            if len(self.clauses) is 0:
                # Set of clauses is empty.
                return True

            # Check for empty clauses.
            for idx in self.clauses:
                if len(self.clauses[idx]) is 0:
                    # Set of clauses contains an empty clause.
                    # print(f"Found empty clause: {idx}: {clauses[idx]}")
                    return False

            # Simplify the set of clauses by assigning the literals of
            # unit clauses.
            for idx in list(self.clauses.keys()):
                clause = self.clauses[idx]

                if len(clause) is 1:
                    # print(f"Found unit clause {clause}")
                    literal = list(clause)[0]

                    # Add an assignment and simplify.
                    self.add_assignment(literal, value=True)
                    self.assign_literal(literal)

                    # Make sure to keep checking for unit clauses until
                    # they are all gone.
                    unfinished = True
                    break

        # Select a literal to split.
        literal, value = self.split(self)

        self.change_log.append([])

        # print(f"Set {literal} to True")
        self.add_assignment(literal, value)
        self.assign_literal(literal)

        satisfied = self.dpll()

        if satisfied:
            return True

        # Restore the state to the previous split to prepare for the
        # next one.
        self.restore()
        self.splits += 1

        # print(f"Set {literal} to False")
        self.add_assignment(literal, not value)
        self.assign_literal(literal)

        return self.dpll()


if __name__ == "__main__":
    example = load_example()
    solver = Solver(example)

    satisfied = solver.solve()

    print(satisfied)
    draw = draw_assignment(solver.assignment)
    entries = [int(char) for char in draw if char in '123456789']
    if check_sudoku(entries):
        print("Sudoku is correct")

    successes = []
    correct = []
    splits = []
    n_games = 1000

    for idx, game in tqdm(enumerate(load_games()), total=n_games):
        solver = Solver(game)
        change_log = [[]]
        assignment = {}
        contain = {}  # All clauses that contain a certain literal.

        try:
            satisfied = solver.solve()
        except RecursionError:
            state = 'error'
        else:
            if satisfied:
                state = 'success'
            else:
                state = 'failure'

        successes.append(state)
        splits.append(solver.splits)

        if idx >= n_games:
            break

    success_rate = sum([state == 'success' for state
                        in successes]) / len(successes)
    failure_rate = sum([state == 'failure' for state
                        in successes]) / len(successes)
    split_rate = sum(splits) / len(splits)

    print(f"\nSuccess rate: {success_rate * 100:0.1f}% | "
          f"Failure rate: {failure_rate * 100:0.1f}%")
    print(f"Average number of splits: {split_rate:.2f}")
