import difflib
import os
import shutil
import time
from dataclasses import dataclass
from typing import Any

import click
from loguru import logger

from config import DATA_DIR
from config import PRODUCT_CATALOG_DIR
from config import REFERENCE_DIR
from data_generation.utilities import get_products_from_path
from geizhals.geizhals_model import ProductPage
from spec_extraction.model import CatalogProduct
from spec_extraction.normalization import normalize_product_specifications
from spec_extraction.process import Processing


@dataclass
class EvaluationScores:
    precision: float = 0
    recall: float = 0
    f1_score: float = 0

    def __repr__(self):
        return (
            f"EvalScores(precision: {self.precision * 100:.2f} %, recall: {self.recall * 100:.2f} %, "
            f"f1_score: {self.f1_score * 100:.2f} %)"
        )


@dataclass
class ConfusionMatrix:
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0

    def __repr__(self):
        return (
            "Confusion matrix("
            f"true positives: {self.true_positives}, false positives: {self.false_positives}, "
            f"false negatives: {self.false_negatives}"
        )

    def __add__(self, other):
        return ConfusionMatrix(
            true_positives=self.true_positives + other.true_positives,
            false_positives=self.false_positives + other.false_positives,
            false_negatives=self.false_negatives + other.false_negatives,
        )

    @property
    def eval_score(self) -> EvaluationScores:
        """Calculate evaluation scores based on the counts of true positives, false positives, etc."""
        precision = (
            self.true_positives / (self.true_positives + self.false_positives)
            if (self.true_positives + self.false_positives) > 0
            else 0
        )
        recall = (
            self.true_positives / (self.true_positives + self.false_negatives)
            if (self.true_positives + self.false_negatives) > 0
            else 0
        )
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return EvaluationScores(precision=precision, recall=recall, f1_score=f1_score)


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"Function '{func.__name__}' took {end_time - start_time:.2f} seconds to execute")
        return result

    return wrapper


def evaluate_pipeline(process: Processing) -> tuple[ConfusionMatrix, dict[str, ConfusionMatrix], float]:
    shutil.rmtree(REFERENCE_DIR, ignore_errors=True)
    os.makedirs(REFERENCE_DIR, exist_ok=True)
    logger.debug(f"Removed reference directory: {REFERENCE_DIR}")
    products = get_products_from_path(DATA_DIR)

    products_perfect_precision = 0
    products_false_positives = 0

    cm_per_attr = {}
    res_confusion_matrix = ConfusionMatrix()
    for idx, product in enumerate(products):
        try:
            confusion_matrix_per_attr = evaluate_product(process, idx, product)
            conf_matrix = sum_confusion_matrices(confusion_matrix_per_attr)
            logger.info(f"Product {product.product_id} scores: {conf_matrix.eval_score}")
        except FileNotFoundError:
            logger.debug(f"Product {product.product_id} not found in catalog.")
            continue

        res_confusion_matrix += conf_matrix

        # sum up confusion matrices
        cm_per_attr = combine_confusion_matrices(cm_per_attr, confusion_matrix_per_attr)
        if conf_matrix.eval_score.precision == 1:
            products_perfect_precision += 1
            logger.debug(f"Product {product.product_id} has perfect precision.")
        else:
            products_false_positives += 1

    total_products = products_perfect_precision + products_false_positives
    product_precision = products_perfect_precision / total_products if total_products > 0 else 0.0
    return res_confusion_matrix, cm_per_attr, product_precision


def combine_confusion_matrices(
    confusion_matrices: dict[str, ConfusionMatrix], other: dict[str, ConfusionMatrix]
) -> dict[str, ConfusionMatrix]:
    """Combine two confusion matrices."""
    for key, value in other.items():
        if key in confusion_matrices:
            confusion_matrices[key] += value
        else:
            confusion_matrices[key] = value
    return confusion_matrices


def print_confusion_matrix_per_attr(confusion_matrix: dict[str, ConfusionMatrix]):
    """Print confusion matrix per attribute."""
    for attr, cmatrix in sorted(confusion_matrix.items()):
        logger.info(f"Attribute: {attr}\n{cmatrix}\n{cmatrix.eval_score}")


def calculate_confusion_matrix_per_attr(reference_data, catalog_data) -> dict[str, ConfusionMatrix]:
    """Determines the numbers of the confusion matrix.

    The values are based on a reference dictionary and a second dictionary that
    is to be compared to the reference.

    True positives:
        The number of properties that exist in both (reference and catalog data) and the values match.
    False positives:
        The number of properties, where the attribute only exists in the catalog data or the values do not match.
    False negatives:
        The number of properties, where the attribute only exists in the reference data or the values do
        not match.

    Returns
    -------
    dict[str, ConfusionMatrix]
        Containing the number of true positives, false positives with attribute level granularity.
    """
    result = {}
    all_keys = set(reference_data.keys()) | set(catalog_data.keys())
    for attribute in all_keys:
        ref_attr_value = (None, None) if attribute not in reference_data else (attribute, reference_data[attribute])
        cat_attr_value = (None, None) if attribute not in catalog_data else (attribute, catalog_data[attribute])

        result[attribute] = _calc_single_attribute_confusion_matrix(ref_attr_value, cat_attr_value)
    return result


def sum_confusion_matrices(confusion_matrices: dict[str, ConfusionMatrix]) -> ConfusionMatrix:
    """Sum up all confusion matrices."""
    return sum(confusion_matrices.values(), ConfusionMatrix())


def _calc_single_attribute_confusion_matrix(
    reference_attr_value: tuple[Any, Any], catalog_attr_value: tuple[Any, Any]
) -> ConfusionMatrix:
    confusion_matrix = ConfusionMatrix()
    ref_attribute, reference_value = reference_attr_value
    cat_attribute, catalog_value = catalog_attr_value

    if ref_attribute is None and cat_attribute is None:
        raise ValueError("Both attributes are None.")

    if ref_attribute is not None and cat_attribute is None:
        # Attribute only exists in reference data -> FN
        confusion_matrix.false_negatives += 1
    elif cat_attribute is not None and ref_attribute is None:
        # Attribute only exists in catalog data -> FP
        confusion_matrix.false_positives += 1
    elif ref_attribute == cat_attribute:
        if reference_value == catalog_value:
            # Attributes exists in both and values match -> TP
            confusion_matrix.true_positives += 1
        else:
            # attribute exists in both, but values do not match -> FP and FN
            confusion_matrix.false_positives += 1
            confusion_matrix.false_negatives += 1
    return confusion_matrix


def evaluate_product(proc, idx, product, normalization=True) -> dict[str, ConfusionMatrix]:
    """Collect all specifications from the reference data and the catalog data and compares them.

    Assumes that the reference data is stored in a JSON file in the
    data directory and the catalog data is stored in a JSON file in the
    product catalog directory.

    Parameters
    ----------
    proc
        The processing object.
    idx
        The index of the product.
    product
        The product to evaluate.
    normalization
        Enable or disable additional value normalization stage. Enabled by default.

    Returns
    -------
    dict[str, ConfusionMatrix]
        The attribute name and confusion matrix for each attribute.
    """
    filename = ProductPage.reference_filename_from_id(product.product_id)
    reference_data = ProductPage.load_from_json(DATA_DIR / filename)
    logger.debug(f"Processing product {idx:05d}: {reference_data.product_name}")

    # extracted and merged product data
    catalog_filename = CatalogProduct.filename_from_id(product.product_id)
    catalog_data = CatalogProduct.load_from_json(PRODUCT_CATALOG_DIR / catalog_filename)
    cat_specs = catalog_data.specifications

    # extract Geizhals data
    ref_export_file = f"ref_specs_{product.product_id}_catalog.json"
    try:
        ref_product = CatalogProduct.load_from_json(REFERENCE_DIR / ref_export_file)
        ref_specs = ref_product.specifications
    except FileNotFoundError:
        ref_specs = None
    if ref_specs is None:
        reference_as_dict = {}
        for detail in reference_data.product_details:
            reference_as_dict[detail.name] = detail.value
        ref_specs = proc.extract_properties(reference_as_dict, "geizhals")

        try:
            # export structured reference data
            ref_export_file = f"ref_specs_{product.product_id}_catalog.json"
            product = CatalogProduct(name=catalog_data.name, specifications=ref_specs, id=catalog_data.id)
            product.save_to_json(REFERENCE_DIR / ref_export_file)
            logger.debug(f"Reference data saved to {ref_export_file}")
        except Exception as e:
            logger.error(f"Could not save reference data: {e}")

    if normalization:
        ref_specs = normalize_product_specifications(ref_specs)
        cat_specs = normalize_product_specifications(cat_specs)
    logger.debug(f"Latest reference specs: {reference_data.url}")

    return calculate_confusion_matrix_per_attr(ref_specs, cat_specs)


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
