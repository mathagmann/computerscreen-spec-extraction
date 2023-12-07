import json
from pathlib import Path
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

    def save_to_json(self, file: Path):
        offer = __class__.Schema().dump(self.__dict__)
        pretty_data = json.dumps(offer, indent=4, sort_keys=True)
        file.write_text(pretty_data)

    @staticmethod
    def load_from_json(file: Path):
        with open(file, "r") as f:
            data = json.load(f)
        return __class__.Schema().load(data)
