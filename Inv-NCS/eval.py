from maxsat import MaxSATSolver
from data_generator import generate_data
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
from config import data_saving_path, solution_saving_path, dimacs_saving_path, gophersat_path
import config
from time import time
from matplotlib import pyplot as plt
from tqdm import tqdm
import os
import numpy as np
from pprint import pprint

output_folder = os.path.join(os.path.dirname(__file__), "output/")
os.makedirs(output_folder + "/n_list", exist_ok=True)
os.makedirs(output_folder + "/n_generated_list", exist_ok=True)
os.makedirs(output_folder + "/mu_list", exist_ok=True)


def eval_parameters(params: dict = config.params, verbose_results=True, verbose_progress=False) -> tuple:
    """
    Evaluates the parameters of the Inverse NCS problem. It trains the solver with
    some training data and then evaluates the performance of the solver on the test data.
    all the data is generated in random according the the parameters.
    
    Arguments:
        params: dict -- parameters of the Inverse NCS problem
        verbose_results: bool -- if True, prints the results
        # verbose_progress: bool -- if True, prints the progress of the training
    Returns:
        tuple -- (accuracy, precision, recall, f1)
    """

    data_test, data_train, correct_data_train = generate_data(params, balanced=True, verbose=False, save=False)
    test_classes = list(data_test["class"])

    solver = MaxSATSolver(data_train, None, dimacs_saving_path, gophersat_path)
    tik = time()
    solver.solve(save_solution=False, verbose=False)
    tok = time()
    duration = tok - tik

    # restoration rate
    train_preds = solver.predict(correct_data_train.iloc[:, :-1])
    restoration_rate = accuracy_score(correct_data_train["class"], train_preds)

    predicted_classes = solver.predict(data_test.iloc[:, :-1])  # [:,:-1] to remove the class column

    acc = accuracy_score(test_classes, predicted_classes)
    prec = precision_score(test_classes, predicted_classes, average="macro")
    rec = recall_score(test_classes, predicted_classes, average="macro")
    f1 = f1_score(test_classes, predicted_classes, average="macro")

    if True:
        print(f"\n\nParameters:")
        print("*" * 20)
        pprint(params)
        print()
        print(f"## Restoration rate : \t {restoration_rate*100}%")
        print(f"## Generalization Indexes :")
        print("=> Confusion Matrix :")
        mtrx = confusion_matrix(test_classes, predicted_classes).__str__()
        for line in mtrx.split("\n"):
            print("\t" + line)

        print("=> Accuracy :\t {:.2}".format(acc))
        print("=> Precision :\t {:.2}".format(prec))
        print("=> Recall :\t {:.2}".format(rec))
        print("=> F1 :\t {:.2}".format(f1))

    return acc, prec, rec, f1, duration

def multi_eval_parameters(
    n=9, p=3, n_generated=128, n_rounds=3, verbose_results=False, verbose_progress=False, mu=0.1
) -> tuple:
    """
    Evaluates the parameters of the Inverse NCS problem for n rounds. It trains the 
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
        params = config.get_random_params(n=n, p=p, n_learning_set=n_generated, mu=mu)
        acc, prec, rec, f1, duration = eval_parameters(params, verbose_results, verbose_progress)
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        durations.append(duration)
    mean_accuracy = sum(accuracies) / n_rounds
    mean_precision = sum(precisions) / n_rounds
    mean_recall = sum(recalls) / n_rounds
    mean_f1 = sum(f1s) / n_rounds
    mean_duration = sum(durations) / n_rounds
    return accuracies, precisions, recalls, f1s, durations


def plot_n_generated_effect_random(
    n=3,
    p=3,
    n_rounds=config.default_eval_rounds,
    n_generated_list=config.default_n_generated_list,
    verbose_results=False,
    verbose_progress=False,
):
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
        acc, prec, rec, f1, duration = multi_eval_parameters(
            n, p, n_generated, n_rounds, verbose_results, verbose_progress
        )
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        durations.append(duration)

    for measure in [
        ("accuracy", accuracies),
        ("precision", precisions),
        ("recall", recalls),
        ("f1", f1s),
        ("duration", durations),
    ]:
        if measure[0] != "duration":
            plt.ylim(0, 1)
        else:
            plt.figure()
        plt.plot(n_generated_list, np.mean(measure[1], axis=1), label=measure[0])
        plt.fill_between(
            n_generated_list, np.percentile(measure[1], 25, axis=1), np.percentile(measure[1], 75, axis=1), alpha=0.5
        )

        plt.title(f"Effect of number of reference assignments on {measure[0]}. n_criterias={n}, p={p}")
        plt.xlabel("Number of reference assignments")
        plt.ylabel(measure[0])
        plt.legend()
        plt.savefig(os.path.join(output_folder, f"n_generated_list/{measure[0]}_n_generated_list_effect.png"), dpi=300)
        # plt.show()


def plot_n_effect_random(
    n_generated=128,
    p=3,
    n_rounds=config.default_eval_rounds,
    n_list=config.default_n_list,
    verbose_results=False,
    verbose_progress=False,
):
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
        acc, prec, rec, f1, duration = multi_eval_parameters(
            n, p, n_generated, n_rounds, verbose_results, verbose_progress
        )
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        durations.append(duration)

    for measure in [
        ("accuracy", accuracies),
        ("precision", precisions),
        ("recall", recalls),
        ("f1", f1s),
        ("duration", durations),
    ]:
        if measure[0] != "duration":
            plt.ylim(0, 1)
        else:
            plt.figure()
        plt.plot(n_list, np.mean(measure[1], axis=1), label=measure[0])
        plt.fill_between(
            n_list, np.percentile(measure[1], 25, axis=1), np.percentile(measure[1], 75, axis=1), alpha=0.5
        )

        plt.title(f"Effect of number of criterias on {measure[0]}. n_generated = {n_generated} & p = {p}")
        plt.xlabel("number of criterias")
        plt.ylabel(measure[0])
        plt.legend()
        plt.savefig(os.path.join(output_folder, f"n_list/{measure[0]}_n_list_effect.png"), dpi=300)
        # plt.show()


def plot_mu_effect_random(
    n=5,
    n_generated=128,
    p=3,
    n_rounds=config.default_eval_rounds,
    mu_list=config.default_mu_list,
    verbose_results=False,
    verbose_progress=False,
):
    """
    Generates some configuration randomly and plots the effect of the
    number of generated data on the performance of the solver. 
    
    Arguments:
        n_egenrated: int -- number of generated data
        p: int -- number of profiles to be generated randomly
        n_rounds: int -- number of rounds of evaluation
        mu_list: list -- list of n criterias to be tested and generated randomly
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
    for mu in tqdm(mu_list, ascii=True, desc="Generating and evaluating"):
        acc, prec, rec, f1, duration = multi_eval_parameters(
            n, p, n_generated, n_rounds, verbose_results, verbose_progress, mu=mu
        )
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        durations.append(duration)

    for measure in [
        ("accuracy", accuracies),
        ("precision", precisions),
        ("recall", recalls),
        ("f1", f1s),
        ("duration", durations),
    ]:
        if measure[0] != "duration":
            plt.ylim(0, 1)
        else:
            plt.figure()
        plt.plot(mu_list, np.mean(measure[1], axis=1), label=measure[0])
        plt.fill_between(
            mu_list, np.percentile(measure[1], 25, axis=1), np.percentile(measure[1], 75, axis=1), alpha=0.5
        )

        plt.title(f"Effect of noise on {measure[0]}. n_generated = {n_generated} & p = {p}")
        plt.xlabel("noise percentage (mu)")
        plt.ylabel(measure[0])
        plt.legend()
        plt.savefig(os.path.join(output_folder, f"mu_list/{measure[0]}_mu_list_effect.png"), dpi=300)
        # plt.show()

