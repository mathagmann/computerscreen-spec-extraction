import pytest

from spec_extraction.evaluation.evaluate import ConfusionMatrix
from spec_extraction.evaluation.evaluate import calculate_confusion_matrix
from spec_extraction.evaluation.evaluate import calculate_evaluation_scores
from spec_extraction.evaluation.evaluate import evaluate_field_mappings
from spec_extraction.evaluation.evaluate import evaluate_pipeline


@pytest.mark.parametrize(
    "reference, extracted, expected_tp, expected_fp, expected_fn, expected_tn",
    [
        (
            {"Auflösung": "1920 x 1080 Pixel", "Bildschirmdiagonale": "27 Zoll", "Bildschirmtechnologie": "IPS"},
            {"Auflösung": "1920 x 1080 Pixel", "Bildschirmdiagonale": "24 Zoll", "Bildschirmtechnologie": "IPS"},
            2,
            1,
            0,
            0,
        ),
        (
            {"Bildschirmdiagonale": "27 Zoll", "DisplayPort Anschlüsse": "1", "Bildschirmtechnologie": "IPS"},
            {"Bildschirmdiagonale": "27 Zoll", "USB 3.0 Anschlüsse": "2", "Bildschirmtechnologie": "IPS"},
            2,
            0,
            1,
            1,
        ),
    ],
)
def test_compare_specifications(reference, extracted, expected_tp, expected_fp, expected_fn, expected_tn):
    count = calculate_confusion_matrix(reference, extracted)

    assert count.true_positives == expected_tp
    assert count.false_positives == expected_fp
    assert count.false_negatives == expected_fn
    assert count.true_negatives == expected_tn


def test_calculate_evaluation_scores():
    evaluation = ConfusionMatrix(true_negatives=50, false_negatives=10, false_positives=0, true_positives=45)

    scores = calculate_evaluation_scores(evaluation)

    assert scores.accuracy == 95 / 105
    assert scores.precision == 1
    assert scores.recall == 45 / 55
    assert scores.f1_score == 0.9


def test_evaluate_token_classifier():
    confusion_matrix, product_precision = evaluate_pipeline(ml_only=True)

    assert confusion_matrix


def test_evaluate_pipeline():
    confusion_matrix, product_precision = evaluate_pipeline()

    scores = calculate_evaluation_scores(confusion_matrix)
    assert scores.precision > 0.02
    assert scores.recall > 0.02


def test_evaluate_field_mappings():
    scores_manual_mapping, scores_auto_mapping = evaluate_field_mappings()

    assert scores_manual_mapping.precision > 0.5
    assert scores_auto_mapping.precision > 0.5
