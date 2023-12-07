from pathlib import Path

from config import ROOT_DIR
from spec_extraction import extraction_config
from spec_extraction.extraction import Parser
from spec_extraction.field_mappings import FieldMappings
from spec_extraction.process import Processing


def bootstrap(
    specification_parser: list = extraction_config.monitor_spec,
    field_mappings: Path = ROOT_DIR / "spec_extraction" / "preparation" / "field_mappings.json",
) -> Processing:
    """Sets up default processing."""
    parser = Parser(specifications=specification_parser)
    field_mappings = FieldMappings(field_mappings)
    return Processing(parser=parser, field_mappings=field_mappings)
