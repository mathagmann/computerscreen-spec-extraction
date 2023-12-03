import difflib

import click
from loguru import logger

from config import DATA_DIR
from data_generation.create_data import get_reference_product
from data_generation.utilities import get_products_from_path
from spec_extraction.extraction_config import MonitorParser
from spec_extraction.process import Processing
from spec_extraction.utilities import get_catalog_product


def evaluate_field_mappings():
    pass


def evaluate_token_classifier():
    pass


def evaluate_pipeline():
    MonitorParser()
    process = Processing()

    products = get_products_from_path(DATA_DIR)
    eval_attributes_correct = 0
    eval_all_attributes_extracted = 0
    eval_products_correct = 0
    eval_all_products = 0
    for idx, product in enumerate(products):
        reference_data = get_reference_product(product.product_id)
        click.echo(f"Processing product {idx:05d}: {reference_data.product_name}")

        reference_as_dict = {}
        for detail in reference_data.product_details:
            reference_as_dict[detail.name] = detail.value
        reference_structured = process.extract_structured_specifications(reference_as_dict, "geizhals")

        try:
            catalog_data = get_catalog_product(product.product_id)
        except FileNotFoundError:
            print(f"Catalog data for product {product.product_id} not found.")
            continue
        catalog_data_structured = catalog_data.specifications

        count_correct, count_all = compare_strings(reference_structured, catalog_data_structured)  # key: str,
        eval_all_attributes_extracted += count_all
        eval_attributes_correct += count_correct
        eval_all_products += 1
        if count_all == count_correct:
            eval_products_correct += 1

    attribute_precision = eval_attributes_correct / eval_all_attributes_extracted * 100
    logger.info(f"Attribute precision: {attribute_precision:.2f}%")

    product_precision = eval_products_correct / eval_all_products * 100
    logger.info(f"Product precision: {product_precision:.2f}%")

    return eval_attributes_correct, eval_all_attributes_extracted


def color_diff(string1, string2):
    """
    Compare two strings and return a colored diff using difflib.
    """
    d = difflib.Differ()
    diff = list(d.compare(string1.splitlines(), string2.splitlines()))

    colored_diff = []
    for line in diff:
        if line.startswith(" "):
            colored_diff.append(click.style(line, fg="white"))
        elif line.startswith("-"):
            colored_diff.append(click.style(line, fg="red"))
        elif line.startswith("+"):
            colored_diff.append(click.style(line, fg="green"))

    return "\n".join(colored_diff)


def compare_strings(reference: dict, dict2: dict) -> tuple[int, int]:
    """Compares two dicts.

    Returns
    -------
    correct: int
        The number of identical values.
    all: int
        The number of all values.
    """

    # Find keys that are in reference but not in dict2
    keys_only_in_ref = set(reference.keys()) - set(dict2.keys())

    # Find keys that are in dict2 but not in reference
    keys_only_in_dict2 = set(dict2.keys()) - set(reference.keys())

    # Find keys that are common to both dictionaries
    common_keys = set(reference.keys()) & set(dict2.keys())

    # Compare values for common keys
    differences = {}
    for key in common_keys:
        if reference[key] != dict2[key]:
            differences[key] = (reference[key], dict2[key])
            logger.debug(f"Found difference for key '{key}': {reference[key]} != {dict2[key]}")

    # Display the differences using click.secho with colors
    if keys_only_in_ref:
        logger.debug(f"Keys only in ref: {keys_only_in_ref}")

    all_keys = set(reference.keys()).union(set(dict2.keys()))
    # for key in all_keys:
    #     # if key in differences print diff, with key else print key and value
    #     if key in differences:
    #         diff = color_diff(differences[key][0], differences[key][1])
    #         click.echo(diff)
    #     elif key in reference:
    #         click.secho(f"{key}: {reference[key]} (gh)")
    #     else:
    #         click.secho(f"{key}: {dict2[key]} (catalog)", fg="green")
    #
    # if differences:
    #     click.secho("Differences in values:", fg="red")
    #     for key, values in differences.items():
    #         diff = color_diff(values[0], values[1])
    #         click.echo(diff)

    # If there are no differences, indicate that the dictionaries are identical
    # if not keys_only_in_ref and not keys_only_in_dict2 and not differences:
    #     click.secho("The dictionaries are identical.", fg="green")

    count_all = len(all_keys)
    count_wrong = len(differences) + len(keys_only_in_ref) + len(keys_only_in_dict2)
    count_correct = count_all - count_wrong
    return count_correct, count_all


if __name__ == "__main__":
    evaluate_pipeline()
