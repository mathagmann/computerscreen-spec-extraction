import re

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

    def id(self):
        matched_groups = re.search(r"\d+", self.reference_file)
        return matched_groups.group(0)  # first number in filename


@dataclass
class CatalogProduct:
    name: str
    specifications: dict
