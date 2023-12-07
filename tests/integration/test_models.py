from spec_extraction.model import CatalogProduct


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
