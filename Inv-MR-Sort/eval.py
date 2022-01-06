
from mip import MIPSolver
from data_generator import generate


def eval_parameters(params : dict) -> tuple:
    data_train = generate(params, verbose=False)
    data_test = generate(params, verbose=False)
    test_classes = list(data_test['class'])
    
    solver = MIPSolver(data_train, None, verbose = False)
    solver.solve(save_solution=False)
    predicted_classes = solver.predict(data_test.to_numpy()[:,:-1]) # [:,:-1] to remove the class column
    
    
    