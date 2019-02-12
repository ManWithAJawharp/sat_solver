def evaluate_clause(clause):
    """
    Evaluate a clause to be true of false.
    """
    # TODO: If clause is a set of clauses; run evaulate_clause for each
    # sublcause.
    if len(clause) is 0:
        return False

    return np.any(clause)


