"""CLI interface for specification_extraction project.
"""
from pathlib import Path

from spec_extraction.extraction_config import MonitorParser
from spec_extraction.process import CATALOG_EXAMPLE
from spec_extraction.process import Processing


def main():  # pragma: no cover
    print("This will do something")

    base_path = Path("/Users/matthias/PycharmProjects/specification-extraction")

    data_dir = base_path / "data_10"
    output_dir_specs =  base_path / "out_10"
    output_dir_catalog = base_path / "out_10_catalog"

    p = Processing(MonitorParser(), data_dir, output_dir_specs)
    p.find_mappings(CATALOG_EXAMPLE)
    p.create_monitor_specs(output_dir_catalog)
