import json
from pathlib import Path
from typing import Optional

from marshmallow_dataclass import dataclass


@dataclass
class Product:
    name: str
    link: str


@dataclass
class CategoryPage:
    url: str
    products: list[Product]
    next_page: Optional[str]


@dataclass
class Offer:
    shop_name: str
    price: float
    offer_link: str
    promotion_description: Optional[str]


@dataclass
class ProductDetail:
    name: str
    value: str


@dataclass
class ProductPage:
    url: str
    product_name: str
    product_details: list[ProductDetail]
    offers: list[Offer]

    def save_to_json(self, file: Path):
        raw_product = __class__.Schema().dump(self.__dict__)
        pretty_data = json.dumps(raw_product, indent=4, sort_keys=True)
        file.write_text(pretty_data)

    @staticmethod
    def load_from_json(file: Path):
        with open(file, "r") as f:
            data = json.load(f)
        return __class__.Schema().load(data)

    @staticmethod
    def reference_filename_from_id(id: str) -> str:
        return f"offer_reference_{id}.json"
