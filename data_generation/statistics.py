import json
from collections import Counter
from pathlib import Path

from marshmallow_dataclass import class_schema

from data_generation.create_data import ExtendedOffer


def get_offer_metadata(filename: Path) -> ExtendedOffer:
    """Loads the offer JSON file and returns the offer metadata."""
    with open(filename, "r") as f:
        products_dict = json.load(f)
    return class_schema(ExtendedOffer)().load(products_dict)


def load_products(data_directory: Path):
    products = []
    for metadata_file in data_directory.glob("*.json"):
        if "reference" not in metadata_file.name:
            # print(metadata_file.name)
            metadata = get_offer_metadata(metadata_file)
            products.append(metadata)
    return products


def calc_statistics(products: list):
    # count number of offers per shop, use Counter
    shop_offers = Counter(p.shop_name for p in products)
    median_price = sum(p.price for p in products) / len(products)
    return dict(
        count_per_shop=shop_offers.most_common(10),
        total_shops=len(shop_offers),
        total_products=len(products),
        median_price=median_price,
    )


if __name__ == "__main__":
    path = Path("../data_10/")
    products = load_products(path)
    result = calc_statistics(products)
    print(json.dumps(result, indent=4))
