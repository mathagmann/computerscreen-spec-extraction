"""Converts the CoNLL file into train, valid, and test .tsv sets.

Creates tab-separated .tsv files with two columns: word, label.
"""
import random
from pathlib import Path
from typing import Tuple

DELIMITER_CONLL = " -X- _ "
DELIMITER_TSV = "\t"

COLUMNS = ["tokens", "ner_tags"]


def _read_data(file_path):
    """Reads CoNLL data and returns it as a list of (text, labels) pairs."""
    inputs, labels = [], []
    with open(file_path, "r") as f:
        token_list, label_list = [], []
        for i, line in enumerate(f):
            line = line.strip()
            if line.startswith("-DOCSTART-"):
                if i == 0:
                    continue
                raise ValueError("Only the first line should be -DOCSTART-")
            if line == "":
                if len(token_list) > 0:
                    assert len(token_list) == len(label_list), "Length of tokens and labels have to be the same."
                    inputs.append(token_list)
                    labels.append(label_list)
                token_list, label_list = [], []
                continue

            splits = line.split(DELIMITER_CONLL)  # CONLL format with just two non-empty columns
            token = splits[0]
            label = splits[1]

            token_list.append(token)
            label_list.append(label)
        inputs.append(token_list)
        labels.append(label_list)
    return list(zip(inputs, labels))


def _split_data(data: list[Tuple], train_ratio=0.8, test_ratio=0.1) -> dict[str, list]:
    """Splits the data randomly into train, valid, and test sets."""
    assert len(data) >= 3, "Data must have at least 3 samples to split into train, valid, and test sets."
    random.shuffle(data)

    train_size = max(1, int(len(data) * train_ratio))
    test_size = max(1, int(len(data) * test_ratio))
    valid_size = len(data) - train_size - test_size

    first_idx = train_size
    second_idx = train_size + valid_size
    train_data = data[:first_idx]
    valid_data = data[first_idx:second_idx]
    test_data = data[second_idx:]

    assert len(train_data) > 0, "Train set must have at least 1 sample."
    assert len(test_data) > 0, "Test set must have at least 1 sample."
    assert len(valid_data) > 0, "Valid set must have at least 1 sample."

    print(f"Split {len(data)} items: (Train: {len(train_data)}, Valid: {len(valid_data)}, Test: {len(test_data)})\n")
    return {"train": train_data, "valid": valid_data, "test": test_data}


def _write_data(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"{DELIMITER_TSV.join(COLUMNS)}")
        for item in data:
            words, labels = item
            assert len(words) == len(labels), "Length of tokens and labels have to be the same."

            file.write("\n")
            for word, label in zip(words, labels):
                if word == '"':
                    word = '\\"'  # escape double quotes
                file.write(f"{word}{DELIMITER_TSV}{label}\n")


def shuffle_and_split(conll_file, overwrite=False):
    file_content = _read_data(conll_file)
    datasets = _split_data(file_content, train_ratio=0.8, test_ratio=0.1)

    if not overwrite:
        for file in datasets.keys():
            if Path(f"{file}.tsv").exists():
                raise FileExistsError(f"File {file} already exists. Please remove all .tsv files and try again.")

    for key, data in datasets.items():
        print(f"{key}: {len(data)}")
        _write_data(key + ".tsv", data)


if __name__ == "__main__":
    shuffle_and_split("computerscreens2023_labeled.conll", overwrite=True)
    print("Data split and saved three .tsv files in the current directory.")
