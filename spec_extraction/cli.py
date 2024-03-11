"""CLI interface for specification_extraction project.
"""

from config import DATA_DIR
from config import PRODUCT_CATALOG_DIR
from spec_extraction.bootstrap import bootstrap
from spec_extraction.catalog_model import CATALOG_EXAMPLE
from spec_extraction.process import extract_raw_specifications


def main():  # pragma: no cover
    extract_raw_specifications(DATA_DIR)

    processing = bootstrap()
    processing.find_mappings(CATALOG_EXAMPLE)
    processing.merge_monitor_specs(PRODUCT_CATALOG_DIR)


if __name__ == "__main__":
    main()
