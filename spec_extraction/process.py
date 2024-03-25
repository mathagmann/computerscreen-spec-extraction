import copy
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Generator
from typing import Protocol

import transformers
from loguru import logger
from marshmallow import EXCLUDE

import config
from data_generation.model import ExtendedOffer
from data_generation.utilities import get_products_from_path
from geizhals.geizhals_model import ProductPage
from spec_extraction import exceptions
from spec_extraction.catalog_model import ActivatedProperties
from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.field_mappings import MIN_FIELD_MAPPING_SCORE
from spec_extraction.field_mappings import rate_mapping
from spec_extraction.html_parser import shop_parser
from spec_extraction.model import CatalogProduct
from spec_extraction.model import RawProduct
from token_classification import utilities as ml_utils

REFERENCE_SHOP = "geizhals"

def pretty(dictionary: dict):
    return json.dumps(dictionary, indent=4, sort_keys=True)


class ParserProtocol(Protocol):
    def nice_output(self, parsed_data: dict) -> str:
        ...

    def parse(self, parsed_data: dict) -> dict:
        ...


class FieldMappingsProtocol(Protocol):
    def get_mappings_per_shop(self, shop_id):
        ...

    def add_mapping(self, shop_id: str, cat_key: str, merch_key: str, score: int = -1):
        ...

    def save_to_disk(self):
        ...


def extract_raw_specifications(data_dir: Path):
    logger.info("--- Extracting raw specifications... ---")

    os.makedirs(config.RAW_SPECIFICATIONS_DIR, exist_ok=True)
    offers = 0
    unparsed_shops = 0
    prev_screen = None
    for idx, monitor_extended_offer in enumerate(get_products_from_path(data_dir)):
        if prev_screen and (prev_screen.reference_file != monitor_extended_offer.reference_file):
            logger.info(f"{offers - unparsed_shops}/{offers} offers for {prev_screen.reference_file} parsed.")
            if offers and not unparsed_shops and prev_screen:
                logger.info(f"All shops parsed successfully: {prev_screen.reference_file}")

            unparsed_shops = 0
            offers = 0
            logger.debug(f"Processing next: {monitor_extended_offer.reference_file}")

        prev_screen = monitor_extended_offer
        offers += 1

        logger.debug(f"Extracting {idx} {monitor_extended_offer.html_file}")
        try:
            raw_monitor = html_json_to_raw_product(monitor_extended_offer, data_dir)
        except ValueError as e:
            logger.warning(e)
            unparsed_shops += 1
            continue
        except exceptions.ShopParserNotImplementedError:
            unparsed_shops += 1
            continue
        raw_monitor.save_to_json(config.RAW_SPECIFICATIONS_DIR / raw_monitor.filename)

    logger.info("--- Extracting raw specifications done ---")


class Processing:
    def __init__(
        self,
        parser: ParserProtocol,
        machine_learning: transformers.Pipeline,
        field_mappings: FieldMappingsProtocol,
        data_dir=None,
        machine_learning_enabled=True,
    ):
        self.parser = parser
        self.field_mappings = field_mappings
        self.machine_learning = machine_learning
        if data_dir is None:
            data_dir = config.DATA_DIR
        self.data_dir = data_dir  # Raw HTML data
        self.machine_learning_enabled = machine_learning_enabled

        logger.info(
            "Instantiate processing pipeline with settings:\n"
            f"Field mappings: {self.field_mappings.mappings_file}\n"
            f"Machine learning: {self.machine_learning_enabled}"
        )

    def find_mappings(self, catalog_example: Dict[MonitorSpecifications, str], value_score: bool = True):
        """Automatically finds mappings from extracted specification keys to unified catalog keys."""
        logger.info("--- Find mappings... ---")
        try:
            for idx, monitor_extended_offer in enumerate(get_products_from_path(self.data_dir)):
                try:
                    raw_monitor = html_json_to_raw_product(monitor_extended_offer, self.data_dir)
                except (ValueError, exceptions.ShopParserNotImplementedError):
                    continue
                for catalog_key, example_value in catalog_example.items():
                    # Tries to map a merchant key to a catalog key.
                    for merchant_key, merchant_text in raw_monitor.raw_specifications.items():
                        if not merchant_text:
                            continue

                        max_score_keys = rate_mapping(merchant_key, catalog_key)
                        if max_score_keys >= MIN_FIELD_MAPPING_SCORE:
                            logger.debug(f"Score keys '{max_score_keys}': {merchant_key}\t->\t{catalog_key}")
                            self.field_mappings.add_mapping(
                                raw_monitor.shop_name, catalog_key, merchant_key, max_score_keys
                            )
                            continue
                        if value_score:
                            max_score_values = rate_mapping(merchant_text, example_value)
                            if max_score_values >= MIN_FIELD_MAPPING_SCORE:
                                logger.debug(
                                    f"Score values '{max_score_values}': {merchant_key} ({merchant_text})\t"
                                    f"->\t{catalog_key} ({example_value})"
                                )
                                self.field_mappings.add_mapping(
                                    raw_monitor.shop_name, catalog_key, merchant_key, max_score_values - 5
                                )

                if idx % 1000 == 0:
                    logger.debug(f"Processed {idx} products.")
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

        shutil.rmtree(catalog_dir, ignore_errors=True)
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
            logger.debug(f"Merged specs for {product_name}:\n{self.parser.nice_output(copy.deepcopy(combined_specs))}")

            catalog_filename = CatalogProduct.filename_from_id(product_id)
            CatalogProduct(name=product_name, specifications=combined_specs, id=product_id).save_to_json(
                catalog_dir / catalog_filename
            )

    def extract_properties(self, raw_specification: dict, shop_name: str) -> dict[str, Any]:
        """Extracts structured properties from a single product.

        Combines both extraction methods:
        - Schema matching and regular expressions
        - Machine learning
        """
        machine_learning_specs = {}
        unified_specifications = self.extract_with_regex(raw_specification, shop_name)
        if self.machine_learning_enabled and shop_name != REFERENCE_SHOP:
            machine_learning_specs = self.extract_with_bert(raw_specification)
        specifications = unified_specifications | machine_learning_specs
        # logger.debug(f"Created specs:\n{self.parser.nice_output(specifications)}")
        return specifications

    def extract_with_regex(self, raw_specification: dict, shop_name: str) -> dict:
        """Extracts properties based on key matching and regular expressions.

        Relies on predefined mappings between merchant keys and catalog keys.

        Returns
        -------
        dict
            Returns structured specifications solely using keys from predefined catalog format.
        """
        monitor_specs = {}
        for catalog_key in ActivatedProperties:
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

    def extract_with_bert(self, raw_specification: dict) -> dict:
        """Extracts specifications with machine learning.

        Returns a dict with structured specifications.
        """
        labeled_data = classify_specifications_with_ml(raw_specification, self.machine_learning)

        machine_learning_specs = convert_machine_learning_labels_to_structured_data(labeled_data)

        if machine_learning_specs:
            logger.debug(f"ML specs extracted:\n{pretty(machine_learning_specs)}")
        return machine_learning_specs


def clean_text(text):
    """Removes invisible characters."""
    text = text.replace("cd/m2", "cd/m\u00b2")
    return text.replace("\u200b", "").strip()  # remove zero-width space


def convert_machine_learning_labels_to_structured_data(labeled_data: dict) -> dict:
    """Convert transformer model output into unified, structured specifications."""
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

    Logic: Shop with most properties wins.
    """
    combined_specs = {}

    # Value fusion based on most properties per shop wins
    shops_sorted_by_property_count = sorted(specs_per_shop.items(), key=lambda item: len(item[1]))
    for shopname, structured_specs in shops_sorted_by_property_count:
        combined_specs |= structured_specs
        print(f"{shopname} specs from '{shopname}':\n{pretty(structured_specs)}")

    # Enhance results using majority vote
    # Clear majority votes overwrite all other values
    # count properties per shop
    properties_per_shop = {}
    for shopname, structured_specs in shops_sorted_by_property_count:
        for key, value in structured_specs.items():
            if key not in properties_per_shop:
                properties_per_shop[key] = {}
            properties_per_shop[key][shopname] = value

    for key, values_per_shop in properties_per_shop.items():
        total_values = len(values_per_shop)
        if total_values == 1:
            continue

        value_counts = {}
        for shopname, value in values_per_shop.items():
            # make sure value is hashable
            if isinstance(value, dict):
                value = tuple(value.items())
            if isinstance(value, list):
                value = tuple(value)
            if value not in value_counts:
                value_counts[value] = 0
            value_counts[value] += 1

        sorted_votes = sorted(value_counts.items(), key=lambda item: item[1], reverse=True)

        limit_votes_for_majority = total_values // 2 + 1
        votes_for_majority = sorted_votes[0][1]

        # Skip update, if majority vote counts is less than 50% of all votes
        if limit_votes_for_majority > votes_for_majority:
            continue

        most_common_value = sorted_votes[0][0]

        # convert back to original type
        if isinstance(most_common_value, tuple):
            try:
                most_common_value = dict(most_common_value)
            except ValueError:
                most_common_value = list(most_common_value)

        # update by majority vote value
        if combined_specs[key] != most_common_value:
            if isinstance(most_common_value, dict) and not len(combined_specs[key]) <= len(most_common_value):
                continue
            logger.debug(f"Majority vote for {key}: '{most_common_value}' replaces '{combined_specs[key]}'")
            combined_specs[key] = most_common_value

    return combined_specs


def html_json_to_raw_product(monitor: ExtendedOffer, raw_data_dir: Path) -> RawProduct:
    """Converts HTML and JSON data into a RawProduct object."""
    html_code = (raw_data_dir / monitor.html_file).read_text()
    raw_specifications = shop_parser.extract_tabular_data(html_code, monitor.shop_name)
    if not raw_specifications:
        raise ValueError(f"Empty specifications for {monitor.html_file} from {monitor.shop_name}")

    # Retrieve name from Geizhals reference JSON
    geizhals_reference = ProductPage.load_from_json(raw_data_dir / monitor.reference_file)

    # turn data and raw_specifications into RawProduct
    data = monitor.__dict__
    data["raw_specifications"] = raw_specifications
    data["name"] = geizhals_reference.product_name
    data["raw_specifications_text"] = ml_utils.specs_to_text(raw_specifications)
    return RawProduct.Schema().load(data, unknown=EXCLUDE)


def get_all_raw_specs_per_screen(data_dir: str) -> Generator[RawProduct, None, None]:
    grouped_data_for_one_screen = []
    reference_name_for_screen = None
    for raw_product in iter_raw_product_files(data_dir):
        if reference_name_for_screen and reference_name_for_screen != raw_product.reference_file:
            # Reference file changed, so we have all data for one screen -> merge data
            yield grouped_data_for_one_screen

            grouped_data_for_one_screen = []
        reference_name_for_screen = raw_product.reference_file  # equal for all products of one screen
        grouped_data_for_one_screen.append(raw_product)


def iter_raw_product_files(data_dir: str) -> Generator[RawProduct, None, None]:
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
        yield RawProduct.load_from_json(data_dir / file.name)
