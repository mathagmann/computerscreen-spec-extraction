import click
import create_data
from loguru import logger

from data_generation.browser import Browser


@click.command()
@click.option("--max_products", "-m", type=int, help="Specify the maximum number of products to scrape")
def main(max_products: int):
    with Browser() as browser:
        products = create_data.retrieve_all_products(browser, max_products)
        logger.info(f"Found {len(products)} products")
        create_data.retrieve_product_details(browser, products)
