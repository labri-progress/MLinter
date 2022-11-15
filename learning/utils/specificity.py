"""Specificity metric."""

import datasets
from sklearn.metrics import recall_score

import evaluate


_DESCRIPTION = """
Specificity (true negative rate) refers to the probability of a negative test, conditioned on truly being negative. It can be computed with:
Specificity = TN / (TN + FP)
 Where:
TN: True negative
FP: False positive
"""


_KWARGS_DESCRIPTION = """
Args:
    predictions (`list` of `int`): Predicted labels.
    references (`list` of `int`): Ground truth labels.
"""


class Accuracy(evaluate.Metric):
    def _info(self):
        return evaluate.MetricInfo(
            description=_DESCRIPTION,
            inputs_description=_KWARGS_DESCRIPTION,
            features=datasets.Features(
                {
                    "predictions": datasets.Value("int32"),
                    "references": datasets.Value("int32"),
                }
            ),
            citation=''
        )


    def _compute(self, predictions, references):
        return {
            "specificity": float(
                recall_score(references, predictions, pos_label=0)
            ),
        }
