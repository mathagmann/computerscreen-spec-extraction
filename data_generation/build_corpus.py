import json

import marshmallow_dataclass
from loguru import logger

from data_generation.browser import ROOT_DIR
from data_generation.create_data import ExtendedOffer
from rule_based_parser import shop_parser


def build_corpus():
    """Creates a corpus from the raw data.

    The corpus is a list of strings, where each line is a specification
    from one merchant offer.

    Transforms the raw data into the corpus 'computer_screen_corpus.txt'
    """
    with open(ROOT_DIR / "corpus" / "computer_screen_corpus.txt", "w") as c:
        dir = ROOT_DIR / "data"
        offers_added = 0
        all_offers = 0
        for filename in dir.iterdir():
            if filename.suffix != ".json":
                continue
            all_offers += 1
            offer_schema = marshmallow_dataclass.class_schema(ExtendedOffer)()
            try:
                with open(filename, "r") as f:
                    offer_dict = json.load(f)
                offer = offer_schema.load(offer_dict)
                logger.debug(offer.shop_name)

                product_offer = ROOT_DIR / "data" / offer.html_file
                shop_html = product_offer.read_text()
                specification_dict = shop_parser.parse_shop(shop_html, offer.shop_name)
                if not specification_dict:
                    logger.error(f"Empty specification for {offer.shop_name}")
                    continue
            except Exception:
                continue

            logger.info(f"Extracted spec from {offer.shop_name}")
            specification_str = flatten_specification_dict(specification_dict)
            c.write(specification_str + "\n")
            offers_added += 1
    logger.debug(f"Wrote {offers_added} from {all_offers} offers to corpus")


def flatten_specification_dict(data: dict) -> str:
    """Transforms the specification key-value pairs into a string.

    Flattens the dictionary for further use in machine learning.

    Example:
        {"size": "27", "resolution": "1920x1080"} -> "size:27;resolution:1920x1080"
    """

    flattened_str = []
    for key, value in data.items():
        flattened_str.append(f"{key}:{value}")

    return ";".join(flattened_str)


if __name__ == "__main__":
    build_corpus()
