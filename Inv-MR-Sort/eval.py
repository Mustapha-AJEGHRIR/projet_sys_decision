
from mip import MIPSolver
from data_generator import generate
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
from numpy import left_shift
from matplotlib import pyplot as plt
from tqdm import tqdm
from config import default_eval_rounds, default_n_generated_list


def eval_parameters(params : dict, verbose_results = True, verbose_progress = False) -> tuple:
    """
    Evaluates the parameters of the Inverse MR-Sort problem. It trains the solver with
    some training data and then evaluates the performance of the solver on the test data.
    all the data is generated in random according the the parameters.
    
    Arguments:
        params: dict -- parameters of the Inverse MR-Sort problem
        verbose_results: bool -- if True, prints the results
        verbose_progress: bool -- if True, prints the progress of the training
    Returns:
        tuple -- (accuracy, precision, recall, f1)
    """
    data_train = generate(params, verbose=False)
    data_test = generate(params, verbose=False)
    test_classes = list(data_test['class'])
    
    solver = MIPSolver(data_train, None, verbose = verbose_progress)
    solver.solve(save_solution=False)
    predicted_classes = solver.predict(data_test.to_numpy()[:,:-1]) # [:,:-1] to remove the class column

    if verbose_results:
        print("=> Confusion Matrix :")
        mtrx = confusion_matrix(test_classes, predicted_classes).__str__()
        for line in mtrx.split("\n"):
            print("\t" + line)
        
        print("=> Accuracy :\t {:.2}".format(accuracy_score(test_classes, predicted_classes)))
        print("=> Precision :\t {:.2}".format(precision_score(test_classes, predicted_classes)))
        print("=> Recall :\t {:.2}".format(recall_score(test_classes, predicted_classes)))
        print("=> F1 :\t {:.2}".format(f1_score(test_classes, predicted_classes)))
    
    return accuracy_score(test_classes, predicted_classes), precision_score(test_classes, predicted_classes), recall_score(test_classes, predicted_classes), f1_score(test_classes, predicted_classes)


def multi_eval_parameters(params : dict, n: int, verbose_results = False, verbose_progress = False) -> tuple:
    """
    Evaluates the parameters of the Inverse MR-Sort problem for n rounds. It trains the 
    solver with some training data and then evaluates the performance of the solver 
    on the test data. all the data is generated in random according the the parameters.
    
    Arguments:
        params: dict -- parameters of the Inverse MR-Sort problem
        n: int -- number of rounds of evaluation
        verbose_results: bool -- if True, prints the results
        verbose_progress: bool -- if True, prints the progress of the training
    Returns:
        tuple -- (mean_accuracy, mean_precision, mean_recall, mean_f1)
    """
    accuracies = []
    precisions = []
    recalls = []
    f1s = []
    for i in range(n):
        acc, prec, rec, f1 = eval_parameters(params, verbose_results, verbose_progress)
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
    mean_accuracy = sum(accuracies)/n
    mean_precision = sum(precisions)/n
    mean_recall = sum(recalls)/n
    mean_f1 = sum(f1s)/n
    return mean_accuracy, mean_precision, mean_recall, mean_f1

def plot_n_generated_effect(params : dict, n_rounds= default_eval_rounds, 
                            n_generated_list= default_n_generated_list, 
                            verbose_results = False, verbose_progress = False):
    """
    Plots the effect of the number of generated data on the performance of the solver. 
    
    Arguments:
        params: dict -- parameters of the Inverse MR-Sort problem
        n_rounds: int -- number of rounds of evaluation
        n_generated_list: list -- list of n_generated values to be tested
        verbose_results: bool -- if True, prints the results
        verbose_progress: bool -- if True, prints the progress of the training
    Returns:
        tuple -- (mean_accuracy, mean_precision, mean_recall, mean_f1)
    """
    accuracies = []
    precisions = []
    recalls = []
    f1s = []
    for n_generated in tqdm(n_generated_list):
        params['n_generated'] = n_generated
        acc, prec, rec, f1 = multi_eval_parameters(params, n_rounds, verbose_results, verbose_progress)
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
    plt.plot(n_generated_list, accuracies, label='accuracy')
    plt.plot(n_generated_list, precisions, label='precision')
    plt.plot(n_generated_list, recalls, label='recall')
    plt.plot(n_generated_list, f1s, label='f1')
    plt.legend()
    plt.show()