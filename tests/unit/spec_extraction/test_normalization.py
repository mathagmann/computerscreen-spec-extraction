import pytest
from astropy import units as u

from spec_extraction import custom_quantities as cq
from spec_extraction.bootstrap import bootstrap as bootstrap_pipeline
from spec_extraction.normalization import convert_to_quantity
from spec_extraction.normalization import normalize_product_specifications
from spec_extraction.normalization import rescale_to_unit


@pytest.mark.parametrize(
    "value, unit, expected",
    [
        ("100", "Hz", 100 * u.Hz),
        ("1.45", "Hz", 1.45 * u.Hz),
        ("1.563", "km", 1.563 * u.km),
        ("24", "inch", 24 * cq.inch),
    ],
)
def test_convert_to_unit(value, unit, expected):
    converted = convert_to_quantity(value, unit)

    assert converted.value == expected.value
    assert converted.unit == expected.unit


def test_rescale_to_unit():
    rescaled = rescale_to_unit(100 * u.Hz, "kHz")

    assert rescaled.value == 0.1
    assert rescaled.unit == u.kHz


@pytest.mark.parametrize(
    "value, unit, expected_equality",
    [
        ("10000", "Hz", 10 * u.kHz),
        ("2", "Jahre", 24 * cq.month),
        ("1", "Jahr", 12 * cq.month),
        ("1,563", "km", 1563 * u.m),
        ("24", "Zoll", 24 * cq.inch),
    ],
)
def test_normalize_value(value, unit, expected_equality):
    normalized_value = convert_to_quantity(value, unit)

    assert normalized_value == expected_equality


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
    normalized_product = normalize_product_specifications(product_specifications)

    assert normalized_product["Helligkeit"] == 250 * u.candela / u.meter**2
    assert normalized_product["Bilddiagonale (cm)"] == 61 * u.cm

    print(processing.parser.nice_output(normalized_product))
