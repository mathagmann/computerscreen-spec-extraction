import difflib

import click

from config import DATA_DIR
from data_generation.create_data import get_reference_product
from data_generation.utilities import get_products_from_path
from spec_extraction.extraction_config import MonitorParser
from spec_extraction.utilities import get_catalog_product


def evaluate_field_mappings():
    pass


def evaluate_token_classifier():
    pass


def evaluate_pipeline():
    parser = MonitorParser()
    products = get_products_from_path(DATA_DIR)
    for idx, product in enumerate(products):
        reference_data = get_reference_product(product.product_id)
        # convert reference_data.product_details name and value to dict
        reference_as_dict = {}
        for detail in reference_data.product_details:
            reference_as_dict[detail.name] = detail.value

        catalog_data = get_catalog_product(product_id)
        catalog_data_as_dict = parser.items(catalog_data.specifications)
        print(product)
        compare(reference_as_dict, catalog_data_as_dict)
        break


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

    # Display the differences using click.secho with colors
    if keys_only_in_ref:
        click.secho(f"Keys only in ref: {keys_only_in_ref}", fg="blue")

    all_keys = set(reference.keys()).union(set(dict2.keys()))
    for key in all_keys:
        # if key in differences print diff, with key else print key and value
        if key in differences:
            diff = color_diff(differences[key][0], differences[key][1])
            click.echo(diff)
        elif key in reference:
            click.secho(f"{key}: {reference[key]} (gh)")
        else:
            click.secho(f"{key}: {dict2[key]} (catalog)", fg="green")

    if differences:
        click.secho("Differences in values:", fg="red")
        for key, values in differences.items():
            diff = color_diff(values[0], values[1])
            click.echo(diff)

    # If there are no differences, indicate that the dictionaries are identical
    if not keys_only_in_ref and not keys_only_in_dict2 and not differences:
        click.secho("The dictionaries are identical.", fg="green")

    count_all = len(all_keys)
    count_wrong = len(differences) + len(keys_only_in_ref) + len(keys_only_in_dict2)
    count_correct = count_all - count_wrong
    return count_correct, count_all
