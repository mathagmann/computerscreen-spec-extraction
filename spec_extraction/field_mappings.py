import json
import os
from json import JSONDecodeError
from pathlib import Path

from loguru import logger
from thefuzz import fuzz

from spec_extraction.catalog_model import MonitorSpecifications


class FieldMappings:
    def __init__(self):
        self.mappings = {}
        self.filepath = Path(".") / "src" / "processing" / "auto_field_mappings.json"

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()

    def load(self):
        try:
            with open(self.filepath) as json_file:
                data = json.load(json_file)
                self.mappings = _remove_empty_mappings(data)

        except (FileNotFoundError, JSONDecodeError):
            os.makedirs(self.filepath.parent, exist_ok=True)
            self.mappings = {}

    def mapping_exists(self, shop_id, cat_key) -> bool:
        shop_mappings = self.get_mappings_shop(shop_id)
        if cat_key not in shop_mappings:
            return False
        return True

    def add_mapping(self, shop_id, cat_key, merch_key):
        """Adds mapping from merchant key to catalog key."""
        shop_mappings = self.mappings.get(shop_id, {})
        if cat_key not in shop_mappings:
            logger.info(f"Add mapping for '{shop_id}': {merch_key} -> {cat_key}")
            shop_mappings.update({cat_key: merch_key})
            self.mappings[shop_id] = shop_mappings

    def get_mappings(self):
        return self.mappings

    def get_mappings_shop(self, shop_id):
        return self.mappings.get(shop_id, {})

    def flush(self):
        # write mappings to file
        with open(self.filepath, "w") as outfile:
            filled_mappings = _fill_empty_mappings(self.mappings)
            json.dump(filled_mappings, outfile, indent=4, sort_keys=True)
        create_mapping_stats(filled_mappings)
        logger.debug(f"Flushed mappings to {str(self.filepath).split('/')[-1]}")

    def rate_mapping(self, merchant_value, catalog_value):
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


def _remove_empty_mappings(data):
    """Removes empty mappings from working data."""
    mappings = {}
    for shop, specs in data.items():
        mappings[shop] = {k: v for k, v in specs.items() if v is not None}
    return mappings
