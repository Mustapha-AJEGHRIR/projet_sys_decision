
from mip import MIPSolver
from data_generator import generate
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
from config import default_eval_rounds, default_n_generated_list, default_n_list, output_folder
from utils import get_random_params
from time import time
from matplotlib import pyplot as plt
from tqdm import tqdm
import os


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
    
    tik = time()
    solver = MIPSolver(data_train, None, verbose = verbose_progress)
    solver.solve(save_solution=False)
    tok = time()
    duration = tok - tik
    predicted_classes = solver.predict(data_test.to_numpy()[:,:-1]) # [:,:-1] to remove the class column

    acc = accuracy_score(test_classes, predicted_classes)
    prec = precision_score(test_classes, predicted_classes)
    rec = recall_score(test_classes, predicted_classes)
    f1 = f1_score(test_classes, predicted_classes)
    if verbose_results:
        print("=> Confusion Matrix :")
        mtrx = confusion_matrix(test_classes, predicted_classes).__str__()
        for line in mtrx.split("\n"):
            print("\t" + line)
        
        print("=> Accuracy :\t {:.2}".format(acc))
        print("=> Precision :\t {:.2}".format(prec))
        print("=> Recall :\t {:.2}".format(rec))
        print("=> F1 :\t {:.2}".format(f1))
    
    return acc, prec, rec, f1, duration


def multi_eval_parameters(n=5, p=1, n_generated=100, n_rounds= 3, verbose_results = False, verbose_progress = False) -> tuple:
    """
    Evaluates the parameters of the Inverse MR-Sort problem for n rounds. It trains the 
    solver with some training data and then evaluates the performance of the solver 
    on the test data. all the data is generated in random according the the parameters.
    
    Arguments:
        n: int -- number of criterias to be generated randomly
        p: int -- number of profiles to be generated randomly
        n_generated: int -- number of generated data
        n_rounds: int -- number of rounds of evaluation
        verbose_results: bool -- if True, prints the results
        verbose_progress: bool -- if True, prints the progress of the training
    Returns:
        tuple -- (mean_accuracy, mean_precision, mean_recall, mean_f1)
    """
    accuracies = []
    precisions = []
    recalls = []
    f1s = []
    durations = []
    for i in range(n_rounds):
        params = get_random_params(n_generated, n, p)
        acc, prec, rec, f1, duration = eval_parameters(params, verbose_results, verbose_progress)
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        durations.append(duration)
    mean_accuracy = sum(accuracies)/n_rounds
    mean_precision = sum(precisions)/n_rounds
    mean_recall = sum(recalls)/n_rounds
    mean_f1 = sum(f1s)/n_rounds
    mean_duration = sum(durations)/n_rounds
    return mean_accuracy, mean_precision, mean_recall, mean_f1, mean_duration

def plot_n_generated_effect_random(n=5, p=1, n_rounds= default_eval_rounds, 
                            n_generated_list= default_n_generated_list, 
                            verbose_results = False, verbose_progress = False):
    """
    Generates some configuration randomly and plots the effect of the
    number of generated data on the performance of the solver. 
    
    Arguments:
        n: int -- number of criterias to be generated randomly
        p: int -- number of profiles to be generated randomly
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
    durations = []
    for n_generated in tqdm(n_generated_list, ascii=True, desc="Generating and evaluating"):
        acc, prec, rec, f1, duration = multi_eval_parameters(n, p, n_generated, n_rounds, verbose_results, verbose_progress)
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        durations.append(duration)
    plt.plot(n_generated_list, accuracies, label='accuracy')
    plt.plot(n_generated_list, precisions, label='precision')
    plt.plot(n_generated_list, recalls, label='recall')
    plt.plot(n_generated_list, f1s, label='f1')
    plt.title("Effect of n_generated on performance number of criterias = {}".format(n))
    plt.xlabel("n_generated")
    plt.ylabel("score")
    plt.legend()
    plt.savefig(os.path.join(output_folder, "score_n_generated_effect.png"), dpi=300)
    plt.show()
    
    plt.plot(n_generated_list, durations)
    plt.title("Duration of the for number of criterias = {}".format(n))
    plt.ylabel("duration")
    plt.xlabel("n_generated")
    plt.savefig(os.path.join(output_folder, "duration_n_generated_effect.png"), dpi=300)
    plt.show()
    
    
def plot_n_effect_random(n_generated=500, p=1, n_rounds= default_eval_rounds, 
                            n_list= default_n_list, 
                            verbose_results = False, verbose_progress = False):
    """
    Generates some configuration randomly and plots the effect of the
    number of generated data on the performance of the solver. 
    
    Arguments:
        n_egenrated: int -- number of generated data
        p: int -- number of profiles to be generated randomly
        n_rounds: int -- number of rounds of evaluation
        n_list: list -- list of n criterias to be tested and generated randomly
        verbose_results: bool -- if True, prints the results
        verbose_progress: bool -- if True, prints the progress of the training
    Returns:
        tuple -- (mean_accuracy, mean_precision, mean_recall, mean_f1)
    """
    accuracies = []
    precisions = []
    recalls = []
    f1s = []
    durations = []
    for n in tqdm(n_list, ascii=True, desc="Generating and evaluating"):
        acc, prec, rec, f1, duration = multi_eval_parameters(n, p, n_generated, n_rounds, verbose_results, verbose_progress)
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        durations.append(duration)
    plt.plot(n_list, accuracies, label='accuracy')
    plt.plot(n_list, precisions, label='precision')
    plt.plot(n_list, recalls, label='recall')
    plt.plot(n_list, f1s, label='f1')
    plt.title("Effect of n_generated on performance for n_generated = {}".format(n_generated))
    plt.xlabel("number of criterias")
    plt.ylabel("score")
    plt.legend()
    plt.savefig(os.path.join(output_folder, "score_n_effect.png"), dpi=300)
    plt.show()
    
    plt.plot(n_list, durations)
    plt.title("Mean duration of solving for n_generated = {}".format(n_generated))
    plt.ylabel("duration")
    plt.xlabel("number of criterias")
    plt.savefig(os.path.join(output_folder, "duration_n_effect.png"), dpi=300)
    plt.show()
    