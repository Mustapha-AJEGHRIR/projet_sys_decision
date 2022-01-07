# This is a project for decision systems

Please feel free to read the file `MR-Sort-NCS.pdf` to understand the case.

# Inv-MR-Sort
MR-Sort is a decision system that sorts the items into classes based on their evaluation on each criteria using some parameters. The goal of Inverse MR-Sort is to learn those parameters from decisions that have been made. 
Please refere to the [paper](https://www.researchgate.net/publication/221367488_Learning_the_Parameters_of_a_Multiple_Criteria_Sorting_Method) for more details.
## File structure:
```
    Inv-MR-Sort
        ├── main.py                  # data generation and model testing
        ├── main.sh                  # executes `main.py` and saves its log
        ├── eval.py                  # evaluate the model performance
        ├── mip.py                   # Gurobi solver
        ├── data_generator.py        # generates data to output/data.csv
        ├── instance_generator.py    # generates instances with MR-sort
        ├── utils.py                 # helper functions
        └── config.py                # configuration file 
```
## Classes:
The Classes are given as integers from `1` to `MaxClasses`, where `MaxClasses` is the maximum number of classes in the data. `0` is reserved for instances that can't be in any Class.

## Data Structure :
Each instance of the problems should be stroed in a csv file with the following format:
| id  |  mark_1  |  mark_2  |mark_3 |   mark_4  |      class   |
|---- |----|----|----|--------------|-----------|
|  0  |  12  |  16  |    12         |     15    |     1     |
|  1  |  12  |  2  |     10         |     8     |     0    |
|  2  |  12  |  10  |    13         |     14    |     1    |

## Usage:
- Please refere to `config.py` to change the configuration that we have used.
- To generate data, go inside the folder, and run data_generator.py. It is possible to change `default_params` in `config.py` to generate different data, or `data_saving_path` to save the data to a different file.
```bash
cd Inv-MR-Sort
python data_generator.py
```
- To Use the model, use the following command, and the output will be saved to `Inv-MR-Sort/output/output.csv` and also printed at the end of the program.
```bash
cd Inv-MR-Sort
python main.py -d data_path
```

