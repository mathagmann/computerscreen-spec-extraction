from unittest import mock

import pytest

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


@pytest.mark.skip(reason="Requires test data")
def test_evaluate_pipeline():
    confusion_matrix, product_precision = evaluate_pipeline()

    scores = confusion_matrix.eval_score
    assert scores.precision > 0.02
    assert scores.recall > 0.02


@pytest.mark.skip(reason="Requires test data")
def test_evaluate_field_mappings():
    scores_manual_mapping, scores_auto_mapping = evaluate_field_mappings()

    assert scores_manual_mapping.precision > 0.5
    assert scores_auto_mapping.precision > 0.5
