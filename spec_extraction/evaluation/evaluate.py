import difflib
import os
import shutil
import time
from dataclasses import dataclass

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
    accuracy: float = 0
    precision: float = 0
    recall: float = 0
    f1_score: float = 0

    def __repr__(self):
        return (
            f"Accuracy: {self.accuracy* 100:.2f} %\n"
            f"Precision: {self.precision* 100:.2f} %\n"
            f"Recall: {self.recall* 100:.2f} %\n"
            f"F1: {self.f1_score* 100:.2f} %"
        )


@dataclass
class ConfusionMatrix:
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    true_negatives: int = 0

    def __repr__(self):
        return (
            "Confusion matrix("
            f"true positives: {self.true_positives}, false positives: {self.false_positives}, "
            f"false negatives: {self.false_negatives}, true negatives: {self.true_negatives})"
        )

    def __add__(self, other):
        return ConfusionMatrix(
            true_positives=self.true_positives + other.true_positives,
            false_positives=self.false_positives + other.false_positives,
            false_negatives=self.false_negatives + other.false_negatives,
            true_negatives=self.true_negatives + other.true_negatives,
        )

    @property
    def eval_score(self) -> EvaluationScores:
        """Calculate evaluation scores based on the counts of true positives, false positives, etc."""
        total_predictions = self.true_negatives + self.false_negatives + self.false_positives + self.true_positives

        accuracy = (self.true_positives + self.true_negatives) / total_predictions if total_predictions > 0 else 0
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

        return EvaluationScores(accuracy=accuracy, precision=precision, recall=recall, f1_score=f1_score)


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"Function '{func.__name__}' took {end_time - start_time:.2f} seconds to execute")
        return result

    return wrapper


def evaluate_pipeline(process: Processing) -> tuple[ConfusionMatrix, float]:
    shutil.rmtree(REFERENCE_DIR, ignore_errors=True)
    os.makedirs(REFERENCE_DIR, exist_ok=True)
    logger.debug(f"Removed reference directory: {REFERENCE_DIR}")
    products = get_products_from_path(DATA_DIR)

    products_perfect_precision = 0
    products_false_positives = 0
    confusion_matrix = ConfusionMatrix()
    for idx, product in enumerate(products):
        try:
            scores = evaluate_product(process, idx, product)
            res = scores.eval_score
            logger.info(f"Product {product.product_id} scores: {res}")
        except FileNotFoundError:
            logger.debug(f"Product {product.product_id} not found in catalog.")
            continue

        confusion_matrix += scores
        if scores.eval_score.precision == 1:
            products_perfect_precision += 1
            logger.debug(f"Product {product.product_id} has perfect precision.")
        else:
            products_false_positives += 1

    total_products = products_perfect_precision + products_false_positives
    product_precision = products_perfect_precision / total_products if total_products > 0 else 0.0
    return confusion_matrix, product_precision


def calculate_confusion_matrix(reference_data, catalog_data) -> ConfusionMatrix:
    """Determines the numbers of the confusion matrix.

    The values are based on a reference dictionary and a second dictionary that
    is to be compared to the reference.

    True positives: The number of properties that exist in both (reference and catalog) and values match.
    False positives: The number of properties that exist in both, but values do not match.
    False negatives: The number of properties that only exists in reference.
    True negatives: The number of properties that only exist in catalog.

    Returns
    -------
    ConfusionMatrix
        A dataclass containing the number of true positives, false positives, etc.
    """
    confusion_matrix = ConfusionMatrix()

    for key in reference_data:
        if key in catalog_data:
            ref_value = reference_data[key]
            catalog_value = catalog_data[key]

            if ref_value == catalog_value:
                # True Positive (Matching entry), key exists in both
                confusion_matrix.true_positives += 1
                logger.debug(f"Match: {key}: {ref_value} == {catalog_value}")
            else:
                # False Positive (Non-matching entry), key exists in both
                confusion_matrix.false_positives += 1
                logger.debug(f"No match: {key}: {ref_value} != {catalog_value} (gathered)")
        else:
            # False Negative (Missing entry in catalog_data, but exists in reference_data)
            confusion_matrix.false_negatives += 1

    # Calculate True Negatives (Entries in catalog_data not present in reference_data)
    confusion_matrix.true_negatives = (
        len(catalog_data) - confusion_matrix.true_positives - confusion_matrix.false_positives
    )
    logger.debug(confusion_matrix)
    return confusion_matrix


def evaluate_product(proc, idx, product, normalization=True) -> ConfusionMatrix:
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
    """
    filename = ProductPage.reference_filename_from_id(product.product_id)
    reference_data = ProductPage.load_from_json(DATA_DIR / filename)

    logger.debug(f"Processing product {idx:05d}: {reference_data.product_name}")

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
            CatalogProduct(name=catalog_data.name, specifications=ref_specs, id=catalog_data.id).save_to_json(
                REFERENCE_DIR / ref_export_file
            )
            logger.debug(f"Reference data saved to {ref_export_file}")
        except Exception as e:
            logger.error(f"Could not save reference data: {e}")

    if normalization:
        ref_specs = normalize_product_specifications(ref_specs)
        cat_specs = normalize_product_specifications(cat_specs)

    return calculate_confusion_matrix(ref_specs, cat_specs)


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
