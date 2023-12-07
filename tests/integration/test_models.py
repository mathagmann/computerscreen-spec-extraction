from data_generation.model import ExtendedOffer
from geizhals.geizhals_model import ProductPage
from spec_extraction.model import CatalogProduct
from spec_extraction.model import RawProduct


def test_product_page(tmp_path):
    product_page = ProductPage(url="url", product_name="test", product_details=[], offers=[])
    tmp_file = tmp_path / ProductPage.reference_filename_from_id("1")

    assert not tmp_file.exists()

    product_page.save_to_json(tmp_file)

    assert tmp_file.exists()

    loaded = ProductPage.load_from_json(tmp_file)

    assert loaded.url == product_page.url
    assert loaded.product_name == product_page.product_name
    assert loaded.product_details == product_page.product_details
    assert loaded.offers == product_page.offers


def test_extended_offer(tmp_path):
    extended_offer = ExtendedOffer(
        shop_name="test",
        price=100,
        offer_link="link",
        promotion_description="promotion",
        html_file="html",
        reference_file="reference",
    )
    tmp_file = tmp_path / extended_offer.reference_file

    assert not tmp_file.exists()

    extended_offer.save_to_json(tmp_file)

    assert tmp_file.exists()

    loaded = ExtendedOffer.load_from_json(tmp_file)

    assert loaded.shop_name == extended_offer.shop_name
    assert loaded.price == extended_offer.price
    assert loaded.offer_link == extended_offer.offer_link
    assert loaded.promotion_description == extended_offer.promotion_description
    assert loaded.html_file == extended_offer.html_file
    assert loaded.reference_file == extended_offer.reference_file


def test_raw_product(tmp_path):
    raw_product = RawProduct(
        name="test",
        raw_specifications={"key1": "value1", "key2": "value2"},
        raw_specifications_text="text",
        shop_name="shop",
        price=100,
        html_file="html",
        offer_link="link",
        reference_file="reference",
    )
    tmp_file = tmp_path / raw_product.filename

    assert not tmp_file.exists()

    raw_product.save_to_json(tmp_file)

    assert tmp_file.exists()

    loaded = RawProduct.load_from_json(tmp_file)

    assert loaded.name == raw_product.name
    assert loaded.raw_specifications == raw_product.raw_specifications
    assert loaded.raw_specifications_text == raw_product.raw_specifications_text
    assert loaded.shop_name == raw_product.shop_name
    assert loaded.price == raw_product.price
    assert loaded.html_file == raw_product.html_file
    assert loaded.offer_link == raw_product.offer_link
    assert loaded.reference_file == raw_product.reference_file


def test_catalog_product(tmp_path):
    catalog_product = CatalogProduct(
        name="test",
        specifications={"key1": {"value": "value1", "score": 100}, "key2": {"value": "value2", "score": 100}},
        id="1",
    )
    tmp_file = tmp_path / CatalogProduct.filename_from_id(catalog_product.id)

    assert not tmp_file.exists()

    catalog_product.save_to_json(tmp_file)

    assert tmp_file.exists()

    loaded = CatalogProduct.load_from_json(tmp_file)

    assert loaded.name == catalog_product.name
    assert loaded.specifications == catalog_product.specifications
    assert loaded.id == catalog_product.id
