"""Details metric."""

import datasets
from sklearn.metrics import confusion_matrix

import evaluate


_DESCRIPTION = """
Returns the details with :
- True positives
- True negatives
- False positives
- False negatives
"""


_KWARGS_DESCRIPTION = """
Args:
    predictions (`list` of `int`): Predicted labels.
    references (`list` of `int`): Ground truth labels.
"""


class Details(evaluate.Metric):
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
        tn, fp, fn, tp = confusion_matrix(references, predictions).ravel()

        return {"TN": tn, "FP": fp, "FN": fn, "TP": tp}
