import csv
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import List

from processing.shop_product import RawShopProduct
from processing.shop_product import ShopParserNotImplementedError


def monitor_repeater(listing_file: str = "detailed_listing.csv"):
    """Returns a generator for all monitors."""
    detailed_listing = Path("raw") / listing_file
    with open(detailed_listing, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for entry in reader:
            entry["shops"] = json.loads(entry["shops"])
            yield RawMonitor(
                title=entry["title"], geizhals_link=entry["link"], raw_shops=entry["shops"], idx=entry["idx"]
            )


class RawMonitor:
    def __init__(self, title: str, geizhals_link: str, raw_shops: list, idx=None):
        self.title = title
        self.geizhals_link = geizhals_link
        self.idx = idx  # monitor index
        self._inter_shops = raw_shops
        self.geizhals: RawShopProduct = None
        self.shops: List[RawShopProduct] = []

    def load_geizhals_specifications(self):
        self.geizhals = RawShopProduct(shop_name="geizhals", link=self.geizhals_link, idx=-1, monitor_id=self.id)
        self.geizhals.get_raw_specifications()

    def load_raw_specifications(self):
        """Retrieves raw semi-structured specifications for each shop

        Shops without parser are skipped.
        """
        for shopdata in self._inter_shops:
            shop = RawShopProduct(
                shop_name=shopdata["name"], link=shopdata["link"], idx=shopdata["idx"], monitor_id=self.id
            )
            try:
                shop.get_raw_specifications()
            except ShopParserNotImplementedError:
                continue
            self.shops.append(shop)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title}, {self.geizhals_link}, {self.idx})"

    @property
    @lru_cache(maxsize=1)
    def id(self):
        gh_identifier = self.geizhals_link.split("/")[-1]
        gh_identifier = gh_identifier.rstrip(".html")
        return self.create_valid_filename(gh_identifier)

    @staticmethod
    def create_valid_filename(name) -> str:
        """Creates a valid filename."""
        s = str(name).strip().replace(" ", "_")
        s = re.sub(r"(?u)[^-\w.]", "", s)
        if s in {"", ".", ".."}:
            raise ValueError(f"Could not derive file name from '{name}'")
        return s
