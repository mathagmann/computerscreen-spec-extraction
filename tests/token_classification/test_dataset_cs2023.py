from pathlib import Path

from datasets import load_from_disk
from transformers import BertTokenizer

from ner_data.computerscreens2023.computerscreens2023 import ComputerScreen2023Dataset

DATASETS_PATH = Path(__file__).parent.parent.parent / "ner_data"
TOKENIZER = BertTokenizer.from_pretrained("bert-base-uncased")


def test_computer_screens_2023_dataset():
    dataset = ComputerScreen2023Dataset(
        DATASETS_PATH / "computerscreens2023" / "computerscreens2023_labeled.conll", TOKENIZER, max_seq_length=128
    )

    assert dataset
    # assert dataset.__getitem__(0)


def test_load_dataset():
    train_dataset = ComputerScreen2023Dataset(
        DATASETS_PATH / "computerscreens2023" / "train.txt", TOKENIZER, max_seq_length=128
    )

    train = load_from_disk(train_dataset)

    assert train
