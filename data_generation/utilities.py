import json
from pathlib import Path

import marshmallow_dataclass
from loguru import logger
from marshmallow_dataclass import class_schema

from data_generation.create_data import PRODUCT_LISTING
from data_generation.create_data import ExtendedOffer
from geizhals.geizhals_model import Product


def get_offer_metadata(filename: Path) -> ExtendedOffer:
    """Loads the offer JSON file and returns the offer metadata."""
    with open(filename, "r") as f:
        products_dict = json.load(f)
    return class_schema(ExtendedOffer)().load(products_dict)


def load_products(data_directory: Path):
    products = []
    for metadata_file in data_directory.glob("*.json"):
        if not metadata_file.name.startswith("offer") or "reference" in metadata_file.name:
            continue
        metadata = get_offer_metadata(metadata_file)
        products.append(metadata)
    return products


def get_product_listing(filename: Path = PRODUCT_LISTING):
    """Loads the product listing from the given file."""
    with open(filename, "r") as f:
        products_dict = json.load(f)
    products = [marshmallow_dataclass.class_schema(Product)().load(p) for p in products_dict]
    logger.debug(f"Loaded products from {filename}")
    return products
