from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.process import CATALOG_EXAMPLE


def test_catalog_values_exist():
    min_expected_values = len(MonitorSpecifications.list()) * 0.95

    example_values = 0
    for feature in MonitorSpecifications.list():
        if feature in CATALOG_EXAMPLE:
            example_values += 1

    assert min_expected_values <= example_values
