import difflib
from dataclasses import dataclass
from functools import partial

import click
from loguru import logger

from config import DATA_DIR
from config import ROOT_DIR
from data_generation.create_data import get_reference_product
from data_generation.utilities import get_products_from_path
from spec_extraction.extraction_config import MonitorParser
from spec_extraction.process import Processing
from spec_extraction.utilities import get_catalog_product


@dataclass
class ConfusionMatrix:
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    true_negatives: int = 0

    def is_perfect(self):
        return self.false_negatives == 0 and self.false_positives == 0

    def __add__(self, other):
        return ConfusionMatrix(
            true_positives=self.true_positives + other.true_positives,
            false_positives=self.false_positives + other.false_positives,
            false_negatives=self.false_negatives + other.false_negatives,
            true_negatives=self.true_negatives + other.true_negatives,
        )


@dataclass
class EvaluationScores:
    accuracy: float = 0
    precision: float = 0
    recall: float = 0
    f1_score: float = 0


def evaluate_token_classifier():
    pass


def evaluate_pipeline(mappings=None) -> ConfusionMatrix:
    MonitorParser()
    if mappings:
        process = Processing(field_mappings=mappings)
    else:
        process = Processing()

    eval_product = partial(evaluate_product, process)

    products = get_products_from_path(DATA_DIR)

    count_products = 0
    count_correct_products = 0
    confusion_matrix = ConfusionMatrix()
    for idx, product in enumerate(products):
        try:
            scores = eval_product(idx, product)
        except FileNotFoundError:
            continue

        confusion_matrix += scores
        count_products += 1
        if scores.is_perfect():
            count_correct_products += 1
    return confusion_matrix


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
    confusion_matrix = evaluate_pipeline(mappings=auto)
    logger.info(f"Auto mapping: {confusion_matrix}")
    scores_auto = calculate_evaluation_scores(confusion_matrix)

    confusion_matrix = evaluate_pipeline(mappings=manual)
    logger.info(f"Manual mapping: {confusion_matrix}")
    scores_manual = calculate_evaluation_scores(confusion_matrix)

    return scores_manual, scores_auto


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
            if reference_data[key] == catalog_data[key]:
                # True Positive (Matching entry), key exists in both
                confusion_matrix.true_positives += 1
            else:
                # False Positive (Non-matching entry), key exists in both
                confusion_matrix.false_positives += 1
        else:
            # False Negative (Missing entry in catalog_data, but exists in reference_data)
            confusion_matrix.false_negatives += 1

    # Calculate True Negatives (Entries in catalog_data not present in reference_data)
    confusion_matrix.true_negatives = (
        len(catalog_data) - confusion_matrix.true_positives - confusion_matrix.false_positives
    )
    return confusion_matrix


def calculate_evaluation_scores(counts: ConfusionMatrix) -> EvaluationScores:
    """Calculate evaluation scores based on the counts of true positives, false positives, etc."""
    total_predictions = counts.true_negatives + counts.false_negatives + counts.false_positives + counts.true_positives

    accuracy = (counts.true_positives + counts.true_negatives) / total_predictions if total_predictions > 0 else 0
    precision = (
        counts.true_positives / (counts.true_positives + counts.false_positives)
        if (counts.true_positives + counts.false_positives) > 0
        else 0
    )
    recall = (
        counts.true_positives / (counts.true_positives + counts.false_negatives)
        if (counts.true_positives + counts.false_negatives) > 0
        else 0
    )
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    logger.info(f"Precision: {precision * 100:.2f}%")
    logger.info(f"Recall: {recall * 100:.2f}%")
    logger.info(f"F1 score: {f1_score * 100:.2f}%")

    return EvaluationScores(accuracy=accuracy, precision=precision, recall=recall, f1_score=f1_score)


def evaluate_product(proc, idx, product) -> ConfusionMatrix:
    """Collect all specifications from the reference data and the catalog data and compares them."""
    reference_data = get_reference_product(product.product_id)
    logger.debug(f"Processing product {idx:05d}: {reference_data.product_name}")

    reference_as_dict = {}
    for detail in reference_data.product_details:
        reference_as_dict[detail.name] = detail.value
    reference_structured = proc.extract_structured_specifications(reference_as_dict, "geizhals")

    try:
        catalog_data = get_catalog_product(product.product_id)
    except FileNotFoundError:
        print(f"Catalog data for product {product.product_id} not found.")
        raise
    catalog_data_structured = catalog_data.specifications

    return calculate_confusion_matrix(reference_structured, catalog_data_structured)


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
    evaluate_pipeline()
