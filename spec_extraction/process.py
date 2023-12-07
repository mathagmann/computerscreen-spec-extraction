import json
import os
import re
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Generator
from typing import Protocol

from loguru import logger
from marshmallow import EXCLUDE

import config
from data_generation.model import ExtendedOffer
from data_generation.utilities import get_products_from_path
from geizhals.geizhals_model import ProductPage
from spec_extraction import exceptions
from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.field_mappings import FieldMappings
from spec_extraction.html_parser import shop_parser
from spec_extraction.model import CatalogProduct
from spec_extraction.model import RawProduct
from spec_extraction.utilities import get_catalog_filename
from token_classification import token_classifier
from token_classification import utilities as ml_utils


def pretty(dictionary: dict):
    return json.dumps(dictionary, indent=4, sort_keys=True)


class ParserProtocol(Protocol):
    def nice_output(self, parsed_data: dict) -> str:
        ...

    def parse(self, parsed_data: dict) -> dict:
        ...


class Processing:
    def __init__(self, parser: ParserProtocol, field_mappings: Path, data_dir=None):
        self.parser = parser
        self.field_mappings = FieldMappings(field_mappings)
        self.port_classifier = token_classifier.setup()
        if data_dir is None:
            data_dir = config.DATA_DIR
        self.data_dir = data_dir  # Raw HTML data
        self.field_mappings.load_from_disk()

    def extract_raw_specifications(self):
        logger.info("--- Extracting raw specifications... ---")

        os.makedirs(config.RAW_SPECIFICATIONS_DIR, exist_ok=True)
        for idx, monitor_extended_offer in enumerate(get_products_from_path(self.data_dir)):
            logger.debug(f"Extracting {idx} {monitor_extended_offer.html_file}")
            try:
                raw_monitor = html_json_to_raw_product(monitor_extended_offer, self.data_dir)
            except exceptions.ShopParserNotImplementedError:
                continue

            save_raw_specifications(config.RAW_SPECIFICATIONS_DIR, raw_monitor)
        logger.info("--- Extracting raw specifications done ---")

    def find_mappings(self, catalog_example: Dict[MonitorSpecifications, str]):
        """Automatically finds mappings from extracted specification keys to unified catalog keys."""
        logger.info("--- Find mappings... ---")
        try:
            for idx, monitor_extended_offer in enumerate(get_products_from_path(self.data_dir)):
                try:
                    raw_monitor = html_json_to_raw_product(monitor_extended_offer, self.data_dir)
                except exceptions.ShopParserNotImplementedError:
                    continue
                for catalog_key, example_value in catalog_example.items():
                    # Tries to map a merchant key to a catalog key.
                    for merchant_key, merchant_text in raw_monitor.raw_specifications.items():
                        if not merchant_text or self.field_mappings.mapping_exists(raw_monitor.shop_name, catalog_key):
                            continue

                        self.field_mappings.add_possible_mapping(raw_monitor.shop_name, catalog_key, merchant_key)
                if idx % 1000 == 0:
                    self.field_mappings.save_to_disk()
        finally:
            self.field_mappings.save_to_disk()
        logger.info("--- Find mappings done ---")

    def merge_monitor_specs(self, catalog_dir: Path):
        """Extracts properties from raw specifications and merges them.

        The resulting product specifications are saved to a JSON file.

        Executes the following steps:
        - Schema matching
        - Property extraction
        - Value fusion (merge data from multiple shops)
        """
        logger.info("Creating monitor specifications...")

        os.makedirs(catalog_dir, exist_ok=True)
        for grouped_specs_single_screen in get_all_raw_specs_per_screen(config.RAW_SPECIFICATIONS_DIR):
            # Handle specifications for one product

            # Steps: Schema matching and extraction
            product_data = {}
            product_name = None
            product_id = None
            for raw_product in grouped_specs_single_screen:
                if not product_name or not product_id:
                    product_name = raw_product.name
                    product_id = raw_product.id

                structured_specs = self.extract_properties(raw_product.raw_specifications, raw_product.shop_name)
                product_data[raw_product.shop_name] = structured_specs

            # Step: Value fusion, last shop wins
            combined_specs = value_fusion(product_data)

            store_product_for_catalog(combined_specs, product_name, product_id, catalog_dir)

    def extract_properties(
        self, raw_specification: dict, shop_name: str, enable_enhancement: bool = True
    ) -> dict[str, Any]:
        """Extracts structured properties from a single product.

        Relies on field mappings and optional machine learning enhancement.
        """
        unified_specifications = self.extract_structured_specifications(raw_specification, shop_name)

        machine_learning_specs = {}
        if enable_enhancement:
            machine_learning_specs = self.extract_with_bert(raw_specification)
            logger.debug(f"ML specs from '{shop_name}':\n{pretty(machine_learning_specs)}")

        specifications = unified_specifications | machine_learning_specs
        logger.info(f"Created specs:\n{self.parser.nice_output(specifications)}")
        return specifications

    def extract_with_bert(self, raw_specification: dict) -> dict:
        """Extracts specifications with machine learning.

        Returns a dict with structured specifications.
        """
        labeled_data = classify_specifications_with_ml(raw_specification, self.port_classifier)
        return get_ml_specs(labeled_data)

    def extract_structured_specifications(self, raw_specification: dict, shop_name: str) -> dict:
        """Returns structured specifications based on predefined catalog format."""
        monitor_specs = {}
        for catalog_key in MonitorSpecifications:
            catalog_key = catalog_key.value
            mapping_per_shop = self.field_mappings.get_mappings_per_shop(shop_name)
            if catalog_key not in mapping_per_shop:
                continue

            merchant_key = mapping_per_shop[catalog_key]
            if merchant_key not in raw_specification:
                continue

            merchant_value = raw_specification[merchant_key]
            merchant_value = clean_text(merchant_value)
            monitor_specs[catalog_key] = merchant_value
        unified_specifications = self.parser.parse(monitor_specs)
        return unified_specifications


def clean_text(text):
    """Removes invisible characters."""
    text = text.replace("cd/m2", "cd/m\u00b2")
    return text.replace("\u200b", "").strip()  # remove zero-width space


def get_ml_specs(labeled_data: dict) -> dict:
    """Merges ML specifications into unified specifications."""
    port_mappings = {
        "hdmi": MonitorSpecifications.PORTS_HDMI.value,
        "displayport": MonitorSpecifications.PORTS_DP.value,
        "usb-a": MonitorSpecifications.PORTS_USB_A.value,
        "usb-c": MonitorSpecifications.PORTS_USB_C.value,
    }

    # maps ML output to product catalog dict for a port
    value_mappings = {"type-{port}": "value", "count-{port}": "count", "version-{port}": "version"}

    ml_specs = {}
    for short_port_name, unified_port_name in port_mappings.items():
        port_values = {}
        for value_key, catalog_sub_key in value_mappings.items():
            ml_label_name = value_key.format(port=short_port_name)
            if ml_label_name in labeled_data:
                port_values[catalog_sub_key] = labeled_data[ml_label_name]

        if port_values:
            if "count" in port_values:
                port_values["count"] = re.search(r"\d+", port_values["count"])
            port_values["count"] = "1"

            # Dismiss ports with version 0
            if port_values["count"] == "0":
                continue

            ml_specs[unified_port_name] = port_values

    return ml_specs


def classify_specifications_with_ml(specifications: dict, classify_func) -> dict:
    """Classifies specifications with ML and returns data"""
    specification_text = ml_utils.specs_to_text(specifications)
    labeled_data = classify_func(specification_text)
    return ml_utils.process_labels(labeled_data)


def value_fusion(specs_per_shop: dict[str, dict]) -> dict:
    """Merges specifications from multiple shops into one dict.

    Logic: Last shop wins.
    """
    combined_specs = {}
    for shopname, structured_specs in specs_per_shop.items():
        combined_specs |= structured_specs
        print(f"{shopname} specs from '{shopname}':\n{pretty(structured_specs)}")
    return combined_specs


def store_product_for_catalog(specifications: dict, product_name: str, product_nr: int, catalog_dir: Path):
    catalog_filename = get_catalog_filename(product_nr)
    with open(catalog_dir / catalog_filename, "w") as file:
        catalog = dict(name=product_name, specifications=specifications)
        catalog_product = CatalogProduct.Schema().dump(catalog)
        file.write(pretty(catalog_product))
    logger.debug(f"Saved catalog ready product to {catalog_dir / catalog_filename}")


def html_json_to_raw_product(monitor: ExtendedOffer, raw_data_dir: Path) -> RawProduct:
    with open(raw_data_dir / monitor.html_file) as file:
        html = file.read()

    raw_specifications = shop_parser.extract_tabular_data(html, monitor.shop_name)
    if not raw_specifications:
        logger.warning(f"Empty specifications for {monitor.html_file} from {monitor.shop_name}")

    # Retrieve name from Geizhals reference JSON
    with open(raw_data_dir / monitor.reference_file) as geizhals_file:
        product_dict = json.load(geizhals_file)
        geizhals_reference = ProductPage.Schema().load(product_dict)
    product_name = geizhals_reference.product_name

    # turn data and raw_specifications into RawProduct
    data = monitor.__dict__
    data["raw_specifications"] = raw_specifications
    data["name"] = product_name
    data["raw_specifications_text"] = ml_utils.specs_to_text(raw_specifications)

    return RawProduct.Schema().load(data, unknown=EXCLUDE)


def save_raw_specifications(output_dir: Path, raw_monitor: RawProduct):
    raw_spec_filename = raw_monitor.html_file.rstrip(".html") + "_specification.json"
    product_dict = RawProduct.Schema().dump(raw_monitor)
    with open(output_dir / raw_spec_filename, "w") as raw_monitor_file:
        json.dump(product_dict, raw_monitor_file, indent=4)


def get_all_raw_specs_per_screen(data_dir: str) -> Generator[RawProduct, None, None]:
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
