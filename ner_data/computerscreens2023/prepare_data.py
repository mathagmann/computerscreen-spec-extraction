import os

import pandas as pd
from torch.utils.data import DataLoader
from torch.utils.data import RandomSampler
from transformers import BertTokenizer

from ner_data.computerscreens2023.brise_dataset import BriseDataset

BATCH_SIZE = 512
BERT_TOKENS_MAX_LEN = 512
BERT_NAME = "bert-base-german-cased"
TEXT_COLUMN = "text"


def create_data_loader(dataset_name, attributes):
    x, y = load_dataset(dataset_name, attributes)
    dataset = create_brise_dataset(x, y)
    return DataLoader(
        dataset,
        sampler=RandomSampler(dataset),
        batch_size=BATCH_SIZE,
    )


def load_dataset(dataset_name, attributes):
    data, _, labels = get_x_y_dataframes(dataset_name)
    return data.iloc[:, :2], labels.filter(attributes)


def get_labels_df_path(sub_dir):
    return os.path.join(os.path.dirname(__file__), "input", f"{sub_dir}_labels.csv")


def get_features_df_path(sub_dir):
    return os.path.join(os.path.dirname(__file__), "input", f"{sub_dir}_features.csv")


def get_x_y_dataframes(sub_dir):
    feats_df = pd.read_csv(get_features_df_path(sub_dir))
    labels_df = pd.read_csv(get_labels_df_path(sub_dir))
    return feats_df, feats_df.iloc[:, 2:], labels_df


def create_brise_dataset(x, y):
    tokenizer = BertTokenizer.from_pretrained(BERT_NAME, do_lower_case=True)
    return BriseDataset(
        x,
        y,
        tokenizer,
        BERT_TOKENS_MAX_LEN,
        TEXT_COLUMN,
    )
