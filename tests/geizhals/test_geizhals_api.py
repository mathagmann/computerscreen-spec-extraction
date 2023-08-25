from pathlib import Path
from urllib.parse import urljoin

import pytest

from geizhals import geizhals_api


class MockBrowser:
    def goto(self, url: str) -> str:
        if "?cat=" in url:
            dummy_file = Path("tests") / "geizhals" / "test_data" / "category_page.html"
        else:
            dummy_file = Path("tests") / "geizhals" / "test_data" / "product_page.html"
        return dummy_file.read_text()


@pytest.fixture
def mock_browser():
    return MockBrowser()


def test_get_category_page(mock_browser):
    base_domain = "https://geizhals.at"
    url = urljoin(base_domain, "/?cat=monlcd19wide")

    parsed_page = geizhals_api.get_category_page(url, mock_browser)

    assert parsed_page.url == url
    assert len(parsed_page.products) == 30
    for product in parsed_page.products:
        assert product.name
        assert product.link.startswith(base_domain)
    assert parsed_page.next_page


def test_get_product(mock_browser):
    url = "https://geizhals.at/samsung-smart-monitor-m8-m80c-warm-white-ls27cm801uuxen-a3001040.html"
    parsed_data = geizhals_api.get_product_page(url, mock_browser)

    assert parsed_data.product_name.startswith("Samsung Smart Monitor M8")
    assert len(parsed_data.product_details) > 5
    for detail in parsed_data.product_details:
        assert detail.name
        assert detail.value
    assert len(parsed_data.offers) > 1
    for offer in parsed_data.offers:
        assert offer.offer_link.startswith("https://")
        assert offer.price > 0
        assert offer.shop_name


def test_get_base_domain():
    expected_base_domain = "https://geizhals.at"
    url = "https://geizhals.at/?cat=monlcd19wide"

    base_domain = geizhals_api.get_base_domain(url)

    assert base_domain == expected_base_domain


def test_de_affiliate_link():
    url = "https://www.abc.at/product&product_id=15785&ghaID=2998520&key=8abaf35a99eab7ad2599c39c44e06797"
    expected_url = "https://www.abc.at/product&product_id=15785"

    de_affiliate_link = geizhals_api.de_affiliate_link(url)

    assert de_affiliate_link == expected_url
