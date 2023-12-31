import copy
import json
import os
from json import JSONDecodeError
from pathlib import Path

from loguru import logger
from thefuzz import fuzz

from spec_extraction.catalog_model import MonitorSpecifications

MIN_FIELD_MAPPING_SCORE = 75


class FieldMappings:
    def __init__(self, mappings_file: Path = None):
        self.mappings = {}
        self.mappings_file = mappings_file

    def get_mappings_per_shop(self, shop_id) -> dict[str, str]:
        """Remove scores and return mappings for a shop."""
        res = copy.deepcopy(self.mappings.get(shop_id, {}))
        for cat_key, value in res.items():
            merch_key, _ = value
            res[cat_key] = merch_key
        return res

    def add_mapping(self, shop_id: str, cat_key: str, merch_key: str, score: int = -1):
        """Adds mapping from merchant key to catalog key."""
        shop_mappings = self.mappings.get(shop_id, {})
        try:
            current_score = shop_mappings[cat_key][1]
        except KeyError:
            current_score = 0

        if cat_key not in shop_mappings:
            logger.info(f"Add mapping for '{shop_id}': {merch_key} -> {cat_key} ({score=})")
            shop_mappings.update({cat_key: (merch_key, score)})
            self.mappings[shop_id] = shop_mappings
        elif score > current_score:
            logger.info(f"Updated mapping for '{shop_id}': {merch_key} -> {cat_key} ({score=})")
            shop_mappings.update({cat_key: (merch_key, score)})
            self.mappings[shop_id] = shop_mappings

    def load_from_disk(self):
        """Loads field mappings from file."""
        try:
            with open(self.mappings_file) as json_file:
                data = json.load(json_file)
                self.mappings = _strip_empty_mappings(data)
        except (FileNotFoundError, JSONDecodeError):
            os.makedirs(self.mappings_file.parent, exist_ok=True)
            self.mappings = {}

    def save_to_disk(self):
        """Saves field mappings to file."""
        with open(self.mappings_file, "w") as outfile:
            filled_mappings = _fill_empty_mappings(self.mappings)
            json.dump(filled_mappings, outfile, indent=4, sort_keys=True)
        create_mapping_stats(filled_mappings)
        logger.debug(f"Flushed mappings to {str(self.mappings_file).split('/')[-1]}")


def rate_mapping(merchant_value, catalog_value):
    max_score = fuzz.ratio(merchant_value, catalog_value)
    for value in merchant_value.split(","):
        res = fuzz.ratio(value, catalog_value)
        if res > max_score:
            max_score = res
    return max_score


def create_mapping_stats(mappings: dict[str, dict[str, str]]) -> int:
    """Counts and Returns automatically mapped properties."""
    non_empty_mappings = 0
    total_possible_mappings = 0
    for shop in mappings:
        for cat_key in mappings[shop]:
            if mappings[shop][cat_key]:
                non_empty_mappings += 1
            total_possible_mappings += 1
    logger.info(
        f"{non_empty_mappings}/{total_possible_mappings} properties automatically mapped for {len(mappings)} shops"
    )
    return non_empty_mappings


def _fill_empty_mappings(mappings: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """Fills empty mappings with None to simplify manual improvements."""
    save_mappings = {}
    for shop in mappings:
        save_mappings[shop] = {}
        for cat_key in MonitorSpecifications.list():
            save_mappings[shop][cat_key] = mappings[shop].get(cat_key, None)
    return save_mappings


def _strip_empty_mappings(data):
    """Removes empty mappings from working data."""
    mappings = {}
    for shop, specs in data.items():
        mappings[shop] = {k: v for k, v in specs.items() if v is not None}
    return mappings
