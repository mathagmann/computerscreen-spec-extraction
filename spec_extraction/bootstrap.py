from pathlib import Path

import transformers

from config import ROOT_DIR
from spec_extraction import extraction_config
from spec_extraction.extraction import Parser
from spec_extraction.field_mappings import FieldMappings
from spec_extraction.process import Processing
from token_classification import bootstrap as ml_bootstrap


def bootstrap(
    specification_parser: list = extraction_config.monitor_spec,
    machine_learning_model: transformers.Pipeline = None,
    field_mappings: Path = ROOT_DIR / "spec_extraction" / "preparation" / "field_mappings.json",
) -> Processing:
    """Sets up default processing."""
    if machine_learning_model is None:
        # late evaluation of model checkpoint simplifies testing
        machine_learning_model = ml_bootstrap.bootstrap()
    parser = Parser(specifications=specification_parser)
    field_mappings = FieldMappings(field_mappings)
    field_mappings.load_from_disk()
    return Processing(parser=parser, machine_learning=machine_learning_model, field_mappings=field_mappings)
