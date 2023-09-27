import os

import pandas as pd
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from torch.utils.data import RandomSampler
from transformers import BertTokenizer

from ner_data.computerscreens2023.computerscreens2023 import ComputerScreens2023Dataset

BATCH_SIZE = 64
BERT_TOKENS_MAX_LEN = 512
BERT_NAME = "dslim/bert-base-NER"
TEXT_COLUMN = "text"


def get_dataset(dataset_name: str) -> Dataset:
    tokens, ner_tags = load_dataset(dataset_name)
    return create_brise_dataset(tokens, ner_tags)


def create_data_loader(dataset_name: str) -> DataLoader:
    dataset = get_dataset(dataset_name)
    return DataLoader(
        dataset,
        sampler=RandomSampler(dataset),
        batch_size=BATCH_SIZE,
    )


def load_dataset(dataset_name: str) -> (pd.DataFrame, pd.DataFrame):
    labeled_data = get_x_y_dataframes(dataset_name)
    tokens = labeled_data.iloc[:, :1]
    ner_tags = labeled_data.iloc[:, 1:2]
    return tokens, ner_tags


def get_features_df_path(sub_dir):
    return os.path.join(os.path.dirname(__file__), f"{sub_dir}.tsv")


def get_x_y_dataframes(sub_dir):
    """Reads the data from the given file and returns it as a pandas DataFrame.

    The data is expected to be in the following format:
    - Each line represents a token.
    - Each paragraph is separated by an empty line.
    - The first column contains the tokens.
    - The second column contains the NER tags.

    Example:
    ```
    token1  O
    token2  O
    1x  B-HDMI-COUNT

    Returns:
        A pandas DataFrame with the following columns:
        - tokens: The tokens of the paragraph.
        - ner_tags: The NER tags of the paragraph.
    """
    separator = "\t"

    # read the file line by line
    with open(get_features_df_path(sub_dir), "r") as file_object:
        _ = file_object.readline()  # read column label
        data = {"tokens": [], "ner_tags": []}
        paragraph = {"tokens": [], "ner_tags": []}

        for line in file_object:
            line = line.strip()  # Remove leading/trailing whitespace
            if not line:  # Empty line indicates the end of a paragraph
                if paragraph["tokens"]:
                    data["tokens"].append(paragraph["tokens"])
                    data["ner_tags"].append(paragraph["ner_tags"])
                paragraph = {"tokens": [], "ner_tags": []}
            else:
                tokens, ner_tags = line.split(separator)
                paragraph["tokens"].append(tokens)
                paragraph["ner_tags"].append(ner_tags)
        data["tokens"].append(paragraph["tokens"])
        data["ner_tags"].append(paragraph["ner_tags"])

    assert len(data["tokens"]) == len(data["ner_tags"])

    # Convert the grouped data to a pandas DataFrame
    return pd.DataFrame(data)


def create_brise_dataset(tokens: pd.DataFrame, ner_tags: pd.DataFrame):
    tokenizer = BertTokenizer.from_pretrained(BERT_NAME)
    return ComputerScreens2023Dataset(
        tokens,
        ner_tags,
        tokenizer,
        BERT_TOKENS_MAX_LEN,
        TEXT_COLUMN,
    )
