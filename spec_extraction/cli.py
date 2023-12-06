"""CLI interface for specification_extraction project.
"""

from config import PRODUCT_CATALOG_DIR
from spec_extraction import extraction_config
from spec_extraction.catalog_model import CATALOG_EXAMPLE
from spec_extraction.extraction import Parser
from spec_extraction.process import Processing


def main():  # pragma: no cover
    parser = Parser(specifications=extraction_config.monitor_spec)
    p = Processing(parser)
    p.extract_raw_specifications()

    p.find_mappings(CATALOG_EXAMPLE)
    p.merge_monitor_specs(PRODUCT_CATALOG_DIR)
