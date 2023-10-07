from pathlib import Path

from minet import Scraper

SCRAPER_CONFIG_DIR = Path(__file__).parent / "config"
FIELDNAMES = ["title", "id", "shop", "path"]


MAPPING_CONFIG = {
    "mylemon.at": "mylemon.yaml",
    "Jacob Elektronik direkt (AT)": "jacobelektronik.yaml",
    "ElectronicShop24": "electronicshop24.yaml",
    "Proshop.at": "proshop_at.yaml",
    "TaufNaus": "bacomputer.yaml",  # duplicate
    "haym.infotec": "haym_infotec.yaml",
    "CSV-Direct.de": "csvdirect.yaml",
    "computeruniverse.at": "computeruniverse_at.yaml",
    "galaxus.at": "galaxus_at.yaml",
    "Universal Versand": "unito.yaml",
    "OTTO Österreich": "unito.yaml",
    "Future-X.at": "future_x.yaml",
    "playox (AT)": "playox.yaml",
    "office-partner (AT)": "playox.yaml",  # duplicate
    "e-tec.at": "e_tec.yaml",
    "DiTech.at": "e_tec.yaml",  # duplicate
    "1ashop.at": "1ashop.yaml",
    "BA-Computer": "bacomputer.yaml",
    "TechnikLaden": "bacomputer.yaml",  # duplicate
    "Amazon.at": "amazon.yaml",
    # "Waldbauer": "waldbauer.yaml", # no specs in html
    "Syswork": "syswork.yaml",
    "ARLT Computer": "arltcomputer.yaml",
    "I-CS": "ics.yaml",
    "Alternate.at": "alternateat.yaml",
    "Cyberport.at": "cyberportat.yaml",
    "Cyberport Stores Österreich": "cyberportat.yaml",
    # "CLS-IT": 720), # no useful data
    "ms-it-beratung": "msitberatung.yaml",
    "cw-mobile.de": "cwmobile.yaml",
    "bauguru": "bauguru.yaml",
    "HEINZSOFT (AT)": "heinzsoftat.yaml",
    "HiQ24": "hiq24.yaml",
    # "barax": "barax.yaml",
    # "ComStern.at": "comstern.yaml",
    "geizhals": "geizhals.yaml",
}


def extract_tabular_data(raw_html: str, shop_name: str) -> dict:
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
