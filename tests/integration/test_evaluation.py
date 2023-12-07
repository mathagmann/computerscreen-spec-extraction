from spec_extraction.evaluation.evaluate import calculate_evaluation_scores
from spec_extraction.evaluation.evaluate import evaluate_field_mappings
from spec_extraction.evaluation.evaluate import evaluate_pipeline


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
