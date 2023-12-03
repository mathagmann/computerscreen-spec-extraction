import pytest

from spec_extraction.evaluation.evaluate import compare_strings
from spec_extraction.evaluation.evaluate import evaluate_pipeline


@pytest.mark.parametrize(
    "reference, specs, expected_correct, expected_all",
    [
        (
            {"Auflösung": "1920 x 1080 Pixel", "Bildschirmdiagonale": "27 Zoll", "Bildschirmtechnologie": "IPS"},
            {"Auflösung": "1920 x 1080 Pixel", "Bildschirmdiagonale": "24 Zoll", "Bildschirmtechnologie": "IPS"},
            2,
            3,
        ),
        (
            {"Bildschirmdiagonale": "27 Zoll", "DisplayPort Anschlüsse": "1", "Bildschirmtechnologie": "IPS"},
            {"Bildschirmdiagonale": "27 Zoll", "USB 3.0 Anschlüsse": "2", "Bildschirmtechnologie": "IPS"},
            2,
            4,
        ),
    ],
)
def test_compare_specifications(reference, specs, expected_correct, expected_all):
    count_correct, count_all = compare_strings(reference, specs)

    assert count_correct == expected_correct
    assert count_all == expected_all


def test_evaluate_pipeline():
    eval_correct, eval_all = evaluate_pipeline()

    assert 1 <= eval_correct <= eval_all
    attribute_precision = eval_correct / eval_all * 100
    assert attribute_precision > 0.02
