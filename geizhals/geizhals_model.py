from typing import Optional

from marshmallow_dataclass import dataclass


@dataclass
class Product:
    name: str
    link: str


@dataclass
class CategoryPage:
    url: str
    products: list[Product]
    next_page: Optional[str]


@dataclass
class Offer:
    shop_name: str
    price: float
    offer_link: str
    promotion_description: Optional[str]


@dataclass
class ProductDetail:
    name: str
    value: str


@dataclass
class ProductPage:
    url: str
    product_name: str
    product_details: list[ProductDetail]
    offers: list[Offer]
