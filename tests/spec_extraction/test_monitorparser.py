from unittest import mock

from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.extraction_config import monitor_parser
from spec_extraction.process import CATALOG_EXAMPLE


def test_colorspace_extraction(mock_synonyms):
    example = {
        MonitorSpecifications.COLOR_SPACE_SRGB: "100% sRGB",
        MonitorSpecifications.COLOR_SPACE_DCIP3: "75% DCI-P3",
    }

    result = monitor_parser.parse(example)
    nice_output = monitor_parser.nice_output(result)

    assert result
    assert nice_output.startswith("Farbraum: ")
    assert nice_output.endswith("100% sRGB, 75% DCI-P3")


def test_parse_properly(mock_synonyms):
    input_dict = CATALOG_EXAMPLE

    with mock.patch("spec_extraction.extraction_config.load_synonyms", return_value={}):
        result = monitor_parser.parse(input_dict)

    for feature in input_dict.keys():
        assert result[feature.value]


def test_nice_output():
    data = {
        "Bilddiagonale (Zoll)": {"1_value": "27", "z_unit": '"'},
        "Bilddiagonale (cm)": {"1_value": "68.6", "z_unit": "cm"},
    }

    nice_output = monitor_parser.nice_output(data)

    assert nice_output.startswith("Diagonale: ")


def test_parser_for_each_feature():
    for feature in MonitorSpecifications.list():
        assert feature in monitor_parser.parser
