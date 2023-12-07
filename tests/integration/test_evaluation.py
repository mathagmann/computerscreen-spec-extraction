from unittest import mock

import pytest

from spec_extraction.evaluation.evaluate import calculate_evaluation_scores
from spec_extraction.evaluation.evaluate import evaluate_field_mappings
from spec_extraction.evaluation.evaluate import evaluate_pipeline


@pytest.fixture(scope="session", autouse=True)
def mock_machine_learning_model():
    """Mock machine learning model for testing."""
    with mock.patch("token_classification.bootstrap.bootstrap", return_value=mock.MagicMock()):
        yield


def test_evaluate_token_classifier():
    confusion_matrix, product_precision = evaluate_pipeline()

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
