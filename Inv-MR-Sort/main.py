from mip import MIPSolver


def inverse_mr_sort():
    solver = MIPSolver()
    res = solver.solve()
    # print(res)


if __name__ == "__main__":
    inverse_mr_sort()