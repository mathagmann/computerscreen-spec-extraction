"""CLI interface for specification_extraction project.
"""
from spec_extraction.extraction_config import MonitorParser
from spec_extraction.process import CATALOG_EXAMPLE
from spec_extraction.process import Processing


def main():  # pragma: no cover
    print("This will do something")
    p = Processing(MonitorParser(), "interim", "processed")
    p.find_mappings(CATALOG_EXAMPLE)
    p.create_monitor_specs()
