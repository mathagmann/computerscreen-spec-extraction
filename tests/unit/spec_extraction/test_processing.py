import pytest

from spec_extraction.catalog_model import CATALOG_EXAMPLE
from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.process import classify_specifications_with_ml
from spec_extraction.process import get_ml_specs
from token_classification import bootstrap as ml_bootstrap


def test_catalog_values_exist():
    min_expected_values = len(MonitorSpecifications.list()) * 0.95

    example_values = 0
    for feature in MonitorSpecifications.list():
        if feature in CATALOG_EXAMPLE:
            example_values += 1

    assert min_expected_values <= example_values


@pytest.mark.skip(reason="Requires equally trained model each time")
def test_classify_specifications():
    expected = {"count-hdmi": "1", "type-hdmi": "HDMI"}
    test_data = {
        "Anschlüsse - DisplayPort 1.2 (75Hz@1920x1080)": "1",
        "Anschlüsse - HDMI Version 1.4 (75Hz@1920x1080)": "1",
        "Anschlüsse - VGA (60Hz@1920x1080)": "1",
        "Anwendung": "stationär",
    }

    token_labeling = ml_bootstrap.bootstrap()
    result = classify_specifications_with_ml(test_data, token_labeling)

    assert result == expected


@pytest.mark.parametrize(
    "labeled_data,expected",
    [
        (
            {"count-hdmi": "1", "type-hdmi": "HDMI"},
            {MonitorSpecifications.PORTS_HDMI.value: {"value": "HDMI", "count": "1"}},
        ),
        (
            {"count-displayport": "1", "type-displayport": "DisplayPort", "version-displayport": "1.2"},
            {MonitorSpecifications.PORTS_DP.value: {"value": "DisplayPort", "count": "1", "version": "1.2"}},
        ),
        (
            {
                "count-displayport": "1",
                "type-displayport": "DisplayPort",
                "version-displayport": "1.2",
                "type-hdmi": "HDMI",
            },
            {
                MonitorSpecifications.PORTS_DP.value: {"value": "DisplayPort", "count": "1", "version": "1.2"},
                MonitorSpecifications.PORTS_HDMI.value: {"count": "1", "value": "HDMI"},
            },
        ),
    ],
)
def test_merge_ml_specs(labeled_data, expected):
    assert get_ml_specs(labeled_data) == expected
