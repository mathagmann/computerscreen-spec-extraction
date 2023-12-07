"""CLI interface for specification_extraction project.
"""

from config import PRODUCT_CATALOG_DIR
from spec_extraction.bootstrap import bootstrap
from spec_extraction.catalog_model import CATALOG_EXAMPLE


def main():  # pragma: no cover
    processing = bootstrap()
    processing.extract_raw_specifications()

    processing.find_mappings(CATALOG_EXAMPLE)
    processing.merge_monitor_specs(PRODUCT_CATALOG_DIR)
