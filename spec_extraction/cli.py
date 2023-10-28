"""CLI interface for specification_extraction project.
"""
from pathlib import Path

from spec_extraction.extraction_config import MonitorParser
from spec_extraction.process import CATALOG_EXAMPLE
from spec_extraction.process import Processing

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def main():  # pragma: no cover
    dataset_name = "computerscreens2023"
    html_data_dir = DATA_DIR / dataset_name

    raw_specs_json_dir = DATA_DIR / f"{dataset_name}_raw_specs"
    specs_as_text_output_dir = DATA_DIR / f"{dataset_name}_raw_specs_as_text"
    product_catalog_dir = DATA_DIR / f"{dataset_name}_product_catalog"

    p = Processing(MonitorParser(), html_data_dir, raw_specs_json_dir, specs_as_text_output_dir)
    p.extract_raw_specifications()

    p.find_mappings(CATALOG_EXAMPLE)
    p.merge_monitor_specs(product_catalog_dir)
