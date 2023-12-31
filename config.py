from pathlib import Path

DATASET_NAME = "computerscreens2023"  # Switch between datasets here
DATASET_NAME = "minimal_testdata"  # Switch between datasets here

ROOT_DIR = Path(__file__).parent
LOG_DIR = ROOT_DIR / "logs"
TEST_DIR = ROOT_DIR / "tests"

ROOT_DATA_DIR = ROOT_DIR / "data"
DATA_DIR = ROOT_DATA_DIR / DATASET_NAME

PRODUCT_CATALOG_DIR = ROOT_DATA_DIR / f"{DATASET_NAME}_product_catalog"
RAW_SPECIFICATIONS_DIR = ROOT_DATA_DIR / f"{DATASET_NAME}_raw_specs"
