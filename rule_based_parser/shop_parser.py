from pathlib import Path

from minet import Scraper

SCRAPER_CONFIG_DIR = Path(__file__).parent / "config"
FIELDNAMES = ["title", "id", "shop", "path"]


MAPPING_CONFIG = {
    "mylemon.at": "mylemon.yaml",
    "ElectronicShop24": "electronicshop24.yaml",
    "Jacob Elektronik direkt": "jacobelektronik.yaml",
    "Proshop.at": "proshop_at.yaml",
    "haym.infotec": "haym_infotec.yaml",
    "computeruniverse.at": "computeruniverse_at.yaml",
    "galaxus.at": "galaxus_at.yaml",
    "Universal Versand": "unito.yaml",
    "OTTO Österreich": "unito.yaml",
    "Future-X.at": "future_x.yaml",
    "BA-Computer": "future_x.yaml",
    "e-tec.at": "e_tec.yaml",
    "DiTech.at": "e_tec.yaml",
    "barax": "barax.yaml",
    "1ashop.at": "1ashop.yaml",
    "ComStern.at": "comstern.yaml",
    "geizhals": "geizhals.yaml",
}

# load file contents into cache
PARSER_MAPPING = {}
for shop, filename in MAPPING_CONFIG.items():
    parser_file = SCRAPER_CONFIG_DIR / filename
    # PARSER_MAPPING[shop] = parser_file.read_text()
    PARSER_MAPPING[shop] = parser_file


def parse_shop(raw_html: str, shop_name: str) -> dict:
    """Parse a shop page and store the result as JSON.

    Shop names from Geizhals are mapped to the corresponding parser configuration file.

    Raises:
        ValueError: If a shop has no configured parser.
    """
    try:
        shop_parser_conf = PARSER_MAPPING[shop_name]
    except Exception:
        raise ValueError(f"Unknown shop name: {shop_name}")

    parser_file = SCRAPER_CONFIG_DIR / shop_parser_conf

    scraper = Scraper(str(parser_file))
    specifications = scraper(raw_html)

    return {item["title"].rstrip(":"): item["description"] for item in specifications}
