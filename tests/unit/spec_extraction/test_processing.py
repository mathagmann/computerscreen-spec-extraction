import pytest
from astropy import units as u

from spec_extraction.bootstrap import bootstrap as bootstrap_pipeline
from spec_extraction.catalog_model import CATALOG_EXAMPLE
from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.process import classify_specifications_with_ml
from spec_extraction.process import convert_machine_learning_labels_to_structured_data
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
def test_convert_machine_learning_labels_to_structured_data(labeled_data, expected):
    assert convert_machine_learning_labels_to_structured_data(labeled_data) == expected


def test_normalize_product():
    product_specifications = {
        "Bilddiagonale (Zoll)": {"value": "24", "unit": '"'},
        "Bilddiagonale (cm)": {"value": "61", "unit": "cm"},
        "Auflösung": {"width": "1920", "height": "1080"},
        "Helligkeit": {"value": "250", "unit": "cd/m²"},
        "Kontrast": {"dividend": "1000", "divisor": "1"},
        "Reaktionszeit": {"value": "1", "unit": "ms"},
        "Panel": "IPS",
        "Form": "gerade (flat)",
        "Beschichtung": "Blendfrei",
        "Seitenverhältnis": {"width": "16", "height": "9"},
        "Farbtiefe": {"value": "8", "unit": "bit"},
        "Bildwiederholfrequenz": {"value": "75", "unit": "Hz"},
        "Anschlüsse Klinke": {"count": "1", "type": "Line-Out"},
        "Farbe": ["Schwarz"],
        "VESA": {"width": "100", "height": "100"},
        "Stromversorgung": "AC-In (internes Netzteil)",
        "Gewicht": {"value": "3.6", "unit": "kg"},
        "Besonderheiten": [
            "Acer Adaptive Contrast Management (ACM)",
            "ComfyView",
            "Flimmerfrei-Technologie",
            "Abblend-Technologie",
            "527 x 296 mm aktiver Displaybereich",
        ],
        "Anschlüsse HDMI": {"count": "1"},
        "Blickwinkel horizontal": {"value": "178"},
        "Blickwinkel vertikal": {"value": "178"},
        "Farbraum sRGB": {"value": "99", "unit": "%", "name": "sRGB"},
        "Variable Synchronisierung": ["AMD FreeSync"],
        "Leistungsaufnahme (SDR)": {"value": "22", "unit": "W"},
        "Abmessungen": {"width": "54.1", "height": "6.6", "depth": "32.3", "unit": "cm"},
        "Kabel HDMI": {"count": "1", "name": "HDMI-Kabel"},
    }

    processing = bootstrap_pipeline()
    normalized_product = processing.normalize_product_specifications(product_specifications)

    assert normalized_product["Helligkeit"]["value"] == 250 * u.candela / u.meter**2
    assert normalized_product["Farbraum sRGB"]["value"] == 99 * u.percent

    print(processing.parser.nice_output(normalized_product))
