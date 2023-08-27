from pathlib import Path

import pytest

from rule_based_parser.shop_parser import parse_shop

TEST_DATA_DIR = Path("tests") / "rule_based_parser" / "test_data"


@pytest.mark.parametrize(
    "shop_name, test_html",
    [
        ("1ashop.at", "1ashop_product_offer.html"),
        ("BA-Computer", "bacomputer_product_offer.html"),
        # "barax", "barax.yaml",
        ("computeruniverse.at", "computeruniverse_product_offer.html"),
        ("ComStern.at", "comstern_product_offer.html"),
        ("DiTech.at", "ditech_product_offer.html"),
        ("e-tec.at", "etec_product_offer.html"),
        ("ElectronicShop24", "electronicshop24_product_offer.html"),
        ("Future-X.at", "futurex_product_offer.html"),
        # ("galaxus.at", "galaxus_product_offer.html"),
        ("haym.infotec", "hayminfotec_product_offer.html"),
        ("Jacob Elektronik direkt", "jacob_electronic_product_offer.html"),
        ("mylemon.at", "mylemon_product_offer.html"),
        # ("OTTO Österreich", "ottoversand_product_offer.html"),
        # ("Proshop.at", "proshop_product_offer.html"),
        # ("Universal Versand", "universal_product_offer.html"),
    ],
)
def test_shop_parser(shop_name, test_html):
    html_dir = TEST_DATA_DIR / test_html
    raw_html = html_dir.read_text()
    data = parse_shop(raw_html, shop_name)

    assert data
