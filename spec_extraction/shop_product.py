import re
from functools import lru_cache
from pathlib import Path

import yaml
from minet import Scraper

from spec_extraction import exceptions

SHOP_PARSER_DIR = Path(__file__).parent / "extraction" / "shop_parser"
MAPPING_CONFIG = Path(__file__).parent / "extraction" / "shop_mappings.yaml"


@lru_cache(maxsize=32)
def load_conf_cached(yml_filename):
    """Returns mappings between Geizhals shop name to Scraper configuration files.

    Uses cache to prevent loading the same file multiple times.
    """
    with open(yml_filename) as file:
        config = yaml.safe_load(file)
    return config


class RawShopProduct:
    def __init__(self, shop_name, link, idx: int, monitor_id: str):
        self.shop_name = shop_name
        self.idx = idx
        self.link = link
        self.monitor_id = monitor_id
        self.raw_specifications = None

    def get_raw_specifications(self):
        filepath = self.shop_filepath
        if self.shop_name == "geizhals":
            filepath = self.monitor_filepath
        self.raw_specifications = parse_shop(self.shop_name, filepath)

    @property
    def shop_filepath(self):
        name = f"{self.idx:02d}_{self.shop_name}.html"
        valid_file_identifier = get_valid_filename(name)
        return Path("raw") / "shops" / self.monitor_id / valid_file_identifier

    @property
    def monitor_filepath(self):
        valid_file_identifier = get_valid_filename(self.monitor_id)
        return Path("raw") / "products" / f"{valid_file_identifier}.html"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.shop_name}, {self.link}, {self.idx})"


def parse_shop(gh_shop_name: str, shoppath: Path or str) -> dict:
    """Parse a shop page and store the result as JSON."""
    shop_mappings = load_conf_cached(MAPPING_CONFIG)["mappings"]
    if gh_shop_name not in shop_mappings:
        raise exceptions.ShopParserNotImplementedError(f"Unknown shop name: {gh_shop_name}")

    shop_parser = shop_mappings[gh_shop_name]
    parser_conf = load_conf_cached(SHOP_PARSER_DIR / f"{shop_parser}.yml")
    with open(shoppath, "rb") as file:
        html = file.read()

    scraper = Scraper(parser_conf)
    specifications = scraper(html)
    return {item["title"].rstrip(":"): item["description"] for item in specifications}


def get_valid_filename(name):
    """Creates a valid filename."""
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise ValueError(f"Could not derive file name from '{name}'")
    return s
