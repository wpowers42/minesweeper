import constraint
# load the state of the board
vectors = [{'root': (0, 0), 'vector': [(0, 1), (1, 0), (1, 1)], 'mines': 1},
           {'root': (0, 2), 'vector': [(0, 1), (1, 1), (1, 2)], 'mines': 2}, ]

#
unique_vectors = {(0, 1), (1, 0), (1, 1), (1, 2)}

# start a new problem

problem = constraint.Problem()

# create a variable for each unique vector location
for vector in unique_vectors:
    problem.addVariable(str(vector), [0, 1])

for vector in vectors:
    variables = tuple([str(c) for c in vector['vector']])
    problem.addConstraint(
        constraint.ExactSumConstraint(vector['mines']), variables)

# get all possible solutions that satisfy the constraints

print(problem.getSolutions())
