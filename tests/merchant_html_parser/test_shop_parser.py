from pathlib import Path

import pytest

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
