"""CLI interface for specification_extraction project.
"""
from pathlib import Path

from config import DATA_DIR
from config import PRODUCT_CATALOG_DIR
from config import RAW_SPECIFICATIONS_DIR
from config import RAW_SPECIFICATIONS_TEXT_DIR
from spec_extraction.extraction_config import MonitorParser
from spec_extraction.process import CATALOG_EXAMPLE
from spec_extraction.process import Processing

PROJECT_ROOT = Path(__file__).parent.parent


def main():  # pragma: no cover
    p = Processing(MonitorParser(), DATA_DIR, RAW_SPECIFICATIONS_DIR, RAW_SPECIFICATIONS_TEXT_DIR)
    p.extract_raw_specifications()

    p.find_mappings(CATALOG_EXAMPLE)
    p.merge_monitor_specs(PRODUCT_CATALOG_DIR)
