from pathlib import Path
from unittest import mock

from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.extraction_config import monitor_parser
from spec_extraction.process import CATALOG_EXAMPLE


def test_parse_catalog_example():
    catalog_example = Path(__file__).parent / "catalog_example.txt"
    expected = catalog_example.read_text()

    result = monitor_parser.parse(CATALOG_EXAMPLE)
    text = monitor_parser.nice_output(result)

    assert isinstance(result, dict)
    assert text == expected.strip()


def test_colorspace_extraction(mock_synonyms):
    example = {
        MonitorSpecifications.COLOR_SPACE_SRGB.value: "100% sRGB",
        MonitorSpecifications.COLOR_SPACE_DCIP3.value: "75% DCI-P3",
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
        assert result[feature]


def test_nice_output():
    data = {"Bilddiagonale (Zoll)": {"value": "27", "unit": '"'}, "Bilddiagonale (cm)": {"value": "68.6", "unit": "cm"}}

    nice_output = monitor_parser.nice_output(data)

    assert nice_output.startswith("Diagonale: ")


def test_parser_for_each_feature():
    for feature in MonitorSpecifications.list():
        assert feature in monitor_parser.parser
