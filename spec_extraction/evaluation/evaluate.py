import json

from jsoncomparison import Compare
from loguru import logger


def evaluate_field_mappings():
    pass


def evaluate_token_classifier():
    pass


def evaluate_pipeline():
    pass


def compare_specifications(reference_spec: dict, catalog_spec: dict) -> int:
    """Compares two dicts and outputs non-empty, different values."""
    diff = Compare().check(reference_spec, catalog_spec)
    wrong_entries = list(
        filter(lambda elem: "_message" in elem and "Values not equal" in elem["_message"], diff.values())
    )
    if wrong_entries:
        logger.warning(f"Diff:\n{json.dumps(wrong_entries, indent=4, sort_keys=True)}")
    return len(wrong_entries)
