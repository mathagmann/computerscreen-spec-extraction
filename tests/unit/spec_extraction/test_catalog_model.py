from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.catalog_model import create_enabled_enum
from spec_extraction.catalog_model import disabled_members


def test_create_enabled_enum():
    defined_properties = len(MonitorSpecifications)
    excluded_properties = len(disabled_members)

    active_properties = create_enabled_enum(MonitorSpecifications, disabled_members)

    assert excluded_properties > 0
    assert defined_properties - excluded_properties == len(active_properties)
