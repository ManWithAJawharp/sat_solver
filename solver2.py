from sudoku import load_example


class ClauseSet():
    def __init__(self, clauses):
        self.clauses = {idx: clause for idx, clause in enumerate(clauses)}
        self.deleted = {}
        self.assignment = {}

    def solve(self):
        # Check for empty set.
        if len(self.clauses) is 0:
            return True, self.assignment

        # Check for empty clause.
        for idx, clause in self.clauses.items():
            if len(clause) is 0:
                return False, self.assignment

        self.remove_tautologies()

    def remove_tautologies(self):
        for idx, clause in self.clauses.items():
            for variable in clause:
                if -variable in clause:
                    self.clauses.remove(idx)
                    break


problem = ClauseSet([{1, -2}, {2, 3}, {-3, 1}])
print(problem.solve())
print()

problem = ClauseSet([{1, -3}, {1, -2, 3}, {2, 3, -1}, {-3, -1, 2}])
print(problem.solve())
print()

example = load_example()
print(len(example))
