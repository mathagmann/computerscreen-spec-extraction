import json
from pathlib import Path
from typing import Generator

import marshmallow_dataclass
from loguru import logger
from marshmallow_dataclass import class_schema

from data_generation import model
from data_generation.create_data import PRODUCT_LISTING
from geizhals.geizhals_model import Product


def get_products_from_path(data_directory: Path) -> Generator[model.ExtendedOffer, None, None]:
    """Yields the next product offer with metadata from the given directory."""
    for metadata_file in data_directory.glob("*.json"):
        if not metadata_file.name.startswith("offer") or "reference" in metadata_file.name:
            continue

        with open(metadata_file, "r") as f:
            products_dict = json.load(f)
        yield class_schema(model.ExtendedOffer)().load(products_dict)


def get_product_listing(filename: Path = PRODUCT_LISTING) -> list[Product]:
    """Loads the product listing from the given file."""
    with open(filename, "r") as f:
        products_dict = json.load(f)
    products = [marshmallow_dataclass.class_schema(Product)().load(p) for p in products_dict]
    logger.debug(f"Loaded products from {filename}")
    return products
