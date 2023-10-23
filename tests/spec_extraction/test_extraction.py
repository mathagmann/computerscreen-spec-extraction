import pytest

from spec_extraction.extraction import apply_synonyms
from spec_extraction.extraction_config import create_listing
from spec_extraction.extraction_config import create_pattern_structure


def test_data_extraction_pattern():
    expected = {
        "1_value": "10.00",
        "z_unit": "kg",
    }
    list_input = [
        "10.00 kg",
        r"(\d+.?\d*)\s?(kg|g)",
        ["1_value", "z_unit"],
    ]

    res = create_pattern_structure(*list_input)

    assert expected == res


# @pytest.mark.skip(reason="Not implemented yet")
def test_data_extraction_create_listing(mock_synonyms):
    expected = ["Slim Bezel"]
    text = "schmaler Rahmen"

    res = create_listing(text)

    assert expected == res


def test_data_extraction_apply_synonyms_to_list(mock_synonyms):
    expected = "Slim Bezel"
    text = "ErgoStand, Acer Adaptive Contrast Management (ACM), Zero Frame, an 3 Seiten ohne Blende"

    res = create_listing(text)

    assert res.__contains__(expected)


@pytest.mark.parametrize(
    "test_input,pattern,match_to,expected",
    [
        ("16:9", r"\d+:*\d+", None, "16:9"),
        (
            "100% sRGB, 83% Rec 2020, 97% DCI-P3, 99.5% Adobe RGB",
            r"(\d+[.\d]*%)\s*([[A-Za-z0-9]\S[A-Za-z0-9]+)",
            [["Wert", "Name"]],
            [
                {"Name": "sRGB", "Wert": "100%"},
                {"Name": "Rec", "Wert": "83%"},
                {"Name": "DCI", "Wert": "97%"},
                {"Name": "Adobe", "Wert": "99.5%"},
            ],
        ),
        (
            "71.3 cm x 51.25 cm x 19.86 cm",
            r"(\d+.?[\d]+)[^\d]*x[^\d]*(\d+.?[\d]+)[^\d]*x[^\d]*(\d+.?[\d]+)[^\d](cm)",
            ["Breite", "Höhe", "Tiefe", "Einheit"],
            {"Breite": "71.3", "Höhe": "51.25", "Tiefe": "19.86", "Einheit": "cm"},
        ),
    ],
)
def test_regex(test_input, pattern, expected, match_to, mock_synonyms):
    res = create_pattern_structure(test_input, pattern, match_to)

    assert res == expected


def test_synonyms(mock_synonyms):
    test_input = "entspiegelt"

    res = apply_synonyms(test_input)

    assert res == "matt"
