# RuleBasedSolution_SemEval2018Task4
A rule-based appoach which outperforms almost all neural systems proposed in the shared task.

## Introduction
This script demonstrates how a simple rule-based entity-linking approach is able to achieve a remarkable result in SemEval 2018 Shared Task 4.

## How to run
* Get SemEval 2018 Task 4 official dataset and evaluation script from [here](https://github.com/emorynlp/semeval-2018-task4).
* Prepare a modified version of the original entity map text file where the characters are ranked by their frequency of occurrence in the training data.

## Evaluate
* Copy the output to a text file, e.g. `result.txt`
* Run the official evaluation script with `-ref.out -result.txt`

## Some Extra Work
This rule-based approach can be applied together with a neural network to achieve a even better result in the task. Code of the neural network is not included in this repo. But the evaluation scores of the combined approach are provided here as a reference.
