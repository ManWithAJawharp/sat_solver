import sys
import random
import argparse

from splits import naive_split, random_split
from sudoku import load_all_games, load_example, draw_assignment, check_sudoku
from sudoku import load_dimacs

RC = 0  # 'Remove Clause'
RL = 1  # 'Remove Literal'
AA = 2  # 'Add Assignment'
CC = 3  # 'Clean Containment'


class Solver():
    def __init__(self, clauses, split=naive_split):
        self.clauses = self._create_clauses(*clauses)
        self.change_log = [[]]
        self.assignment = {}
        self.containment = {}

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
        self.containment = self._get_containment()
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
        try:
            value = self.assignment[abs(literal)]
        except KeyError:
            return False

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
                    self._delete_clause(idx)
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
                print("All clauses where satisfied")
                return True

            # Check for empty clauses.
            if set() in self.clauses.values():
                return False

            # Simplify the set of clauses by assigning the literals of
            # unit clauses.
            for idx in list(self.clauses):
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

    def solve(self):
        # self._remove_tautologies()

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

                sys.stdout.write(f"\r{idx:05d}: {score}/{len(self.clauses)} ")
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

                if random.random() > 0.2:
                    literal = random.choice(ties)
                    best_score = self.predict_score(literal)
                else:
                    literal = random.choice(list(self._get_variables()))

                print(literal, best_score)

                value = self._get_assignment(literal)
                self._add_assignment(literal, not value)

            print("Restart")

        return False


class WalkSAT(Solver):
    def __init__(self, clauses, simplify=False):
        self.clauses = self._create_clauses(*clauses)

        self.max_tries = 50
        self.max_flips = 10000
        self.containment = self._get_containment()
        self.assignment = self._guess_assignment()
        self.change_log = [[]]

        if simplify:
            # Simplify by removing unit clauses.
            for clause in list(self.clauses.values()):
                if len(clause) is 1:
                    literal = list(clause)[0]
                    self._add_assignment(literal, True)
                    self._assign_literal(literal)

            self.containment = self._get_containment()
            self.assignment = self._guess_assignment(self.assignment)

    def solve(self):
        for retry in range(self.max_tries):
            self.assignment = self._guess_assignment(self.assignment)

            for flip in range(self.max_flips):
                sat, score = self._check_sat()
                true_rate = sum(value for value in self.assignment.values())
                true_rate /= len(self.assignment)

                sys.stdout.write(
                    f"\r{retry}:{flip} | Score: {score}/{len(self.clauses)} |"
                    f" {100 * true_rate:.1f}%")
                sys.stdout.flush()

                if sat:
                    return True

                select = random.random()
                # progress = score / len(self.clauses)
                progress = flip / self.max_flips
                p_walk = progress * 0.7 + (1 - progress) * 0.9
                p_best = progress * 0.9 + (1 - progress) * 0.95

                if select <= p_walk:
                    self._random_walk()
                elif select <= p_best:
                    self._flip_best_literal()
                else:
                    literal = random.choice(list(self.containment.keys()))
                    value = self._get_assignment(literal)
                    self._add_assignment(literal, not value)

                # print(self._find_unsat())

        return sat

    def _get_containment(self):
        containment = {}

        for idx in self.clauses:
            clause = self.clauses[idx]

            for literal in clause:
                if literal not in containment:
                    containment[literal] = {idx}
                else:
                    containment[literal].add(idx)

        return containment

    def _guess_assignment(self, assignment=None, soft=0.7):
        """
        Guess a random assignment.
        If an assignment is provided, a 'soft reset' will be
        performed, leaving most assignments intact.

        Parameters
        ----------
        assignment : dict, optional
            A given assignment. If this is not None, a soft
            reset will be performed as determined by `soft`.
        soft : float, optional
            If an assignment is given, this value determines
            the probability of leaving an assignment intact
            when resetting.

        Returns
        -------
        dict
            Either a new assignment dictionary or an updated
            variant of the given assignment.
        """
        if assignment is None:
            assignment = {}

        for literal in self.containment:
            if literal > 0:
                if literal in assignment and random.random() < soft:
                    continue

                assignment[literal] = random.random() < 0.1

        return assignment

    def _check_sat(self):
        unsat_clauses = self._find_unsat()
        # print(unsat_clauses, len(unsat_clauses), len(unsat_clauses) is 0)

        score = len(self.clauses) - len(unsat_clauses)

        if len(unsat_clauses) is 0:
            return True, score

        return False, score

    def _predict_score(self, literal):
        try:
            clauses = self.containment[literal]
        except KeyError:
            return 0

        sat_clauses = 0

        for idx in clauses:
            clause = self.clauses[idx]
            sat_literals = 0

            # print(idx, clause)
            for literal_ in clause:
                if self._get_assignment(literal_):
                    sat_literals += 1

            if sat_literals is 0:
                sat_clauses += 1
            elif sat_literals is 1 and self._get_assignment(literal):
                sat_clauses -= 1

        return sat_clauses

    def _add_assignment(self, literal, value):
        """
        Add an assignment
        """
        if literal < 0:
            literal = abs(literal)
            value = not value

        self.assignment[literal] = value

    def _flip_best_literal(self):
        ties = []
        best_score = -1e10

        for literal in self.containment:
            if literal < 0:
                continue

            score = self._predict_score(literal) \
                + self._predict_score(-literal)

            if score > best_score:
                ties = [literal]
                best_score = score
            elif score is best_score:
                ties.append(literal)

        literal = random.choice(ties)

        value = self._get_assignment(literal)
        self._add_assignment(literal, not value)

        # print(literal, value, best_score, ties)

    def _random_walk(self):
        unsat_clauses = self._find_unsat()
        # print(unsat_clauses)

        clause = random.choice(list(unsat_clauses.values()))

        ties = []
        best_score = -1e10

        for literal in clause:
            if literal < 0:
                continue

            score = self._predict_score(literal) \
                + self._predict_score(-literal)

            if score > best_score:
                ties = [literal]
                best_score = score
            elif score is best_score:
                ties.append(literal)

        if len(ties) > 0:
            literal = random.choice(ties)
        else:
            literal = random.choice(list(clause))

        self._add_assignment(literal, not self._get_assignment(literal))

    def _find_unsat(self):
        unsat_clauses = {}
        for idx, clause in self.clauses.items():
            # print("find_unsat", idx, clause)
            for literal in clause:
                if self._get_assignment(literal):
                    break
            else:
                unsat_clauses[idx] = clause

        return unsat_clauses


def generate_random_problems(n, variables=600, clause_size=3,
                             num_clauses=1000):
    for problem in range(n):
        clauses = []

        for idx in range(num_clauses):
            clause = set()

            for _ in range(clause_size):
                literal = random.randint(0, variables - 1) + 1

                if random.random() < 0.5:
                    literal *= -1

                clause.add(literal)

            clauses.append(clause)

        yield clauses


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

    try:
        for idx, game in enumerate(load_all_games()):
            solver = Solver(game)
            satisfied = solver.solve()
            draw = draw_assignment(solver.assignment)
            entries = [int(char) for char in draw if char in '123456789']

            if satisfied and check_sudoku(entries):
                state = 'success'
            else:
                state = 'failure'
                print(state)

            successes.append(state)
            splits.append(solver.splits)
    except KeyboardInterrupt:
        pass

    success_rate = sum([state == 'success' for state
                        in successes]) / len(successes)
    failure_rate = sum([state == 'failure' for state
                        in successes]) / len(successes)
    split_rate = sum(splits) / len(splits)

    print(f"\nSuccess rate: {success_rate * 100:0.1f}% | "
          f"Failure rate: {failure_rate * 100:0.1f}%")
    print(f"Average number of splits: {split_rate:.2f}")


def test_gsat():
    for problem in generate_random_problems(10):
        solver = GreedySolver(problem)
        print(solver.solve())

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


def test_walksat():
    for problem in generate_random_problems(10):
        solver = WalkSAT(problem)
        satisfied = solver.solve()
        print("Satisfied" if satisfied else "Unsatisfied")

        solver = Solver(problem)
        satisfied = solver.solve()
        print("Satisfied" if satisfied else "Unsatisfied")

    for game in load_all_games():
        game = load_example()
        solver = WalkSAT(game, True)
        satisfied = solver.solve()

        print("Satisfied" if satisfied else "Unsatisfied")
        draw = draw_assignment(solver.assignment)
        entries = [int(char) for char in draw if char in '123456789']
        if check_sudoku(entries):
            print("Sudoku is correct")
        print(draw)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAT Solver")
    parser.add_argument('-S', metavar='N', dest='strategy', type=int,
                        default=1, help="The strategy to apply to a problem.")
    parser.add_argument(metavar='CNF', dest='cnf',
                        help="Input file in DIMACS CNF format.")
    args = parser.parse_args()

    clauses = load_dimacs(args.cnf)

    if args.strategy is 1:
        print("Selected basic Davis-Putnam")
        solver = Solver(clauses)
    elif args.strategy is 2:
        print("Selected Davis-Putnam with random split")
        solver = Solver(clauses, split=random_split)
    elif args.strategy is 3:
        print("Selected WalkSAT")
        solver = WalkSAT(clauses, True)
    else:
        raise ValueError(f"'{args.strategy}' is not a valid strategy."
                         f"Please select 1, 2, or 3.")

    satisfied = solver.solve()
    print("Satisfied" if satisfied else "Unsatisfied")

    print(draw_assignment(solver.assignment))
