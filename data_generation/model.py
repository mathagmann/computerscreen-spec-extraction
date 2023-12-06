from typing import Optional

from marshmallow_dataclass import dataclass


@dataclass
class ExtendedOffer:
    shop_name: str
    price: float
    offer_link: str
    promotion_description: Optional[str]
    html_file: str
    reference_file: str

    @property
    def product_id(self) -> str:
        return self.reference_file.split("_")[2].split(".")[0]
