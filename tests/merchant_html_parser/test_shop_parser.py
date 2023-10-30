from pathlib import Path

import pytest
from loguru import logger

from data_generation.utilities import get_products_from_path
from merchant_html_parser import shop_parser
from merchant_html_parser.shop_parser import extract_tabular_data

TEST_DATA_DIR = Path("tests") / "merchant_html_parser" / "test_data"

top30 = [
    ("mylemon.at", "mylemon_product_offer.html"),
    ("Jacob Elektronik direkt (AT)", "jacob_electronic_product_offer.html"),
    ("ElectronicShop24", "electronicshop24_product_offer.html"),
    ("Proshop.at", "proshop_product_offer.html"),
    ("TaufNaus", "taufnaus_product_offer.html"),
    ("galaxus.at", "galaxus_product_offer.html"),
    ("haym.infotec", "hayminfotec_product_offer.html"),
    ("CSV-Direct.de", "csvdirect_product_offer.html"),
    ("Future-X.at", "futurex_product_offer.html"),
    ("playox (AT)", "playox_product_offer.html"),
    ("office-partner (AT)", "officepartner_product_offer.html"),
    ("e-tec.at", "etec_product_offer.html"),
    ("DiTech.at", "ditech_product_offer.html"),
    ("1ashop.at", "1ashop_product_offer.html"),
    ("BA-Computer", "bacomputer_product_offer.html"),
    ("TechnikLaden", "technikladen_product_offer.html"),
    ("Amazon.at", "amazon_product_offer.html"),
    # ("Waldbauer", "waldbauer_product_offer.html"),  # no specs in html
    ("Syswork", "syswork_product_offer.html"),
    # ("ARLT Computer", "arlt_product_offer.html"),
    ("I-CS", "ics_product_offer.html"),
    ("Alternate.at", "alternate_product_offer.html"),
    ("Cyberport.at", "cyberport_product_offer.html"),
    ("Cyberport Stores Österreich", "cyberport_product_offer.html"),
    # ("CLS-IT", 720),  # no useful data
    ("ms-it-beratung", "ms_it_beratung_product_offer.html"),
    ("cw-mobile.de", "cwmobile_product_offer.html"),
    ("bauguru", "bauguru_product_offer.html"),
    ("HEINZSOFT (AT)", "heinzsoft_product_offer.html"),
    ("HiQ24", "hiq24_product_offer.html"),
]


@pytest.mark.parametrize("shop_name,test_html", top30)
def test_shop_parser(shop_name, test_html):
    html_dir = TEST_DATA_DIR / test_html
    raw_html = html_dir.read_text()
    data = extract_tabular_data(raw_html, shop_name)

    assert data != {}


@pytest.mark.skip(reason="Requires data and may take a while.")
def test_retrieve_specs_real_data():
    """Tests if the top 30 shops extract at least one specification."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    dataset_name = "computerscreens2023"

    html_json_data_dir = data_dir / dataset_name

    checkboxes = {shop_name: False for shop_name, _ in top30}

    for idx, monitor_extended_offer in enumerate(get_products_from_path(html_json_data_dir)):
        # skip if shop_name not in checkboxes or shop_name is true in checkboxes
        if monitor_extended_offer.shop_name not in checkboxes or checkboxes[monitor_extended_offer.shop_name]:
            continue

        with open(html_json_data_dir / monitor_extended_offer.html_file) as file:
            html = file.read()
        raw_specifications = shop_parser.extract_tabular_data(html, monitor_extended_offer.shop_name)
        if raw_specifications:
            logger.debug(
                f"Specifications for {monitor_extended_offer.html_file} from {monitor_extended_offer.shop_name}\n"
                f"{raw_specifications}"
            )
            checkboxes[monitor_extended_offer.shop_name] = True

            if all(checkboxes.values()):
                break

    assert all(checkboxes.values())
