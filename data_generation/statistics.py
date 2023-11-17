import json
from collections import Counter

from config import DATA_DIR
from data_generation.utilities import get_products_from_path


def calc_statistics(products: list, most_common: int = 30):
    shop_offers = Counter(p.shop_name for p in products)
    median_price = sum(p.price for p in products) / len(products)

    top_shops = shop_offers.most_common(most_common)
    total_products_common_shops = sum(count for _, count in top_shops)
    percentage_top_shops = total_products_common_shops / len(products) * 100

    return dict(
        product_count_per_shop=shop_offers.most_common(most_common),
        total_shops=len(shop_offers),
        total_products=len(products),
        n_most_common_shops=most_common,
        total_products_n_most_common_shops=total_products_common_shops,
        percentage_products_most_common_shops=round(percentage_top_shops, 2),
        median_price=round(median_price, 2),
    )


if __name__ == "__main__":
    print("Calculating statistics...")
    path = DATA_DIR
    products = [prod for prod in get_products_from_path(path)]
    result = calc_statistics(products)
    with open(path / "statistics.json", "w") as f:
        json.dump(result, f, indent=4)
    print(f"Written statistics to {path / 'statistics.json'}")
