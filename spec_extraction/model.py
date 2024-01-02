import json
import re
from pathlib import Path
from typing import Any

from marshmallow_dataclass import dataclass


@dataclass
class RawProduct:
    name: str
    raw_specifications: dict
    raw_specifications_text: str
    shop_name: str
    price: float
    html_file: str
    offer_link: str
    reference_file: str

    @property
    def id(self):
        matched_groups = re.search(r"\d+", self.reference_file)
        return matched_groups.group(0)  # first number in filename

    def save_to_json(self, file: Path):
        raw_product = __class__.Schema().dump(self.__dict__)
        pretty_data = json.dumps(raw_product, indent=4, sort_keys=True)
        file.write_text(pretty_data)

    @staticmethod
    def load_from_json(file: Path):
        """Reads catalog product data for given product id.

        The ID is the number of retrieval.
        """
        with open(file, "r") as f:
            data = json.load(f)
        return __class__.Schema().load(data)

    @property
    def filename(self):
        return f"{self.html_file.rstrip('.html')}_specification.json"


@dataclass
class CatalogProduct:
    """
    Parameters
    ----------
    name
        Human-friendly name of the product.
    specifications:
        Where the allowed key are one of the property names from MonitorSpecifications enum.
    id
        The ID of the product.
    """

    name: str
    specifications: dict[str, Any]
    id: str

    def save_to_json(self, file: Path):
        catalog_product = __class__.Schema().dump(self.__dict__)
        pretty_data = json.dumps(catalog_product, indent=4, sort_keys=True)
        file.write_text(pretty_data)

    @staticmethod
    def load_from_json(file: Path):
        with open(file, "r") as f:
            data = json.load(f)
        return __class__.Schema().load(data)

    @staticmethod
    def filename_from_id(product_id: str) -> str:
        return f"product_{product_id}_catalog.json"
