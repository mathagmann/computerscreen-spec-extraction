import difflib
from dataclasses import dataclass

import click
from loguru import logger

from config import DATA_DIR
from config import PRODUCT_CATALOG_DIR
from config import ROOT_DIR
from data_generation.utilities import get_products_from_path
from geizhals.geizhals_model import ProductPage
from spec_extraction.bootstrap import bootstrap
from spec_extraction.model import CatalogProduct
from spec_extraction.normalization import normalize_product_specifications


@dataclass
class EvaluationScores:
    accuracy: float = 0
    precision: float = 0
    recall: float = 0
    f1_score: float = 0


@dataclass
class ConfusionMatrix:
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    true_negatives: int = 0

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

        logger.info(f"Precision: {precision * 100:.2f}%")
        logger.info(f"Recall: {recall * 100:.2f}%")
        logger.info(f"F1 score: {f1_score * 100:.2f}%")

        return EvaluationScores(accuracy=accuracy, precision=precision, recall=recall, f1_score=f1_score)


def evaluate_machine_learning():
    """Evaluate the machine learning model.

    Requires the machine learning model to be trained and saved to disk.
    """
    processing = bootstrap(machine_learning_enabled=True)
    processing.merge_monitor_specs(PRODUCT_CATALOG_DIR)

    attribute_confusion_matrix, product_precision = evaluate_pipeline()

    return attribute_confusion_matrix, product_precision


def evaluate_pipeline() -> tuple[ConfusionMatrix, float]:
    process = bootstrap()
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

    print(f"Attribute confusion matrix: {confusion_matrix}")
    print(f"Attribute evaluation scores: {confusion_matrix.eval_score}")
    print(f"Product precision: {product_precision * 100:.2f}%")

    return confusion_matrix, product_precision


def evaluate_field_mappings() -> tuple[EvaluationScores, EvaluationScores]:
    """Evaluate the field mappings.

    Returns
    -------
    tuple[EvaluationScores, EvaluationScores]
        A tuple containing the evaluation scores for the auto mapping and the manual mapping.

    """
    auto = ROOT_DIR / "spec_extraction" / "preparation" / "auto_field_mappings.json"
    manual = ROOT_DIR / "spec_extraction" / "preparation" / "field_mappings.json"

    # run pipeline twice and compare results
    auto_confusion_matrix, product_precision = evaluate_pipeline(mappings=auto)
    logger.info(f"Auto mapping: {auto_confusion_matrix}")
    logger.info(f"Product precision: {product_precision * 100:.2f}%")

    manual_confusion_matrix, product_precision = evaluate_pipeline(mappings=manual)
    logger.info(f"Manual mapping: {manual_confusion_matrix}")
    logger.info(f"Product precision: {product_precision * 100:.2f}%")

    return manual_confusion_matrix.eval_score, auto_confusion_matrix.eval_score


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

    reference_as_dict = {}
    for detail in reference_data.product_details:
        reference_as_dict[detail.name] = detail.value
    ref_specs = proc.extract_with_regex(reference_as_dict, "geizhals")

    catalog_filename = CatalogProduct.filename_from_id(product.product_id)
    catalog_data = CatalogProduct.load_from_json(PRODUCT_CATALOG_DIR / catalog_filename)
    cat_specs = catalog_data.specifications

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


if __name__ == "__main__":
    # evaluate_pipeline()
    evaluate_machine_learning()
