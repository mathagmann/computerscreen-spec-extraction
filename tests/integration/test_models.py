from spec_extraction.model import CatalogProduct
from spec_extraction.model import RawProduct


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