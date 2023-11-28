"""CLI interface for specification_extraction project.
"""

from config import PRODUCT_CATALOG_DIR
from spec_extraction.process import CATALOG_EXAMPLE
from spec_extraction.process import Processing


def main():  # pragma: no cover
    p = Processing()
    p.extract_raw_specifications()

    p.find_mappings(CATALOG_EXAMPLE)
    p.merge_monitor_specs(PRODUCT_CATALOG_DIR)
