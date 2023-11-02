import json

import pytest

from spec_extraction import field_mappings


def test_field_mappings_load_from_disk(tmp_path):
    expected = {"shop1": {"key1": "key2"}}

    # prepare test file
    tmp_file = tmp_path / "test_field_mappings.json"
    with open(tmp_file, "w") as f:
        json.dump(expected, f)

    fm = field_mappings.FieldMappings(tmp_file)
    fm.load_from_disk()

    assert fm.mappings == expected


def test_field_mappings():
    expected = {"shop1": {"key1": "key2"}}

    fm = field_mappings.FieldMappings()
    fm.add_possible_mapping("shop1", "key2", "key1")
    fm.add_possible_mapping("shop2", "value", "completely different value")

    assert fm.mappings == expected


@pytest.mark.parametrize(
    "merchant_value, catalog_value, expected_score",
    [("test", "test", 100), ("test", "test2", 89), ("test", "test3", 89), ("test", "100", 0)],
)
def test_rate_mapping(merchant_value, catalog_value, expected_score):
    assert field_mappings.rate_mapping(merchant_value, catalog_value) == expected_score