import csv
import json
import os
from collections import namedtuple
from json import JSONDecodeError
from pathlib import Path
from typing import Any
from typing import Dict

import pandas
from jsoncomparison import Compare
from loguru import logger
from thefuzz import fuzz

from processing.extraction import clean_text
from processing.monitorparser import MonitorParser
from processing.monitorparser import MonitorSpecifications
from processing.raw_monitor import RawMonitor

Monitor = namedtuple("Monitor", "title, shop, raw_specs")

REFERENCE_SHOP = "geizhals"

CATALOG_EXAMPLE = {
    MonitorSpecifications.EAN: "4710886422812",
    MonitorSpecifications.DIAGONAL_INCH: '27 "',
    MonitorSpecifications.DIAGONAL_CM: "68.6 cm",
    MonitorSpecifications.BRAND: "Acer",
    MonitorSpecifications.RESOLUTION: "2560x1440",
    MonitorSpecifications.BRIGHTNESS: "250 cd/m²",
    MonitorSpecifications.CONTRAST: "1000:1",
    MonitorSpecifications.REACTION_TIME: "5 ms",
    MonitorSpecifications.VIEWING_ANGLE_HOR: "178",
    MonitorSpecifications.VIEWING_ANGLE_VER: "178",
    MonitorSpecifications.PANEL: "IPS",
    MonitorSpecifications.FORM: "gerade",
    MonitorSpecifications.CURVATURE: "1500R",
    MonitorSpecifications.COATING: "matt",
    MonitorSpecifications.HDR: "HDR10",
    MonitorSpecifications.ASPECT_RATIO: "16:9",
    MonitorSpecifications.COLOR_DEPTH: "8 bit",
    MonitorSpecifications.COLOR_SPACE_SRGB: "100% (sRGB)",
    MonitorSpecifications.COLOR_SPACE_ARGB: "100% (Adobe RGB)",
    MonitorSpecifications.COLOR_SPACE_DCIP3: "100% (DCI-P3)",
    MonitorSpecifications.COLOR_SPACE_REC709: "100% (Rec 709)",
    MonitorSpecifications.COLOR_SPACE_REC2020: "100% (Rec 2020)",
    MonitorSpecifications.COLOR_SPACE_NTSC: "72% (NTSC)",
    MonitorSpecifications.REFRESH_RATE: "144 Hz",
    MonitorSpecifications.VARIABLE_SYNC: "AMD FreeSync",
    MonitorSpecifications.PORTS_HDMI: "2 x HDMI",
    MonitorSpecifications.PORTS_DP: "1x DisplayPort",
    MonitorSpecifications.PORTS_MINI_DP: "1x Mini DisplayPort",
    MonitorSpecifications.PORTS_DVI: "1x DVI",
    MonitorSpecifications.PORTS_VGA: "1x VGA",
    MonitorSpecifications.PORTS_USB_C: "1x USB-C",
    MonitorSpecifications.PORTS_THUNDERBOLT: "1x Thunderbolt",
    MonitorSpecifications.PORTS_USB_A: "2x USB-A",
    MonitorSpecifications.PORTS_DISPLAY_OUT: " 1x DisplayPort-Out 1.2 (Daisy Chain)",
    MonitorSpecifications.PORTS_LAN: "1x Gb LAN (RJ-45)",
    MonitorSpecifications.PORTS_AUDIO: "1x Line-Out",
    MonitorSpecifications.USB_HUB_IN_USBC: "1x USB Typ C",
    MonitorSpecifications.USB_HUB_IN_USBB: "1x USB-B 3.0",
    MonitorSpecifications.USB_HUB_OUT: (
        "1x USB-C 3.0,  2x USB-A 3.0,  1x USB-A 3.0 (Schnellladefunktion USB BC " "1.2)"
    ),
    MonitorSpecifications.ERGONOMICS_HEIGHT_ADJUSTABLE: "15 cm",
    MonitorSpecifications.ERGONOMICS_TILT_ANGLE: "5 - 22\u00b0",
    MonitorSpecifications.ERGONOMICS_PIVOT_ANGLE: "90 - -90\u00b0",
    MonitorSpecifications.COLOR: "schwarz",
    MonitorSpecifications.VESA: "100 x 100 mm",
    MonitorSpecifications.WEIGHT: "10.00 kg",
    MonitorSpecifications.FEATURES: "Power Delivery",
    MonitorSpecifications.POWER_CONSUMPTION_SDR: "20 Watt",
    MonitorSpecifications.POWER_CONSUMPTION_SLEEP: "0.5 Watt",
    MonitorSpecifications.POWER_SUPPLY: "AC-In (internes Netzteil)",
    MonitorSpecifications.ENERGY_EFFICIENCY: "E",
    MonitorSpecifications.DIMENSIONS: "53.3 cm x 20.7 cm x 39 cm",
    MonitorSpecifications.CABLES_HDMI: "1x HDMI-Kabel",
    MonitorSpecifications.CABLES_DP: "1x DisplayPort-Kabel",
    MonitorSpecifications.CABLES_DVI: "1x DVI-Kabel",
    MonitorSpecifications.CABLES_VGA: "1x VGA-Kabel",
    MonitorSpecifications.CABLES_AC_POWER: "1x Strom-Kabel",
    MonitorSpecifications.WARRANTY: "2 Jahre",
}


def pretty(dictionary: dict):
    return json.dumps(dictionary, indent=4, sort_keys=True)


def compare_specifications(reference_spec: dict, catalog_spec: dict) -> int:
    """Compares two dicts and outputs non-empty, different values."""
    diff = Compare().check(reference_spec, catalog_spec)
    wrong_entries = list(
        filter(lambda elem: "_message" in elem and "Values not equal" in elem["_message"], diff.values())
    )
    if wrong_entries:
        logger.warning(f"Diff:\n{json.dumps(wrong_entries, indent=4, sort_keys=True)}")
    return len(wrong_entries)


class FieldMappings:
    def __init__(self):
        self.mappings = {}
        self.filepath = Path(".") / "src" / "processing" / "field_mappings.json"

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()

    def load(self):
        try:
            with open(self.filepath) as json_file:
                data = json.load(json_file)
                self.mappings = self._remove_empty_mappings(data)

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
            filled_mappings = self._fill_empty_mappings(self.mappings)
            json.dump(filled_mappings, outfile, indent=4, sort_keys=True)
        logger.debug(f"Flushed mappings to {str(self.filepath).split('/')[-1]}")

    @staticmethod
    def _fill_empty_mappings(mappings: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
        """Fills empty mappings with None to simplify manual improvements."""
        save_mappings = {}
        for shop in mappings:
            save_mappings[shop] = {}
            for cat_key in MonitorSpecifications.list():
                save_mappings[shop][cat_key] = mappings[shop].get(cat_key, None)
        return save_mappings

    @staticmethod
    def _remove_empty_mappings(data):
        """Removes empty mappings from working data."""
        mappings = {}
        for shop, specs in data.items():
            mappings[shop] = {k: v for k, v in specs.items() if v is not None}
        return mappings

    @staticmethod
    def rate_mapping(merchant_value, catalog_value):
        max_score = fuzz.ratio(merchant_value, catalog_value)
        for value in merchant_value.split(","):
            res = fuzz.ratio(value, catalog_value)
            if res > max_score:
                max_score = res
        return max_score


class Processing:
    FIELD_MAPPING_MIN_SCORE = 75

    def __init__(self, parser: MonitorParser, data_dir, out_dir):
        self.parser = parser
        self.data_dir = data_dir
        self.out_dir = out_dir

    def find_mappings(self, catalog_example: Dict[MonitorSpecifications, str]):
        logger.info("Find mappings...")
        self.check_example(catalog_example)

        with FieldMappings() as fm:
            for idx, monitor in enumerate(self._next_monitor()):
                merchant_specs = monitor["raw_specifications"]
                shop_id = monitor["shop"]
                for catalog_key, example_value in catalog_example.items():
                    # Tries to map a merchant key to a catalog key.
                    for merchant_key, merchant_text in merchant_specs.items():
                        if not merchant_text or fm.mapping_exists(shop_id, catalog_key):
                            continue
                        merchant_text = clean_text(merchant_text)
                        if not merchant_text:
                            continue

                        # Check possible new mappings
                        catalog_text = catalog_example[catalog_key]
                        max_score = fm.rate_mapping(merchant_text, catalog_text)
                        if max_score >= self.FIELD_MAPPING_MIN_SCORE:
                            logger.debug(f"Score '{max_score}': {merchant_text}\t->\t{catalog_text}")
                            fm.add_mapping(shop_id, catalog_key, merchant_key)
                # logger.debug(f"Mappings for {monitor['title']} done")
                if idx % 1000 == 0:
                    fm.flush()

    def check_example(self, catalog_example: dict):
        for feature in MonitorSpecifications.list():
            if feature not in catalog_example:
                logger.warning(f"Missing feature in catalog example, no auto mapping: '{feature}'")

    def create_monitor_specs(self):
        logger.info("Creating monitor specifications...")

        self.parser.init()

        differing_entries = 0
        parsed_features_count = 0
        reference_specs = {}
        for df in self._next_monitor_group():
            combined_specs = {}  # All specs for this monitor combined
            monitor_name = ""
            assert len(df) > 0
            for entry in df.itertuples():
                monitor = entry._asdict()
                with open(monitor["path"]) as json_file:
                    monitor["raw_specifications"] = json.load(json_file)["raw_specifications"]

                # Convert semi-structured text into structured specifications
                monitor = Monitor(title=monitor["title"], shop=monitor["shop"], raw_specs=monitor["raw_specifications"])

                monitor_specs = self._parse_monitor_specs(monitor)
                # Merge fields, but exclude Geizhals reference
                if monitor.shop == REFERENCE_SHOP:
                    reference_specs: dict = monitor_specs
                else:
                    logger.debug(
                        f"Parsing monitor '{monitor.title}' from '{monitor.shop}':\n" f"{pretty(monitor.raw_specs)}"
                    )
                    combined_specs: dict = combined_specs | monitor_specs
                    parsed_features_count += 1
                    print(f"{monitor.title} specs from '{monitor.shop}':\n{pretty(monitor_specs)}")
                    print(f"{monitor.title}\n{self.parser.nice_output(monitor_specs)}")
                monitor_name = monitor.title
            assert reference_specs  # Geizhals reference must exist

            self._store_created_specifications(monitor_name, combined_specs, reference_specs)

            logger.info(f"Combined specs {monitor_name}\n" f"{pretty(combined_specs)}")
            logger.info(f"Reference Specs\n" f"{pretty(reference_specs)}")
            differing_entries += compare_specifications(reference_specs, combined_specs)
            parsed_features_count += len(combined_specs)
        logger.info(f"Parsed features: {parsed_features_count}")
        if differing_entries > 0:
            logger.warning(f"Found {differing_entries} differing entries between combined and reference specs.")

    def _next_monitor(self) -> Dict[str, Any]:
        with open(self.data_dir / "semistructured.csv", "r") as csvfile:
            raw_data = csv.DictReader(csvfile)
            for monitor in raw_data:
                with open(monitor["path"]) as json_file:
                    monitor["raw_specifications"] = json.load(json_file)["raw_specifications"]
                yield monitor

    def _next_monitor_group(self) -> pandas.DataFrame:
        """Returns entries of a monitors, marked by same ID.

        A group contains the same monitor, but with specifications from different shops.
        """
        df = pandas.read_csv(self.data_dir / "semistructured.csv")
        for group in df.groupby("id"):
            _, df = group
            yield df

    def _parse_monitor_specs(self, monitor: Monitor) -> Dict:
        fm = FieldMappings()
        fm.load()
        monitor_specs = {}
        for catalog_key in MonitorSpecifications:
            catalog_key = catalog_key.value
            if catalog_key not in fm.get_mappings_shop(monitor.shop):
                continue

            merchant_key = fm.get_mappings_shop(monitor.shop)[catalog_key]
            if merchant_key not in monitor.raw_specs:
                continue

            merchant_value = monitor.raw_specs[merchant_key]
            merchant_value = clean_text(merchant_value)
            monitor_specs[catalog_key] = merchant_value
        return self.parser.parse(monitor_specs)

    def _store_created_specifications(self, monitor_name, created_specs, reference_specs):
        data = {"title": monitor_name, "created": created_specs, "reference": reference_specs}
        filename = RawMonitor.create_valid_filename(monitor_name)
        with open(filename, "w"):
            json.dump(data, self.out_dir / f"{filename}_specs.json", indent=4, sort_keys=True)


if __name__ == "__main__":
    p = Processing(MonitorParser(), "interim", "processed")
    p.find_mappings(CATALOG_EXAMPLE)
    p.create_monitor_specs()
