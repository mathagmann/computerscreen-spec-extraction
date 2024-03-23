from loguru import logger

from config import PRODUCT_CATALOG_DIR
from config import ROOT_DIR
from spec_extraction.bootstrap import bootstrap as extraction_bootstrap
from spec_extraction.evaluation.evaluate import evaluate_pipeline
from spec_extraction.evaluation.evaluate import measure_time

DEFAULT_FIELD_MAPPINGS = ROOT_DIR / "spec_extraction" / "preparation" / "field_mappings.json"


@measure_time
def evaluate_base_pipeline():
    processing_instance = extraction_bootstrap(field_mappings=DEFAULT_FIELD_MAPPINGS, machine_learning_enabled=False)
    processing_instance.merge_monitor_specs(PRODUCT_CATALOG_DIR)

    confusion_matrix, product_precision = evaluate_pipeline(processing_instance)

    return confusion_matrix, product_precision


@measure_time
def evaluate_base_pipeline_with_machine_learning():
    processing_instance = extraction_bootstrap(field_mappings=DEFAULT_FIELD_MAPPINGS, machine_learning_enabled=True)

    confusion_matrix, product_precision = evaluate_pipeline(processing_instance)

    return confusion_matrix, product_precision


@measure_time
def evaluate_base_pipeline_with_manual_mapping():
    enhanced_field_mappings = ROOT_DIR / "spec_extraction" / "preparation" / "field_mappings_enhanced_mylemon.json"
    processing_instance = extraction_bootstrap(field_mappings=enhanced_field_mappings, machine_learning_enabled=False)
    processing_instance.merge_monitor_specs(PRODUCT_CATALOG_DIR)

    confusion_matrix, product_precision = evaluate_pipeline(processing_instance)

    return confusion_matrix, product_precision


@measure_time
def main():
    scores_base, product_precision_base = evaluate_base_pipeline()
    scores_machine_learning, product_precision_machine_learning = evaluate_base_pipeline_with_machine_learning()
    scores_manual, product_precision_manual = evaluate_base_pipeline_with_manual_mapping()

    logger.info(f"{'*'*10} Evaluation results {'*'*10}")
    logger.info(f"Base pipeline:\nConfusion matrix{scores_base}\n{scores_base.eval_score}")
    logger.info(f"Machine learning:\nConfusion matrix{scores_machine_learning}\n{scores_machine_learning.eval_score}")
    logger.info(f"Manual mapping:\nConfusion matrix{scores_manual}\n{scores_manual.eval_score}")


if __name__ == "__main__":
    main()
