import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import BertTokenizer

label2id = {
    "O": 0,
    "B-type-hdmi": 1,
    "I-type-hdmi": 2,
    "B-count-hdmi": 3,
    "I-count-hdmi": 4,
    "B-version-hdmi": 5,
    "I-version-hdmi": 6,
    "B-details-hdmi": 7,
    "I-details-hdmi": 8,
}


def tokenize_and_preserve_labels(sentence: list, text_labels: list, tokenizer):
    """
    Word piece tokenization makes it difficult to match word labels
    back up with individual word pieces. This function tokenizes each
    word one at a time so that it is easier to preserve the correct
    label for each subword. It is, of course, a bit slower in processing
    time, but it will help our model achieve higher accuracy.

    Modified from
    https://github.com/chambliss/Multilingual_NER/blob/master/python/utils/main_utils.py#L118
    """

    tokenized_sentence = []
    labels = []

    assert len(sentence) == len(text_labels)

    for word, label in zip(sentence, text_labels):
        # Tokenize the word and count # of subwords the word is broken into
        tokenized_word = tokenizer.tokenize(word)
        n_subwords = len(tokenized_word)

        # Add the tokenized word to the final tokenized word list
        tokenized_sentence.extend(tokenized_word)

        # Add the same label to the new list of labels `n_subwords` times
        labels.extend([label] * n_subwords)

    assert len(tokenized_sentence) == len(labels)
    return tokenized_sentence, labels


class ComputerScreens2023Dataset(Dataset):
    def __init__(
        self,
        data: pd.DataFrame,
        labels: pd.DataFrame,
        tokenizer: BertTokenizer,
        max_length: int,
        text_column: str,
    ):
        self.tokenizer = tokenizer
        self.data = data
        self.labels = labels
        self.max_length = max_length
        self.text_column = text_column
        assert len(data) == len(labels)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        # step 1: tokenize (and adapt corresponding labels)
        sentence = self.data.iloc[index]
        word_labels = self.labels.iloc[index]
        tokenized_sentence, labels = tokenize_and_preserve_labels(sentence.tokens, word_labels.ner_tags, self.tokenizer)

        # step 2: add special tokens (and corresponding labels)
        tokenized_sentence = ["[CLS]"] + tokenized_sentence + ["[SEP]"]  # add special tokens
        labels.insert(0, "O")  # add outside label for [CLS] token
        labels.insert(-1, "O")  # add outside label for [SEP] token

        # step 3: truncating/padding
        maxlen = self.max_length

        if len(tokenized_sentence) > maxlen:
            # truncate
            tokenized_sentence = tokenized_sentence[:maxlen]
            labels = labels[:maxlen]
        else:
            # pad
            tokenized_sentence = tokenized_sentence + ["[PAD]" for _ in range(maxlen - len(tokenized_sentence))]
            labels = labels + ["O" for _ in range(maxlen - len(labels))]

        # step 4: obtain the attention mask
        attention_mask = [1 if tok != "[PAD]" else 0 for tok in tokenized_sentence]

        # step 5: convert tokens to input ids
        input_ids = self.tokenizer.convert_tokens_to_ids(tokenized_sentence)

        label_ids = [label2id[label] for label in labels]

        return dict(
            text_rebuild=" ".join(sentence.tokens),  # doesn't match input exactly, because of tokenization
            input_ids=torch.tensor(input_ids, dtype=torch.long),
            attention_mask=torch.tensor(attention_mask, dtype=torch.long),
            labels=torch.tensor(label_ids, dtype=torch.long),
        )
