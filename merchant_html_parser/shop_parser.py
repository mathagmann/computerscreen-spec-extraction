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


def parse_shop(raw_html: str, shop_name: str) -> dict:
    """Parse a shop page and store the result as JSON.

    Shop names from Geizhals are mapped to the corresponding parser configuration file.

    Raises
    ------
        ValueError: If a shop has no configured parser.

    Returns
    -------
    dict
        The extracted tabular specifications as key-value pairs.
    """
    parser_file = _get_parser_config(shop_name)
    scraper = Scraper(parser_file)
    specifications = scraper(raw_html)

    return {item["title"].rstrip(":"): item["description"] for item in specifications}


def _get_parser_config(shop_name: str) -> str:
    """Get the parser configuration file for a shop.

    Shop names from Geizhals are mapped to the corresponding parser configuration file.

    Raises:
        ValueError: If a shop has no configured parser.
    """
    try:
        parser_config = MAPPING_CONFIG[shop_name]
        shop_parser_conf = SCRAPER_CONFIG_DIR / parser_config
    except Exception:
        raise ValueError(f"Unknown shop name: {shop_name}")
    return str(shop_parser_conf)
