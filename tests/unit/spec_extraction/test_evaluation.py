import pytest

from spec_extraction.evaluation.evaluate import ConfusionMatrix
from spec_extraction.evaluation.evaluate import EvaluationScores
from spec_extraction.evaluation.evaluate import _calc_single_attribute_confusion_matrix
from spec_extraction.evaluation.evaluate import calculate_confusion_matrix


@pytest.mark.parametrize(
    "reference, extracted, expected_confusion_matrix, expected_eval_scores",
    [
        (
            {},
            {"attr1": "val_a"},
            ConfusionMatrix(true_positives=0, false_positives=1, false_negatives=0),
            EvaluationScores(precision=0, recall=0, f1_score=0),
        ),
        (
            {"attr1": "val_a"},
            {},
            ConfusionMatrix(true_positives=0, false_positives=0, false_negatives=1),
            EvaluationScores(precision=0, recall=0, f1_score=0),
        ),
        (
            {"attr1": "val_a"},
            {"attr1": "val_a"},
            ConfusionMatrix(true_positives=1, false_positives=0, false_negatives=0),
            EvaluationScores(precision=1, recall=1, f1_score=1),
        ),
        (
            {"attr1": "val_a", "attr2": "val_b", "attr3": "val_d"},
            {"attr1": "val_a", "attr2": "val_c", "attr3": "val_d"},
            ConfusionMatrix(true_positives=2, false_positives=1, false_negatives=1),
            EvaluationScores(precision=2 / 3, recall=2 / 3, f1_score=2 / 3),
        ),
        (
            {"attr1": "val_a", "attr2": "val_b"},
            {"attr1": "val_a", "attr4": "val_c"},
            ConfusionMatrix(true_positives=1, false_positives=1, false_negatives=1),
            EvaluationScores(precision=0.5, recall=0.5, f1_score=0.5),
        ),
        (
            {"attr1": "val_a", "attr2": "val_b", "attr3": "val_c"},
            {"attr1": "val_a", "attr3": "val_d"},
            ConfusionMatrix(true_positives=1, false_positives=1, false_negatives=2),
            EvaluationScores(precision=0.5, recall=1 / 3, f1_score=0.4),
        ),
    ],
)
def test_compare_specifications_confusion_matrix(reference, extracted, expected_confusion_matrix, expected_eval_scores):
    count = calculate_confusion_matrix(reference, extracted)

    assert count == expected_confusion_matrix
    assert count.eval_score == expected_eval_scores


@pytest.mark.parametrize(
    "reference, extracted, expected_confusion_matrix, expected_eval_scores",
    [
        (
            (None, None),
            ("attr1", "val_a"),
            ConfusionMatrix(true_positives=0, false_positives=1, false_negatives=0),
            EvaluationScores(precision=0, recall=0, f1_score=0),
        ),
        (
            ("attr1", "val_a"),
            (None, None),
            ConfusionMatrix(true_positives=0, false_positives=0, false_negatives=1),
            EvaluationScores(precision=0, recall=0, f1_score=0),
        ),
        (
            ("attr1", "val_a"),
            ("attr1", "val_a"),
            ConfusionMatrix(true_positives=1, false_positives=0, false_negatives=0),
            EvaluationScores(precision=1, recall=1, f1_score=1),
        ),
    ],
)
def test_calc_single_attribute_confusion_matrix(reference, extracted, expected_confusion_matrix, expected_eval_scores):
    count = _calc_single_attribute_confusion_matrix(reference, extracted)

    assert count == expected_confusion_matrix
    assert count.eval_score == expected_eval_scores


def test_calculate_evaluation_scores():
    evaluation = ConfusionMatrix(false_negatives=2, false_positives=1, true_positives=1)

    scores = evaluation.eval_score

    assert scores.precision == 0.5
    assert scores.recall == 1 / 3
    assert scores.f1_score == 0.4


def test_calculate_evaluation_scores_adv():
    evaluation = ConfusionMatrix(false_negatives=10, false_positives=0, true_positives=45)

    scores = evaluation.eval_score

    assert scores.precision == 1
    assert scores.recall == 45 / 55
    assert scores.f1_score == 0.9
