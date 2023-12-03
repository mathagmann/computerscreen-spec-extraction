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


def compare(dict1, dict2):
    # Assuming dict1 and dict2 are dictionaries to be compared

    # Find keys that are in dict1 but not in dict2
    keys_only_in_dict1 = set(dict1.keys()) - set(dict2.keys())

    # Find keys that are in dict2 but not in dict1
    keys_only_in_dict2 = set(dict2.keys()) - set(dict1.keys())

    # Find keys that are common to both dictionaries
    common_keys = set(dict1.keys()) & set(dict2.keys())

    # Compare values for common keys
    differences = {}
    for key in common_keys:
        if dict1[key] != dict2[key]:
            differences[key] = (dict1[key], dict2[key])

    # Display the differences using click.secho with colors
    if keys_only_in_dict1:
        click.secho(f"Keys only in dict1: {keys_only_in_dict1}", fg="red")

    if keys_only_in_dict2:
        click.secho(f"Keys only in dict2: {keys_only_in_dict2}", fg="red")

    if differences:
        click.secho("Differences in values:", fg="red")
        for key, values in differences.items():
            diff = color_diff(values[0], values[1])
            click.echo(diff)
            # message = f"  {key}: {values[0]} (dict1) != {values[1]} (dict2)"
            # click.secho(message, fg="yellow")

    # If there are no differences, indicate that the dictionaries are identical
    if not keys_only_in_dict1 and not keys_only_in_dict2 and not differences:
        click.secho("The dictionaries are identical.", fg="green")

    return len(differences)


def compare_specifications(reference_spec: dict, catalog_spec: dict) -> int:
    """Compares two dicts and outputs non-empty, different values."""
    diff = compare(reference_spec, catalog_spec)
    # wrong_entries = list(
    #     filter(lambda elem: "_message" in elem and "Values not equal" in elem["_message"], diff.values())
    # )
    # if wrong_entries:
    #     logger.warning(f"Diff:\n{json.dumps(wrong_entries, indent=4, sort_keys=True)}")
    return diff
