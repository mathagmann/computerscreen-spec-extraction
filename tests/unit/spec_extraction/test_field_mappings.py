import json

import pytest

from spec_extraction import field_mappings


@pytest.fixture
def fm():
    return field_mappings.FieldMappings()


def test_field_mappings_load_from_disk(tmp_path):
    expected = {"shop1": {"key1": "key2"}}

    # prepare test file
    tmp_file = tmp_path / "test_field_mappings.json"
    with open(tmp_file, "w") as f:
        json.dump(expected, f)

    fm = field_mappings.FieldMappings(tmp_file)
    fm.load_from_disk()

    assert fm.mappings == expected


def test_field_mappings(fm):
    fm.add_mapping("shop1", "cat_key", "merch_key")
    fm.add_mapping("shop1", "cat_key2", "merch_key2")

    assert fm.mappings == {"shop1": {"cat_key": ("merch_key", -1), "cat_key2": ("merch_key2", -1)}}

    res = fm.get_mappings_per_shop("shop1")

    assert res == {"cat_key": "merch_key", "cat_key2": "merch_key2"}


def test_add_mappings_with_score(fm):
    fm.add_mapping("shop1", "cat_key", "merch_key", 50)

    assert fm.get_mappings_per_shop("shop1") == {"cat_key": "merch_key"}

    fm.add_mapping("shop1", "cat_key", "best_merchant_key", 80)
    fm.add_mapping("shop1", "cat_key", "invalid_merch_key", 70)

    assert fm.get_mappings_per_shop("shop1") == {"cat_key": "best_merchant_key"}


@pytest.mark.parametrize(
    "merchant_value, catalog_value, expected_score",
    [("test", "test", 100), ("test", "test2", 89), ("test", "test3", 89), ("test", "100", 0)],
)
def test_rate_mapping(merchant_value, catalog_value, expected_score):
    assert field_mappings.rate_mapping(merchant_value, catalog_value) == expected_score
