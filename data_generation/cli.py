from pathlib import Path

import click
import create_data
from loguru import logger

from data_generation.browser import Browser


@click.command()
@click.option("--max_products", "-m", type=int, help="Specify the maximum number of products for product listing")
@click.option(
    "--product_listing",
    type=click.Path(exists=True),
    default=None,
    help="Download product details for products in JSON",
)
def main(max_products: int, product_listing: Path):
    with Browser(headless=False) as browser:
        if product_listing:
            # Download products based on an existing product listing
            products = create_data.get_product_listing(product_listing)
        else:
            products = create_data.retrieve_all_products(browser, max_products)
        logger.info(f"Found {len(products)} products")
        create_data.retrieve_product_details(browser, products)


if __name__ == "__main__":
    main()
