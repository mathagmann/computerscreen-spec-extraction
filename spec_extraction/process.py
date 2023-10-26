import json
import os
import re
from json import JSONDecodeError
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Generator

from jsoncomparison import Compare
from loguru import logger
from marshmallow import EXCLUDE
from thefuzz import fuzz

from data_generation import utilities
from geizhals.geizhals_model import ProductPage
from merchant_html_parser import shop_parser
from spec_extraction import exceptions
from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.extraction import clean_text
from spec_extraction.extraction_config import MonitorParser
from spec_extraction.model import CatalogProduct
from spec_extraction.model import RawProduct
from spec_extraction.raw_monitor import RawMonitor

CATALOG_EXAMPLE = {
    MonitorSpecifications.EAN.value: "4710886422812",
    MonitorSpecifications.DIAGONAL_INCH.value: '27 "',
    MonitorSpecifications.DIAGONAL_CM.value: "68.6 cm",
    MonitorSpecifications.BRAND.value: "Acer",
    MonitorSpecifications.RESOLUTION.value: "2560x1440",
    MonitorSpecifications.BRIGHTNESS.value: "250 cd/m²",
    MonitorSpecifications.CONTRAST.value: "1000:1",
    MonitorSpecifications.REACTION_TIME.value: "5 ms",
    MonitorSpecifications.VIEWING_ANGLE_HOR.value: "178",
    MonitorSpecifications.VIEWING_ANGLE_VER.value: "178",
    MonitorSpecifications.PANEL.value: "IPS",
    MonitorSpecifications.FORM.value: "gerade",
    MonitorSpecifications.CURVATURE.value: "1500R",
    MonitorSpecifications.COATING.value: "matt",
    MonitorSpecifications.HDR.value: "HDR10",
    MonitorSpecifications.ASPECT_RATIO.value: "16:9",
    MonitorSpecifications.COLOR_DEPTH.value: "8 bit",
    MonitorSpecifications.COLOR_SPACE_SRGB.value: "100% (sRGB)",
    MonitorSpecifications.COLOR_SPACE_ARGB.value: "100% (Adobe RGB)",
    MonitorSpecifications.COLOR_SPACE_DCIP3.value: "100% (DCI-P3)",
    MonitorSpecifications.COLOR_SPACE_REC709.value: "100% (Rec 709)",
    MonitorSpecifications.COLOR_SPACE_REC2020.value: "100% (Rec 2020)",
    MonitorSpecifications.COLOR_SPACE_NTSC.value: "72% (NTSC)",
    MonitorSpecifications.REFRESH_RATE.value: "144 Hz",
    MonitorSpecifications.VARIABLE_SYNC.value: "AMD FreeSync",
    MonitorSpecifications.PORTS_HDMI.value: "2 x HDMI",
    MonitorSpecifications.PORTS_DP.value: "1x DisplayPort",
    MonitorSpecifications.PORTS_MINI_DP.value: "1x Mini DisplayPort",
    MonitorSpecifications.PORTS_DVI.value: "1x DVI",
    MonitorSpecifications.PORTS_VGA.value: "1x VGA",
    MonitorSpecifications.PORTS_USB_C.value: "1x USB-C",
    MonitorSpecifications.PORTS_THUNDERBOLT.value: "1x Thunderbolt",
    MonitorSpecifications.PORTS_USB_A.value: "2x USB-A",
    MonitorSpecifications.PORTS_DISPLAY_OUT.value: " 1x DisplayPort-Out 1.2 (Daisy Chain)",
    MonitorSpecifications.PORTS_LAN.value: "1x Gb LAN (RJ-45)",
    MonitorSpecifications.PORTS_AUDIO.value: "1x Line-Out",
    MonitorSpecifications.USB_HUB_IN_USBC.value: "1x USB Typ C",
    MonitorSpecifications.USB_HUB_IN_USBB.value: "1x USB-B 3.0",
    MonitorSpecifications.USB_HUB_OUT.value: (
        "1x USB-C 3.0,  2x USB-A 3.0,  1x USB-A 3.0 (Schnellladefunktion USB BC " "1.2)"
    ),
    MonitorSpecifications.ERGONOMICS_HEIGHT_ADJUSTABLE.value: "15 cm",
    MonitorSpecifications.ERGONOMICS_TILT_ANGLE.value: "5 - 22\u00b0",
    MonitorSpecifications.ERGONOMICS_PIVOT_ANGLE.value: "90 - -90\u00b0",
    MonitorSpecifications.COLOR.value: "schwarz",
    MonitorSpecifications.VESA.value: "100 x 100 mm",
    MonitorSpecifications.WEIGHT.value: "10.00 kg",
    MonitorSpecifications.FEATURES.value: "Power Delivery",
    MonitorSpecifications.POWER_CONSUMPTION_SDR.value: "20 Watt",
    MonitorSpecifications.POWER_CONSUMPTION_SLEEP.value: "0.5 Watt",
    MonitorSpecifications.POWER_SUPPLY.value: "AC-In (internes Netzteil)",
    MonitorSpecifications.ENERGY_EFFICIENCY.value: "E",
    MonitorSpecifications.DIMENSIONS.value: "53.3 cm x 20.7 cm x 39 cm",
    MonitorSpecifications.CABLES_HDMI.value: "1x HDMI-Kabel",
    MonitorSpecifications.CABLES_DP.value: "1x DisplayPort-Kabel",
    MonitorSpecifications.CABLES_DVI.value: "1x DVI-Kabel",
    MonitorSpecifications.CABLES_VGA.value: "1x VGA-Kabel",
    MonitorSpecifications.CABLES_AC_POWER.value: "1x Strom-Kabel",
    MonitorSpecifications.WARRANTY.value: "2 Jahre",
}
FIELD_MAPPING_MIN_SCORE = 75


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


def _fill_empty_mappings(mappings: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
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


def rate_mapping(merchant_value, catalog_value):
    max_score = fuzz.ratio(merchant_value, catalog_value)
    for value in merchant_value.split(","):
        res = fuzz.ratio(value, catalog_value)
        if res > max_score:
            max_score = res
    return max_score


class Processing:
    def __init__(self, parser: MonitorParser, data_dir, raw_specs_output_dir, specs_as_text_output_dir):
        self.parser = parser
        self.data_dir = data_dir  # Raw HTML data
        self.raw_specs_output_dir = raw_specs_output_dir  # RAW Specifications as JSON with metadata
        self.specs_as_text_output_dir = specs_as_text_output_dir  # Input for NER labeling in Label Studio

    def extract_raw_specifications(self):
        logger.info("--- Extracting raw specifications... ---")

        os.makedirs(self.raw_specs_output_dir, exist_ok=True)
        for idx, raw_monitor in enumerate(next_raw_monitor(self.data_dir)):
            # Write raw specs to file in output_dir
            filename_specification = raw_monitor.html_file.rstrip(".html") + "_specification.json"

            product_dict = RawProduct.Schema().dump(raw_monitor)
            with open(self.raw_specs_output_dir / filename_specification, "w") as raw_monitor_file:
                json.dump(product_dict, raw_monitor_file, indent=4)

            # prepare plain text for NER labeling too
            os.makedirs(self.specs_as_text_output_dir, exist_ok=True)
            filename_specification = raw_monitor.html_file.rstrip(".html") + "_token_labeling.json"
            with open(self.specs_as_text_output_dir / filename_specification, "w") as raw_monitor_file:
                product_dict["raw_specifications"] = specs_to_text(product_dict["raw_specifications"])
                json.dump(product_dict, raw_monitor_file, indent=4)
        logger.info("--- Extracting raw specifications done. ---")

    def find_mappings(self, catalog_example: Dict[MonitorSpecifications, str]):
        logger.info("Find mappings...")
        check_example(catalog_example)

        with FieldMappings() as fm:
            for idx, raw_monitor in enumerate(next_raw_monitor(self.data_dir)):
                for catalog_key, example_value in catalog_example.items():
                    # Tries to map a merchant key to a catalog key.
                    for merchant_key, merchant_text in raw_monitor.raw_specifications.items():
                        if not merchant_text or fm.mapping_exists(raw_monitor.shop_name, catalog_key):
                            continue
                        merchant_text = clean_text(merchant_text)
                        if not merchant_text:
                            continue

                        # Check possible new mappings
                        catalog_text = catalog_example[catalog_key]
                        max_score = rate_mapping(merchant_text, catalog_text)
                        if max_score >= FIELD_MAPPING_MIN_SCORE:
                            logger.debug(f"Score '{max_score}': {merchant_text}\t->\t{catalog_text}")
                            fm.add_mapping(raw_monitor.shop_name, catalog_key, merchant_key)
                # logger.debug(f"Mappings for {monitor['title']} done")
                if idx % 1000 == 0:
                    fm.flush()
        fm.flush()

    def create_monitor_specs(self, catalog_dir: Path):
        """Extracts properties from raw specifications and merges them.

        The resulting product specifications are saved to a JSON file.

        Executes the following steps:
        - Schema matching
        - Property extraction
        - Value fusion (merge data from multiple shops)
        """
        logger.info("Creating monitor specifications...")
        self.parser.init()

        os.makedirs(catalog_dir, exist_ok=True)

        # Value fusion
        for grouped_specs in _group_of_specs(self.raw_specs_output_dir):
            combined_specs = {}
            product_name = None
            for raw_product in grouped_specs:
                product_name = raw_product.name

                structured_specs = self.parse_monitor_specs(raw_product.raw_specifications, raw_product.shop_name)

                logger.debug(
                    f"Parsing monitor '{product_name}' from '{raw_product.shop_name}':\n"
                    f"{pretty(raw_product.raw_specifications)}"
                )
                # Value fusion, last shop wins
                combined_specs: dict = combined_specs | structured_specs
                print(f"{product_name} specs from '{raw_product.shop_name}':\n{pretty(structured_specs)}")

            print(f"{product_name}\n{self.parser.nice_output(combined_specs)}")

            # Store structured product specifications in catalog directory
            matched_groups = re.search(r"\d+", raw_product.reference_file)
            product_nr = matched_groups.group(0)

            catalog_filename = f"product_{product_nr}_catalog.json"
            with open(catalog_dir / catalog_filename, "w") as file:
                catalog = dict(name=product_name, specifications=combined_specs)
                catalog_product = CatalogProduct.Schema().dump(catalog)
                file.write(pretty(catalog_product))
            logger.debug(f"Saved catalog ready product to {catalog_dir / catalog_filename}")

    def parse_monitor_specs(self, raw_specification: dict, shop_name: str) -> dict[str, Any]:
        """Extracts structured properties from raw specifications.

        Executes the following steps:
        - Schema matching
        - Property extraction
        """
        fm = FieldMappings()
        fm.load()
        monitor_specs = {}
        for catalog_key in MonitorSpecifications:
            catalog_key = catalog_key.value
            if catalog_key not in fm.get_mappings_shop(shop_name):
                continue

            merchant_key = fm.get_mappings_shop(shop_name)[catalog_key]
            if merchant_key not in raw_specification:
                continue

            merchant_value = raw_specification[merchant_key]
            merchant_value = clean_text(merchant_value)
            monitor_specs[catalog_key] = merchant_value
        return self.parser.parse(monitor_specs)


def check_example(catalog_example: dict):
    for feature in MonitorSpecifications.list():
        if feature not in catalog_example:
            logger.warning(f"Missing feature in catalog example, no auto mapping: '{feature}'")


def next_raw_monitor(raw_html_data_dir) -> Generator[RawMonitor, None, None]:
    products = utilities.load_products(raw_html_data_dir)
    for monitor in products:
        # load raw HTML
        with open(raw_html_data_dir / monitor.html_file) as file:
            html = file.read()

        try:
            raw_specifications = shop_parser.extract_tabular_data(html, monitor.shop_name)
        except exceptions.ShopParserNotImplementedError:
            continue

        if not raw_specifications:
            logger.debug(f"Empty specifications for {monitor.html_file} from {monitor.shop_name}")
            continue

        # Retrieve name from Geizhals reference JSON
        with open(raw_html_data_dir / monitor.reference_file) as geizhals_file:
            product_dict = json.load(geizhals_file)
            geizhals_reference = ProductPage.Schema().load(product_dict)
        product_name = geizhals_reference.product_name

        # turn data and raw_specifications into RawProduct
        data = monitor.__dict__
        data["raw_specifications"] = raw_specifications
        data["name"] = product_name
        raw_product = RawProduct.Schema().load(data, unknown=EXCLUDE)

        yield raw_product


def specs_to_text(raw_specifications: dict[str, Any]) -> str:
    """Converts raw specifications into a plain text string.

    Formats the text in the following format:

    <property name>: <property value>
    <property name>: <property value>
    """
    return "\n".join([f"{key}: {value}" for key, value in raw_specifications.items()])


def _group_of_specs(data_dir: str) -> list[RawProduct]:
    grouped_data_for_one_screen = []
    reference_name_for_screen = None
    for raw_product in _next_raw_specs(data_dir):
        if reference_name_for_screen and reference_name_for_screen != raw_product.reference_file:
            # Reference file changed, so we have all data for one screen -> merge data
            yield grouped_data_for_one_screen

            grouped_data_for_one_screen = []
        reference_name_for_screen = raw_product.reference_file  # equal for all products of one screen
        grouped_data_for_one_screen.append(raw_product)


def _next_raw_specs(data_dir: str) -> Generator[RawProduct, None, None]:
    """Yields raw specification with metadata from JSON files.

    The order of the files is not guaranteed, but specifications from the same
    monitor follow each other.

    Example:
    --------
    offer_1_3_specification.json
    offer_1_2_specification.json
    offer_1_1_specification.json
    offer_10_5_specification.json
    offer_10_3_specification.json
    """
    for file in sorted(data_dir.glob("*.json")):
        if not file.name.startswith("offer") or not file.name.endswith("specification.json"):
            continue

        logger.debug(f"Loading {file.name}...")
        with open(data_dir / file.name, "r") as f:
            products_dict = json.load(f)
        raw_product = RawProduct.Schema().load(products_dict)

        yield raw_product


if __name__ == "__main__":
    p = Processing(MonitorParser(), "interim", "processed")
    p.find_mappings(CATALOG_EXAMPLE)
    p.create_monitor_specs()
