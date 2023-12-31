import copy
import json
import os
from json import JSONDecodeError
from pathlib import Path

from loguru import logger
from thefuzz import fuzz

from spec_extraction.catalog_model import MonitorSpecifications

MIN_FIELD_MAPPING_SCORE = 75

GEIZHALS_REFERENCE_MAPPING = {
    "geizhals": {
        "Abmessungen": ["Abmessungen (BxHxT)", 100],
        "Anschl\u00fcsse DVI": ["Anschl\u00fcsse", 100],
        "Anschl\u00fcsse DisplayPort": ["Anschl\u00fcsse", 100],
        "Anschl\u00fcsse HDMI": ["Anschl\u00fcsse", 100],
        "Anschl\u00fcsse Klinke": ["Audio", 100],
        "Anschl\u00fcsse LAN": ["Weitere Anschl\u00fcsse", 100],
        "Anschl\u00fcsse Mini DisplayPort": ["Anschl\u00fcsse", 100],
        "Anschl\u00fcsse USB-A": ["USB-Hub Out", 100],
        "Anschl\u00fcsse USB-C": ["USB-Hub Out", 100],
        "Anschl\u00fcsse VGA": ["Anschl\u00fcsse", 100],
        "Aufl\u00f6sung": ["Aufl\u00f6sung", 100],
        "Ausg\u00e4nge Display": ["Anschl\u00fcsse", 100],
        "Beschichtung": ["Beschichtung", 100],
        "Besonderheiten": ["Besonderheiten", 100],
        "Bilddiagonale (Zoll)": ["Diagonale", 100],
        "Bilddiagonale (cm)": ["Diagonale", 100],
        "Bildwiederholfrequenz": ["Bildwiederholfrequenz", 100],
        "Blickwinkel horizontal": ["Blickwinkel", 100],
        "Blickwinkel vertikal": ["Blickwinkel", 100],
        "EAN": [None, 100],
        "Energieeffizienzklasse": ["Energieeffizienzklasse SDR (A bis G)", 100],
        "Farbe": ["Farbe", 100],
        "Farbraum Adobe RGB": ["Farbraum", 100],
        "Farbraum DCI-P3": ["Farbraum", 100],
        "Farbraum NTSC": ["Farbraum", 100],
        "Farbraum REC 2020": ["Farbraum", 100],
        "Farbraum REC 709": ["Farbraum", 100],
        "Farbraum sRGB": ["Farbraum", 100],
        "Farbtiefe": ["Farbtiefe", 100],
        "Form": ["Form", 100],
        "Gewicht": ["Gewicht", 100],
        "HDR": ["HDR", 100],
        "Helligkeit": ["Helligkeit", 100],
        "Herstellergarantie": ["Herstellergarantie", 100],
        "H\u00f6henverstellbar": ["Ergonomie", 100],
        "Kabel DVI": [None, 100],
        "Kabel DisplayPort": [None, 100],
        "Kabel HDMI": [None, 100],
        "Kabel Strom": [None, 100],
        "Kabel VGA": [None, 100],
        "Kontrast": ["Kontrast", 100],
        "Kr\u00fcmmung": ["Form", 100],
        "Leistungsaufnahme (SDR)": ["Leistungsaufnahme", 100],
        "Leistungsaufnahme (Sleep)": ["Leistungsaufnahme", 100],
        "Marke": [None, 100],
        "Neigungswinkelbereich": ["Ergonomie", 100],
        "Panel": ["Panel", 100],
        "Rahmenst\u00e4rke oben": [None, 100],
        "Rahmenst\u00e4rke seitlich": [None, 100],
        "Rahmenst\u00e4rke unten": [None, 100],
        "Reaktionszeit": ["Reaktionszeit", 100],
        "Schwenkwinkelbereich": ["Ergonomie", 100],
        "Seitenverh\u00e4ltnis": ["Aufl\u00f6sung", 100],
        "Stromversorgung": ["Stromversorgung", 100],
        "Thunderbolt": ["Anschl\u00fcsse", 100],
        "USB-Hub Ausgang": ["USB-Hub Out", 100],
        "USB-Hub Eing\u00e4nge USB-B": ["USB-Hub In", 100],
        "USB-Hub Eing\u00e4nge USB-C": ["USB-Hub In", 100],
        "VESA": ["VESA", 100],
        "Variable Synchronisierung": ["Variable Synchronisierung", 100],
    }
}


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
            logger.info(f"Updated mapping for '{shop_id}': {merch_key} -> {cat_key} ({current_score=} -> {score=})")
            shop_mappings.update({cat_key: (merch_key, score)})
            self.mappings[shop_id] = shop_mappings

    def load_from_disk(self, mapping_path: Path = None):
        """Loads field mappings from file."""
        if mapping_path is None:
            mapping_path = self.mappings_file

        try:
            with open(mapping_path) as json_file:
                dynamic_mappings = json.load(json_file)
                extended_mappings = dynamic_mappings | GEIZHALS_REFERENCE_MAPPING
                self.mappings = _strip_empty_mappings(extended_mappings)
        except (FileNotFoundError, JSONDecodeError):
            os.makedirs(mapping_path.parent, exist_ok=True)
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
