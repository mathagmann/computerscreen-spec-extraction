import pytest

from data_generation import create_data
from data_generation.browser import Browser


@pytest.mark.skip(reason="Only for manual tests, not for CI")
def test_get_monitor_listing():
    """This test actually scrapes data from the web."""
    max_products = 3
    with Browser(headless=False) as browser:
        products = create_data.retrieve_all_products(browser, max_products=max_products)

    assert len(products) == max_products
