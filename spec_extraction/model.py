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


@dataclass
class CatalogProduct:
    name: str
    specifications: dict
