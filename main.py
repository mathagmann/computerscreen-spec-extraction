from loguru import logger

from config import PRODUCT_CATALOG_DIR
from config import ROOT_DIR
from spec_extraction.bootstrap import bootstrap as extraction_bootstrap
from spec_extraction.evaluation.evaluate import evaluate_pipeline
from spec_extraction.evaluation.evaluate import measure_time
from spec_extraction.evaluation.evaluate import print_confusion_matrix_per_attr
from spec_extraction.evaluation.evaluate import sum_confusion_matrices

DEFAULT_FIELD_MAPPINGS = ROOT_DIR / "spec_extraction" / "preparation" / "field_mappings.json"
DEFAULT_PRODUCT_CATALOG_DIR = PRODUCT_CATALOG_DIR


@measure_time
def evaluate_base_pipeline():
    processing_instance = extraction_bootstrap(field_mappings=DEFAULT_FIELD_MAPPINGS, machine_learning_enabled=False)
    processing_instance.merge_monitor_specs(DEFAULT_PRODUCT_CATALOG_DIR)

    confusion_matrix, cm_per_attr, product_precision = evaluate_pipeline(
        processing_instance, evaluated_data_dir=DEFAULT_PRODUCT_CATALOG_DIR
    )
    assert confusion_matrix == sum_confusion_matrices(cm_per_attr)

    return confusion_matrix, cm_per_attr, product_precision


@measure_time
def evaluate_base_pipeline_with_machine_learning():
    processing_instance = extraction_bootstrap(field_mappings=DEFAULT_FIELD_MAPPINGS, machine_learning_enabled=True)
    processing_instance.merge_monitor_specs(DEFAULT_PRODUCT_CATALOG_DIR)

    confusion_matrix, cm_per_attr, product_precision = evaluate_pipeline(
        processing_instance, evaluated_data_dir=DEFAULT_PRODUCT_CATALOG_DIR
    )
    assert confusion_matrix == sum_confusion_matrices(cm_per_attr)

    return confusion_matrix, cm_per_attr, product_precision


@measure_time
def evaluate_base_pipeline_with_manual_mapping():
    enhanced_field_mappings = ROOT_DIR / "spec_extraction" / "preparation" / "field_mappings_enhanced_mylemon.json"
    processing_instance = extraction_bootstrap(field_mappings=enhanced_field_mappings, machine_learning_enabled=False)
    processing_instance.merge_monitor_specs(DEFAULT_PRODUCT_CATALOG_DIR)

    confusion_matrix, cm_per_attr, product_precision = evaluate_pipeline(
        processing_instance, evaluated_data_dir=DEFAULT_PRODUCT_CATALOG_DIR
    )
    assert confusion_matrix == sum_confusion_matrices(cm_per_attr)

    return confusion_matrix, cm_per_attr, product_precision


@measure_time
def main():
    scores_base, cm_per_attr_base, product_precision_base = evaluate_base_pipeline()
    scores_machine_learning, cm_per_attr_bert, product_precision_bert = evaluate_base_pipeline_with_machine_learning()
    scores_manual, cm_per_attr_manual, product_precision_manual = evaluate_base_pipeline_with_manual_mapping()

    logger.info(f"{'*'*10} Evaluation results {'*'*10}")
    logger.info(
        f"{'#'*5} Base pipeline results {'#'*5}\n{scores_base}\n{scores_base.eval_score}\n"
        f"Product precision: {product_precision_base:.2f}%"
    )
    print_confusion_matrix_per_attr(cm_per_attr_base)

    logger.info(
        f"{'#'*5} Machine learning results {'#'*5}\n{scores_machine_learning}\n"
        f"{scores_machine_learning.eval_score}\n"
        f"Product precision: {product_precision_bert:.2f}%"
    )
    print_confusion_matrix_per_attr(cm_per_attr_bert)

    logger.info(
        f"{'#'*5} Manual mapping results {'#'*5}\n{scores_manual}\n{scores_manual.eval_score}\n"
        f"Product precision: {product_precision_manual:.2f}%"
    )
    print_confusion_matrix_per_attr(cm_per_attr_manual)


if __name__ == "__main__":
    main()
