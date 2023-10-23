import json
import time
from pathlib import Path

import marshmallow_dataclass
from loguru import logger

from geizhals import geizhals_api
from geizhals.geizhals_model import Offer
from geizhals.geizhals_model import Product
from geizhals.geizhals_model import ProductPage

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
PRODUCT_LISTING = DATA_DIR / "product_listing.json"

CATEGORY_URL = "https://geizhals.at/?cat=monlcd19wide&asuch=&bpmin=&bpmax=&v=e&hloc=at&hloc=de&plz=&dist=&sort=n"


@marshmallow_dataclass.dataclass
class ExtendedOffer(Offer):
    html_file: str
    reference_file: str


def retrieve_all_products(browser, max_products=None) -> list[Product]:
    """Collects all products from the category 'Monitore' on Geizhals.

    Creates product_listing.json with all products.
    """
    if max_products:
        logger.info(f"Collecting up to {max_products} products")
    logger.info("")
    force_stop = False
    products = []
    page_counter = 0
    next_page = CATEGORY_URL
    while next_page:
        page_counter += 1
        category_page = geizhals_api.get_category_page(next_page, browser)
        for idx, product in enumerate(category_page.products):
            logger.debug(f"{idx} {product.name} {product.link}")
            products.append(product)

            if max_products and len(products) >= max_products:
                force_stop = True
                break
        if force_stop:
            break
        next_page = category_page.next_page
        if not next_page:
            break
    return products


def retrieve_product_details(browser, products: list[Product]):
    """Collects all product details from the given products.

    Stores the reference product details from Geizhals in a JSON file
    for each product called offer_reference_{product_idx}.json.
    """
    for product_idx, product in enumerate(products, start=1):
        logger.debug(f"{product_idx} {product.name}")
        start = time.time()

        reference_file = f"offer_reference_{product_idx}.json"
        # Skip already retrieved Geizhals products
        if (DATA_DIR / reference_file).exists():
            logger.debug(f"Skip {product.name}: Geizhals reference data for already exists")
            continue

        product_page = geizhals_api.get_product_page(product.link, browser)
        with open(DATA_DIR / reference_file, "w") as f:
            product_page_schema = marshmallow_dataclass.class_schema(ProductPage)()
            product_dict = product_page_schema.dump(product_page)
            json.dump(product_dict, f, indent=4)
        logger.debug(f"Reference for {product_page.product_name} stored")

        download_merchant_offers(browser, product_page.offers, reference_file, product_idx)
        logger.debug(f"Products took {time.time() - start:.1f}s to download")


def download_merchant_offers(browser, merchant_offers: list[Offer], reference_file: str, product_idx: int):
    """Collects all product details from the given products.

    Stores the merchant offer as html file and the offer details and
    link to the reference in a json file.
    """
    for idx, merchant_offer in enumerate(merchant_offers):
        logger.debug(f"Downloading offer {merchant_offer.offer_link}")
        try:
            html = browser.goto(merchant_offer.offer_link, no_wait=True)
            html_name = f"offer_{product_idx}_{idx}.html"
            html_file = DATA_DIR / html_name
            with open(html_file, "w") as f:
                f.write(html)

            with open(DATA_DIR / f"offer_{product_idx}_{idx}.json", "w") as f:
                offer_schema = marshmallow_dataclass.class_schema(ExtendedOffer)()
                offer_dict = offer_schema.dump(merchant_offer)
                offer_dict.update({"html_file": html_name, "reference_file": reference_file})
                json.dump(offer_dict, f, indent=4)
        except Exception:
            logger.error(f"Failed to download offer {merchant_offer.offer_link}")


def dump_product_listing(products: list[Product], filename: Path = PRODUCT_LISTING):
    """Stores the product listing as JSON in the given file."""
    with open(filename, "w") as f:
        products_dict = [marshmallow_dataclass.class_schema(Product)().dump(p) for p in products]
        json.dump(products_dict, f, indent=4)
