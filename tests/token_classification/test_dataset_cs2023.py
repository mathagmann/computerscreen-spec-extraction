from pathlib import Path
from unittest import mock

import pytest
from datasets import load_dataset
from datasets import load_dataset_builder
from transformers import BertTokenizer

from ner_data.computerscreens2023.prepare_data import create_data_loader
from ner_data.computerscreens2023.shuffle_and_split import _split_data

DATASETS_PATH = Path(__file__).parent.parent.parent / "ner_data"
TOKENIZER = BertTokenizer.from_pretrained("bert-base-uncased")


def test_shuffle_and_split():
    item_count = 10
    data = [([f"sent_{i}word1", f"sent_{i}word2"], [f"label{i}_1", f"label{i}_2"]) for i in range(item_count)]

    res = _split_data(data, train_ratio=0.8, test_ratio=0.1)

    assert res
    assert len(res["train"]) == 8
    assert len(res["valid"]) == 1
    assert len(res["test"]) == 1

    # check all items unique and no duplication
    # check items from train are not in valid or test
    assert all(item not in res["valid"] for item in res["train"])
    assert all(item not in res["test"] for item in res["train"])

    # check items from valid are not in train or test
    assert all(item not in res["train"] for item in res["valid"])
    assert all(item not in res["test"] for item in res["valid"])

    # check items from test are not in train or valid
    assert all(item not in res["train"] for item in res["test"])
    assert all(item not in res["valid"] for item in res["test"])


def test_custom_dataset():
    data_files = {
        "train": str(DATASETS_PATH / "computerscreens2023" / "train.tsv"),
        "test": str(DATASETS_PATH / "computerscreens2023" / "test.tsv"),
        "valid": str(DATASETS_PATH / "computerscreens2023" / "valid.tsv"),
    }
    local_csv_dataset = load_dataset("csv", data_files=data_files, sep="\t")

    for dataset in local_csv_dataset.values():
        assert dataset.column_names == ["tokens", "ner_tags"]


@pytest.mark.skip(reason="This test is not yet implemented.")
def test_custom_dataset_loader():
    script_path = str(DATASETS_PATH / "computerscreens2023")
    local_csv_dataset = load_dataset_builder(script_path)

    for dataset in local_csv_dataset.values():
        assert dataset.column_names == ["token", "ner_tags"]


def test_create_brise_dataset():
    dataloader = create_data_loader("train")
    expected_result = {
        "text_rebuild": mock.ANY,
        "input_ids": mock.ANY,
        "attention_mask": mock.ANY,
        "labels": mock.ANY,
    }

    assert dataloader
    assert dataloader.dataset[0] == expected_result
