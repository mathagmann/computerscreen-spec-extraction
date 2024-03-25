import difflib
import os
import shutil
import time
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click
from loguru import logger

from config import DATA_DIR
from config import REFERENCE_DIR
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


def get_products_from_catalog(catalog_dir: Path) -> Generator[CatalogProduct, None, None]:
    """Yields raw specification with metadata from JSON files.

    The order of the files is not guaranteed, but specifications from the same
    monitor follow each other.

    Example:
    --------
    product_1_catalog.json
    product_2_catalog.json
    product_3_catalog.json
    """
    for file in sorted(catalog_dir.glob("*.json")):
        logger.debug(f"Loading {file.name}...")
        yield CatalogProduct.load_from_json(catalog_dir / file.name)


def evaluate_pipeline(
    process: Processing,
    evaluated_data_dir: Path,
) -> tuple[ConfusionMatrix, dict[str, ConfusionMatrix], float]:
    # Delete reference data directory and create it again
    shutil.rmtree(REFERENCE_DIR, ignore_errors=True)
    os.makedirs(REFERENCE_DIR, exist_ok=True)

    products_perfect_precision = 0
    products_false_positives = 0

    cm_per_attr = {}
    res_confusion_matrix = ConfusionMatrix()

    evaluated_products = get_products_from_catalog(evaluated_data_dir)
    idx = 0
    for idx, eval_product in enumerate(evaluated_products):
        logger.info(f"Evaluate product {eval_product.name}' with ID: {eval_product.id}")
        confusion_matrix_per_attr = evaluate_product(process, eval_product=eval_product)
        conf_matrix = sum_confusion_matrices(confusion_matrix_per_attr)
        logger.info(f"Scores for Product ID {eval_product.id}: {conf_matrix.eval_score}")

        res_confusion_matrix += conf_matrix

        # sum up confusion matrices
        cm_per_attr = combine_confusion_matrices(cm_per_attr, confusion_matrix_per_attr)
        if conf_matrix.eval_score.precision == 1:
            products_perfect_precision += 1
            logger.debug(f"Product {eval_product.id} has perfect precision.")
        else:
            products_false_positives += 1
    assert idx > 0, "No products found for evaluation."
    logger.debug(f"Processed {idx+1} products.")

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


def evaluate_product(proc, eval_product: CatalogProduct, normalization=True) -> dict[str, ConfusionMatrix]:
    """Collect all specifications from the reference data and the catalog data and compares them.

    Assumes that the reference data is stored in a JSON file in the
    data directory and the catalog data is stored in a JSON file in the
    product catalog directory.

    Parameters
    ----------
    proc
        The processing object.
    eval_product
        The product to evaluate.
    normalization
        Enable or disable additional value normalization stage. Enabled by default.

    Returns
    -------
    dict[str, ConfusionMatrix]
        The attribute name and confusion matrix for each attribute.
    """
    evaluation_specs = eval_product.specifications

    # Create structured reference data from Geizhals raw data
    filename = ProductPage.reference_filename_from_id(eval_product.id)
    reference_data = ProductPage.load_from_json(DATA_DIR / filename)
    ref_export_file = f"ref_specs_{eval_product.id}_catalog.json"
    reference_as_dict = {}
    for detail in reference_data.product_details:
        reference_as_dict[detail.name] = detail.value

    # machine learning disabled for reference data
    reference_product_specs = proc.extract_properties(reference_as_dict, "geizhals")

    if len(reference_product_specs.keys()) <= 0:
        logger.warning(f"Reference data {reference_product_specs} empty for {reference_data.id}")

    product = CatalogProduct(name=eval_product.name, specifications=reference_product_specs, id=eval_product.id)
    product.save_to_json(REFERENCE_DIR / ref_export_file)
    logger.debug(f"Reference data saved to {ref_export_file}")

    # Normalize and compare specifications
    if normalization:
        reference_product_specs = normalize_product_specifications(reference_product_specs)
        evaluation_specs = normalize_product_specifications(evaluation_specs)
    logger.debug(f"Latest reference specs: {reference_data.url}")

    return calculate_confusion_matrix_per_attr(reference_product_specs, evaluation_specs)


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
