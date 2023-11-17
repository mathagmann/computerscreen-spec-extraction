import json

from config import PRODUCT_CATALOG_DIR
from spec_extraction.model import CatalogProduct


def get_catalog_filename(id_: str) -> str:
    return f"product_{id_}_catalog.json"


def get_catalog_product(id_: str) -> CatalogProduct:
    """Reads catalog product data for given product id.

    The ID is the number of retrieval.
    """
    with open(PRODUCT_CATALOG_DIR / get_catalog_filename(id_), "r") as f:
        return CatalogProduct.Schema().load(json.load(f))
