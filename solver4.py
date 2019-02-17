import random

from tqdm import tqdm

from sudoku import load_games, load_example, draw_assignment

RC = 0
RL = 1


class Solver():
    def __init__(self, *clauses):
        self.clauses = {idx: clause for idx, clause in enumerate(clauses)}
        self.assignment = {}

        # The log is a stack of entries keeping track of elements
        # deleted from the set of clauses.
        self.log = {}

        self.splits = 1
        self.log[self.splits] = []

    def solve(self):
        print("Start solving")
        return self.dll(True), self.assignment

    def delete_clause(self, idx):
        """
        Delete a clause from the set and record it in the log.
        """
        clause = self.clauses[idx]
        self.log[self.splits].append((RC, idx, clause))
        del self.clauses[idx]

    def delete_literal(self, idx, literal):
        """
        Delete a literal from a clause and record it in the log.
        """
        self.clauses[idx].remove(literal)
        self.log[self.splits].append((RL, idx, literal))

    def restore(self):
        """
        Restore the most recent log entry to the clause set.
        """
        while len(self.log[self.splits]) > 0:
            action, idx, entry = self.log[self.splits].pop()

            if action is RC:
                self.clauses[idx] = entry
            elif action is RL:
                self.clauses[idx].add(entry)

    def add_assignment(self, literal, value):
        """
        Register the assignment of a variable.
        """
        if literal < 0:
            literal = abs(literal)
            value = not value

        self.assignment[literal] = value

    def del_assignment(self, literal):
        """
        Undo the assignment of a variable.
        """
        del self.assignment[abs(literal)]

    def get_assignment(self, literal):
        """
        Retrieve the value assigned to a literal.
        """
        value = self.assignment[abs(literal)]

        if literal < 0:
            return not value
        else:
            return value

    def get_variables(self):
        """
        Return the set of all variables in the set of clauses.
        """
        variables = set()
        for idx in list(self.clauses.keys()):
            variables = variables | self.clauses[idx]

        return variables

    def assign_literal(self, literal):
        """
        Propagate the value of a variable through the set of clauses.
        """
        value = self.get_assignment(literal)
        # print(f"Assigning {literal} to {value}")

        for idx in list(self.clauses.keys()):
            clause = self.clauses[idx]

            if literal in clause:
                if value:
                    self.delete_clause(idx)
                else:
                    self.delete_literal(idx, literal)
            elif -literal in clause:
                if not value:
                    self.delete_clause(idx)
                else:
                    self.delete_literal(idx, -literal)

    def remove_tautologies(self):
        """
        Remove any clauses that contain `l v -l`.
        """
        for idx in list(self.clauses.keys()):
            clause = self.clauses[idx]

            for literal in clause:
                if -literal in clause:
                    self.delete_clause(idx)
                    break

    def pure_detector(self):
        """
        Iterate over all literals that appear as pure in the set.
        """
        variables = self.get_variables()

        while len(variables) > 0:
            variable = variables.pop()

            if -variable not in variables:
                yield variable
            else:
                variables.remove(-variable)

    def assign_pure_literals(self):
        """
        Set any pure literal to true.
        """
        for literal in self.pure_detector():
            self.add_assignment(literal, value=True)
            self.assign_literal(literal)

    def unit_propagate(self):
        for idx in self.clauses:
            clause = self.clauses[idx]

            if len(clause) is 1:
                # print("Found unit clause: ", clause)
                literal = list(clause)[0]

                self.add_assignment(literal, value=True)
                self.assign_literal(literal)

                return self.unit_propagate()

    def choose_literal(self, variables):
        """
        Choose a literal from the set of clauses.
        """
        # print(f"Variables: {variables}")
        return random.choice(list(variables)), True

    def split(self):
        self.splits += 1
        self.log[self.splits] = []

        variables = self.get_variables()
        if len(variables) is 0:
            return False

        literal, value = self.choose_literal(variables)

        self.add_assignment(literal, value)
        self.assign_literal(literal)

        print(f"Split at {literal}: {value}")
        satisfied = self.dll()

        if satisfied:
            return satisfied

        self.restore()
        del self.log[self.splits]
        self.splits -= 1

        self.del_assignment(literal)
        self.add_assignment(literal, not value)
        self.assign_literal(literal)

        print(f"Split at {literal}: {not value}")
        return self.dll()

    def dll(self, tautologies=False):
        print(f"Clauses: {len(self.clauses)}")

        # Set of clauses is empty.
        if len(self.clauses) is 0:
            return True

        # Empty clause found.
        for idx in self.clauses.keys():
            if len(self.clauses[idx]) is 0:
                print(f"Empty clause found {idx}: {self.clauses[idx]}")
                return False

        if tautologies:
            print("Removing tautologies")
            self.remove_tautologies()

        print("Unit-propagate")
        self.unit_propagate()

        '''
        print("Assign pure")
        self.assign_pure_literals()
        '''

        if len(self.clauses) is 0:
            return True

        print("Split")
        return self.split()


if __name__ == "__main__":
    '''
    solver = Solver({5}, {1, -2}, {2, 3}, {-3, 1}, {-1, 2, 3, 1})
    print(solver.solve())
    print()

    solver = Solver({1, -3}, {1, -2, 3}, {2, 3, -1}, {-3, -1, 2})
    print(solver.solve())
    print()
    '''

    example = load_example()
    solver = Solver(*example)
    satisfied, assignment = solver.solve()
    print(draw_assignment(assignment))

    successes = []
    for idx, game in enumerate(load_games()):
        solver = Solver(*game)

        satisfied, assignment = solver.solve()
        if not satisfied:
            continue
        print(draw_assignment(assignment))

        successes.append(1 if satisfied else 0)

    print(sum(successes))
