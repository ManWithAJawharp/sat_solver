import sys
import random
# import matplotlib.pyplot as plt

from heapq import nlargest

from splits import random_split
from sudoku import load_all_games, load_example, draw_assignment, check_sudoku

RC = 0  # 'Remove Clause'
RL = 1  # 'Remove Literal'
AA = 2  # 'Add Assignment'
CC = 3  # 'Clean Containment'


class Solver():
    def __init__(self, clauses, split=random_split):
        self.clauses = self._create_clauses(*clauses)
        self.change_log = [[]]
        self.assignment = {}
        self.containment = self._get_containment()

        self.split = split
        self.splits = 0

    def solve(self):
        """
        Run the solver.

        Returns
        -------
        bool
            True if a solution was found, False otherwise.
        """
        self._remove_tautologies()
        return self._dpll()

    def _create_clauses(self, *clauses):
        """
        Convert a list of clauses to a dictionary where each entry's key
        is the clause's index.
        """
        clauses = {idx: clause for idx, clause in enumerate(clauses)}

        return clauses

    def _add_assignment(self, literal, value):
        """
        Add an assignment
        """
        if literal < 0:
            literal = abs(literal)
            value = not value

        self.assignment[literal] = value

        self.change_log[-1].append((AA, literal, literal))

    def _get_assignment(self, literal):
        """
        Retrieve the assignment of a literal.
        """
        value = self.assignment[abs(literal)]

        if literal < 0:
            return not value
        else:
            return value

    def _delete_clause(self, idx):
        """
        Delete a clause from the set of clauses by its index.
        """
        clause = self.clauses[idx]

        self.change_log[-1].append((RC, idx, clause))
        del self.clauses[idx]

    def _delete_literal(self, idx, literal):
        """
        Delete a literal from a clause.

        The clause is addressed by its index.
        """
        self.clauses[idx].remove(literal)
        self.change_log[-1].append((RL, idx, literal))

    def _clean_containment(self, idx, literal):
        """
        Make a literal not point to a certain clause anymore through
        the containment dictionary.

        Parameters
        ----------
        idx : int
            Index of the clause.
        literal : int
            Index of the literal.
        """
        self.containment[literal].remove(idx)

        self.change_log[-1].append((CC, idx, literal))

    def _assign_literal(self, literal):
        """
        Simplify the set of clauses by removing references to a assigned
        literal and its negations.
        """
        value = self._get_assignment(literal)

        if -literal in self.containment:
            not_clauses = set(self.containment[-literal])

            for idx in not_clauses:
                self._clean_containment(idx, -literal)

                if idx not in self.clauses:
                    continue

                if not value:
                    self._delete_clause(idx)
                else:
                    self._delete_literal(idx, -literal)

        clauses = set(self.containment[literal])

        for idx in clauses:
            self._clean_containment(idx, literal)

            if idx not in self.clauses:
                continue

            if value:
                self._delete_clause(idx)
            else:
                self._delete_literal(idx, literal)

    def _restore(self):
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

    def _remove_tautologies(self):
        for idx in list(self.clauses.keys()):
            clause = self.clauses[idx]

            for literal in clause:
                if -literal in clause:
                    self._delete_clause(idx, -literal)
                    self._clean_containment(idx, -literal)
                    break

    def _get_variables(self):
        """
        Return a set of all literals currently in the set of clauses.
        """
        variables = set()

        for idx in self.clauses:
            # clause = {abs(literal) for literal in self.clauses[idx]}
            clause = self.clauses[idx]
            variables = variables | clause

        return variables

    def _get_containment(self):
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

    def _dpll(self):
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
                    return False

            # Simplify the set of clauses by assigning the literals of
            # unit clauses.
            for idx in list(self.clauses.keys()):
                clause = self.clauses[idx]

                if len(clause) is 1:
                    literal = list(clause)[0]

                    # Add an assignment and simplify.
                    self._add_assignment(literal, value=True)
                    self._assign_literal(literal)

                    # Make sure to keep checking for unit clauses until
                    # they are all gone.
                    unfinished = True
                    break

        # Select a literal to split.
        literal, value = self.split(self)

        self.change_log.append([])

        self._add_assignment(literal, value)
        self._assign_literal(literal)

        satisfied = self._dpll()

        if satisfied:
            return True

        # Restore the state to the previous split to prepare for the
        # next one.
        self._restore()
        self.splits += 1

        self._add_assignment(literal, not value)
        self._assign_literal(literal)

        return self._dpll()


class GreedySolver(Solver):
    def __init__(self, clauses):
        super(GreedySolver, self).__init__(clauses)

        self.max_retries = 20
        self.max_flips = 10000

        self.score_log = []

    def solve(self):
        self._remove_tautologies()

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
                    return False

            # Simplify the set of clauses by assigning the literals of
            # unit clauses.
            for idx in list(self.clauses.keys()):
                clause = self.clauses[idx]

                if len(clause) is 1:
                    literal = list(clause)[0]

                    # Add an assignment and simplify.
                    self._add_assignment(literal, value=True)
                    self._assign_literal(literal)

                    # Make sure to keep checking for unit clauses until
                    # they are all gone.
                    unfinished = True
                    break

        return self.gsat()

    def guess_assignment(self):
        """
        Guess an initial assignment.
        """
        variables = self._get_variables()

        for variable in variables:
            if variable < 0:
                continue

            if variable in self.assignment and random.random() > 0.9:
                self.assignment[variable] = not self.assignment[variable]

            self.assignment[variable] = random.random() > 0.85

        self.change_log = [[]]

    def check_sat(self):
        sat_score = 0
        sat = True

        for idx in self.clauses:
            clause = self.clauses[idx]

            for literal in clause:
                if self._get_assignment(literal):
                    sat_score += 1
                    break
            else:
                sat = False

        return sat, sat_score

    def predict_score(self, literal):
        """
        Predict number of satisfied clauses after flipping a literal.
        """
        score = 0

        for idx in self.containment[literal]:
            clause = self.clauses[idx]

            # Count the number of satisfied literals.
            sat_literals = 0
            for lit in clause:
                if self._get_assignment(lit):
                    sat_literals += 1

            if sat_literals is 0:
                # If before no literals where satisfied, flipping one will
                # satisfy the clause.
                score += 1
            elif sat_literals is 1 and self._get_assignment(literal):
                # If the literal is the only satisfied literal in the clause,
                # flipping it will make the whole clause unsatisfied.
                score -= 1

        if literal > 0:
            return score + self.predict_score(-literal)
        else:
            return score

    def gsat(self):
        self.containment = self._get_containment()

        for iteration in range(self.max_retries):
            self.guess_assignment()

            for idx in range(self.max_flips):
                sat, score = self.check_sat()

                sys.stdout.write(f"\r{idx}: {score}/{len(self.containment)}")
                sys.stdout.flush()

                if sat:
                    return True

                best_score = -1e10
                ties = []

                for literal in self.containment:
                    if literal < 0:
                        continue

                    score = self.predict_score(literal)

                    if score > best_score:
                        best_score = score
                        ties = [literal]
                    elif score is best_score:
                        ties.append(literal)

                literal = random.choice(ties)

                value = self._get_assignment(literal)
                self._add_assignment(literal, not value)

            print("Restart")

        return False


def test_dpll():
    example = load_example()
    solver = Solver(example)

    satisfied = solver.solve()

    print(satisfied)
    draw = draw_assignment(solver.assignment)
    entries = [int(char) for char in draw if char in '123456789']
    if check_sudoku(entries):
        print("Sudoku is correct")

    successes = []
    splits = []
    n_games = 17445

    for idx, game in enumerate(load_all_games()):
        solver = Solver(game)

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


def test_gsat():
    example = load_example()
    solver = GreedySolver(example)
    satisfied = solver.solve()

    print(satisfied)
    draw = draw_assignment(solver.assignment)
    entries = [int(char) for char in draw if char in '123456789']
    if check_sudoku(entries):
        print("Sudoku is correct")
    print(draw)

    '''
    plt.title("GSAT progress")
    plt.plot(solver.score_log)
    plt.xlabel("Flips")
    plt.ylabel("Satisfied clauses")
    plt.show()
    '''


if __name__ == "__main__":
    test_gsat()
    # test_dpll()
