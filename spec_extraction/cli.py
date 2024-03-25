"""Automatic setup of pipeline.

If a {name}_raw_specs exists, the pipeline will use the JSON files
inside to create computer screen specifications.

Otherwise, HTML files in {DATA_DIR} will be used to extract
these specifications from merchant pages (HTML).
"""
from config import DATA_DIR
from config import PRODUCT_CATALOG_DIR
from spec_extraction.bootstrap import bootstrap
from spec_extraction.catalog_model import CATALOG_EXAMPLE
from spec_extraction.process import extract_specifications_from_html

EXTRACT_FROM_HTML = False
RUN_MAIN_PIPELINE = False


def main():
    if EXTRACT_FROM_HTML:
        extract_specifications_from_html(DATA_DIR)

    # Initial setup
    processing = bootstrap()
    processing.find_mappings(CATALOG_EXAMPLE)

    if RUN_MAIN_PIPELINE:
        processing.merge_monitor_specs(PRODUCT_CATALOG_DIR)


if __name__ == "__main__":
    main()
