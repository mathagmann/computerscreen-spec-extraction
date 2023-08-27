import pytest

from data_generation import create_data
from data_generation.browser import Browser


@pytest.mark.skip(reason="Only for manual tests, not for CI")
def test_scrape_data_from_web():
    """This test actually scrapes data from the web."""
    max_products = 3
    with Browser(headless=False) as browser:
        products = create_data.retrieve_all_products(browser, max_products=max_products)
        create_data.retrieve_product_details(browser, products)
