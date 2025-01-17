from data_generation import model
from data_generation import statistics


def test_statistics():
    products = [
        model.ExtendedOffer(
            shop_name="shop1",
            price=100,
            offer_link="https://www.example.com",
            promotion_description=None,
            html_file=None,
            reference_file=None,
        ),
        model.ExtendedOffer(
            shop_name="shop2",
            price=200,
            offer_link="https://www.example.com",
            promotion_description=None,
            html_file=None,
            reference_file=None,
        ),
        model.ExtendedOffer(
            shop_name="shop2",
            price=300,
            offer_link="https://www.example.com",
            promotion_description=None,
            html_file=None,
            reference_file=None,
        ),
    ]
    result = statistics.calc_statistics(products)

    assert result["median_price"] == 200
    assert result["total_products"] == 3
    assert result["total_shops"] == 2
    assert result["product_count_per_shop"] == [("shop2", 2), ("shop1", 1)]
