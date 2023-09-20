from unittest import mock

import pytest

from processing.monitorparser import MonitorSpecifications
from processing.monitorparser import monitor_parser
from processing.process import CATALOG_EXAMPLE


@pytest.fixture
def mock_synonyms():
    def apply_synonyms(text: str) -> str:
        synonyms = {
            "zero frame": "Slim Bezel",
            "schmaler Rahmen": "Slim Bezel",
            "entspiegelt": "matt",
        }
        for key, value in synonyms.items():
            if key.lower() == text.lower():
                return value
        return text

    with mock.patch("processing.monitorparser.DataExtractor.apply_synonyms", apply_synonyms):
        yield


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

    with mock.patch("processing.monitorparser.DataExtractor.load_synonyms", return_value={}):
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
