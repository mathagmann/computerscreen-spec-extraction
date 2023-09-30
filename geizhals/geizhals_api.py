import re
from typing import Protocol
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .geizhals_model import CategoryPage
from .geizhals_model import ProductPage


class SupportsGoto(Protocol):
    def goto(self, url: str) -> str:
        """Visits given url and returns the html content."""
        ...


def get_category_page(category_url: str, browser: SupportsGoto) -> CategoryPage:
    """Returns all products listed on a Geizhals category page."""
    html = browser.goto(category_url)
    data = parse_category_page(html, category_url)
    return CategoryPage.Schema().load(data)


def get_product_page(product_url: str, browser: SupportsGoto) -> ProductPage:
    """Returns the product details from a Geizhals product page."""
    html = browser.goto(product_url)
    data = parse_product_page(html, product_url)
    return ProductPage.Schema().load(data)


def get_base_domain(url: str) -> str:
    """Returns the base domain of given url."""
    url_parts = url.split("/")
    if len(url_parts) >= 3:
        url = "/".join(url.split("/")[:3])
    return url


def parse_category_page(html: str, url: str) -> dict:
    base_domain = get_base_domain(url)
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("body")

    iterator = body.find_all("div", attrs={"class": "productlist__product"})
    products = []
    for product in iterator:
        name = product.find("a", attrs={"class": "productlist__link"}).text.strip()
        link = product.find("a", attrs={"class": "productlist__link"}).get("href")
        link = urljoin(base_domain, link)
        products.append({"name": name, "link": link})
    next_page = body.find("a", attrs={"class": "gh_pag_i_last"}).get("href")
    next_page = urljoin(base_domain, next_page)

    return {"url": url, "products": products, "next_page": next_page}


def parse_product_page(html, product_url) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("body")

    product_name = body.select_one("h1.variant__header__headline").text.strip()
    product_details = []
    for detail in body.select("div.variant__content__specs div.specs-grid__item"):
        title = detail.find("dt").text.strip()
        description = detail.find("dd").text.strip()
        product_details.append({"name": title, "value": description})

    offers = []
    for offer in body.select("div.steel_list_container > div.offer"):
        shop_name = offer.select_one("div.offer__clickout > a").get("data-merchant-name").strip()
        price = float(offer.select_one("span.gh_price").text.strip().replace("€ ", "").replace(",", "."))
        offer_link = _convert_to_url(offer.select_one("div.offer__clickout > a").get("href").strip())
        offer_link = de_affiliate_link(offer_link)
        res = {"shop_name": shop_name, "price": price, "offer_link": offer_link}
        has_promotion = offer.select_one("div.promotiontooltip")
        if has_promotion:
            promo_wrapper = has_promotion.select_one("div.promotiontooltip__tooltip__text")
            promotion_description = " ".join([x.text for x in promo_wrapper.children]).strip().replace("  ", " ")
            res.update({"promotion_description": promotion_description})
        offers.append(res)

    return {"url": product_url, "product_name": product_name, "product_details": product_details, "offers": offers}


def _convert_to_url(encoded_url: str) -> str:
    """Extracts and unquotes given url."""
    encoded_shop_url = encoded_url.split("&loc=")[-1]
    return requests.utils.unquote(encoded_shop_url)


def de_affiliate_link(url: str) -> str:
    """Removes affiliate parameters from given url."""
    shop_url = re.sub("ghaID=[^&]+&*", "", url)
    shop_url = re.sub("key=[^&]+&*", "", shop_url)
    shop_url = re.sub("referrer=[^&]+&*", "", shop_url)
    return shop_url.rstrip("&")
