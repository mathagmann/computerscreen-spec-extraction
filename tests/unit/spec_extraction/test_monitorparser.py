import copy
from pathlib import Path
from unittest import mock

import pytest

from spec_extraction import extraction_config
from spec_extraction.catalog_model import CATALOG_EXAMPLE
from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.extraction import Parser

REGEX_EXAMPLES = copy.deepcopy(CATALOG_EXAMPLE)
REGEX_EXAMPLES.pop(MonitorSpecifications.PORTS_HDMI.value)


@pytest.fixture
def monitor_parser():
    yield Parser(specifications=extraction_config.monitor_spec)


def test_parse_catalog_example(monitor_parser):
    catalog_example = Path(__file__).parent / "catalog_example.txt"
    expected = catalog_example.read_text()

    result = monitor_parser.parse(REGEX_EXAMPLES)
    text = monitor_parser.nice_output(result)

    assert isinstance(result, dict)
    assert text == expected.strip()


def test_colorspace_extraction(mock_synonyms, monitor_parser):
    example = {
        MonitorSpecifications.COLOR_SPACE_SRGB.value: "100% sRGB",
        MonitorSpecifications.COLOR_SPACE_DCIP3.value: "75% DCI-P3",
    }

    result = monitor_parser.parse(example)
    nice_output = monitor_parser.nice_output(result)

    assert result
    assert nice_output.startswith("Farbraum: ")
    assert nice_output.endswith("100% sRGB, 75% DCI-P3")


def test_parse_properly(mock_synonyms, monitor_parser):
    input_dict = REGEX_EXAMPLES

    with mock.patch("spec_extraction.extraction.load_synonyms", return_value={}):
        result = monitor_parser.parse(input_dict)

    for feature in input_dict.keys():
        assert result[feature]


def test_nice_output(monitor_parser):
    specs_dict = {
        MonitorSpecifications.DIAGONAL_INCH.value: {"value": "27", "unit": '"'},
        MonitorSpecifications.DIAGONAL_CM.value: {"value": "68.6", "unit": "cm"},
    }

    nice_output = monitor_parser.nice_output(specs_dict)

    assert nice_output.startswith("Diagonale: ")


def test_parser_for_each_feature(monitor_parser):
    for feature in MonitorSpecifications.list():
        assert feature in monitor_parser.parser
