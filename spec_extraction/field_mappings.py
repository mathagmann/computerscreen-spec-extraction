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
        MonitorSpecifications.DIMENSIONS.value: ["Abmessungen (BxHxT)", 100],
        MonitorSpecifications.PORTS_DVI.value: ["Anschl\u00fcsse", 100],
        MonitorSpecifications.PORTS_DP.value: ["Anschl\u00fcsse", 100],
        MonitorSpecifications.PORTS_HDMI.value: ["Anschl\u00fcsse", 100],
        MonitorSpecifications.PORTS_AUDIO.value: ["Audio", 100],
        MonitorSpecifications.PORTS_LAN.value: ["Weitere Anschl\u00fcsse", 100],
        MonitorSpecifications.PORTS_MINI_DP.value: ["Anschl\u00fcsse", 100],
        MonitorSpecifications.PORTS_USB_A.value: ["USB-Hub Out", 100],
        MonitorSpecifications.PORTS_USB_C.value: ["USB-Hub Out", 100],
        MonitorSpecifications.PORTS_VGA.value: ["Anschl\u00fcsse", 100],
        MonitorSpecifications.RESOLUTION.value: ["Aufl\u00f6sung", 100],
        MonitorSpecifications.PORTS_DISPLAY_OUT.value: ["Anschl\u00fcsse", 100],
        MonitorSpecifications.COATING.value: ["Beschichtung", 100],
        MonitorSpecifications.FEATURES.value: ["Besonderheiten", 100],
        MonitorSpecifications.DIAGONAL_INCH.value: ["Diagonale", 100],
        MonitorSpecifications.DIAGONAL_CM.value: ["Diagonale", 100],
        MonitorSpecifications.REFRESH_RATE.value: ["Bildwiederholfrequenz", 100],
        MonitorSpecifications.VIEWING_ANGLE_HOR.value: ["Blickwinkel", 100],
        MonitorSpecifications.VIEWING_ANGLE_VER.value: ["Blickwinkel", 100],
        MonitorSpecifications.EAN.value: [None, 100],
        MonitorSpecifications.ENERGY_EFFICIENCY.value: ["Energieeffizienzklasse SDR (A bis G)", 100],
        MonitorSpecifications.COLOR.value: ["Farbe", 100],
        MonitorSpecifications.COLOR_SPACE_ARGB.value: ["Farbraum", 100],
        MonitorSpecifications.COLOR_SPACE_DCIP3.value: ["Farbraum", 100],
        MonitorSpecifications.COLOR_SPACE_NTSC.value: ["Farbraum", 100],
        MonitorSpecifications.COLOR_SPACE_REC2020.value: ["Farbraum", 100],
        MonitorSpecifications.COLOR_SPACE_REC709.value: ["Farbraum", 100],
        MonitorSpecifications.COLOR_SPACE_SRGB.value: ["Farbraum", 100],
        MonitorSpecifications.COLOR_DEPTH.value: ["Farbtiefe", 100],
        MonitorSpecifications.FORM.value: ["Form", 100],
        MonitorSpecifications.WEIGHT.value: ["Gewicht", 100],
        MonitorSpecifications.HDR.value: ["HDR", 100],
        MonitorSpecifications.BRIGHTNESS.value: ["Helligkeit", 100],
        MonitorSpecifications.WARRANTY.value: ["Herstellergarantie", 100],
        MonitorSpecifications.ERGONOMICS_HEIGHT_ADJUSTABLE.value: ["Ergonomie", 100],
        MonitorSpecifications.CABLES_DVI.value: [None, 100],
        MonitorSpecifications.CABLES_DP.value: [None, 100],
        MonitorSpecifications.CABLES_HDMI.value: [None, 100],
        MonitorSpecifications.CABLES_AC_POWER.value: [None, 100],
        MonitorSpecifications.CABLES_VGA.value: [None, 100],
        MonitorSpecifications.CONTRAST.value: ["Kontrast", 100],
        MonitorSpecifications.CURVATURE.value: ["Form", 100],
        MonitorSpecifications.POWER_CONSUMPTION_SDR.value: ["Leistungsaufnahme", 100],
        MonitorSpecifications.POWER_CONSUMPTION_SLEEP.value: ["Leistungsaufnahme", 100],
        MonitorSpecifications.BRAND.value: [None, 100],
        MonitorSpecifications.ERGONOMICS_TILT_ANGLE.value: ["Ergonomie", 100],
        MonitorSpecifications.PANEL.value: ["Panel", 100],
        MonitorSpecifications.BEZEL_TOP.value: [None, 100],
        MonitorSpecifications.BEZEL_SIDE.value: [None, 100],
        MonitorSpecifications.BEZEL_BOTTOM.value: [None, 100],
        MonitorSpecifications.REACTION_TIME.value: ["Reaktionszeit", 100],
        MonitorSpecifications.ERGONOMICS_PIVOT_ANGLE.value: ["Ergonomie", 100],
        MonitorSpecifications.ASPECT_RATIO.value: ["Aufl\u00f6sung", 100],
        MonitorSpecifications.POWER_SUPPLY.value: ["Stromversorgung", 100],
        MonitorSpecifications.PORTS_THUNDERBOLT.value: ["Anschl\u00fcsse", 100],
        MonitorSpecifications.USB_HUB_OUT.value: ["USB-Hub Out", 100],
        MonitorSpecifications.USB_HUB_IN_USBB.value: ["USB-Hub In", 100],
        MonitorSpecifications.USB_HUB_IN_USBC.value: ["USB-Hub In", 100],
        MonitorSpecifications.VESA.value: ["VESA", 100],
        MonitorSpecifications.VARIABLE_SYNC.value: ["Variable Synchronisierung", 100],
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
