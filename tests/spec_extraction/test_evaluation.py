from spec_extraction.evaluation.evaluate import compare_specifications
from spec_extraction.evaluation.evaluate import evaluate_pipeline


def test_compare_specifications():
    expected_differences = 1
    specs = {
        "Auflösung": "1920 x 1080 Pixel",
        "Bildschirmdiagonale": "27 Zoll",
        "Bildschirmtechnologie": "IPS",
        "Bildschirmoberfläche": "matt",
    }
    reference = {"Auflösung": "1920 x 1080 Pixel", "Bildschirmdiagonale": "24 Zoll", "Bildschirmtechnologie": "IPS"}
    res = compare_specifications(reference, specs)

    assert res == expected_differences


def test_evaluate_pipeline():
    evaluate_pipeline()
