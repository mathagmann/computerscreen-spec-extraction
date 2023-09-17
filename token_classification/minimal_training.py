from pathlib import Path
from time import sleep

from datasets import Dataset
from datasets import DatasetDict
from datasets import load_dataset
from transformers import AutoModelForTokenClassification
from transformers import AutoTokenizer
from transformers import DataCollatorForTokenClassification
from transformers import Trainer
from transformers import TrainingArguments

DATASETS_PATH = Path(__file__).parent.parent / "ner_data"


bac_raw_datasets = load_dataset("conll2003")  # TODO remove Load the CoNLL-2003 NER dataset

model_checkpoint = "bert-base-uncased"  # Use an appropriate token classification model
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

MODEL_MAX_LENGTH = tokenizer.model_max_length


def load_tsv_data(path) -> DatasetDict[str, Dataset]:
    """Loads tab-separated data from a folder.

    Loads TSV data from files named train.tsv, test.tsv, and valid.tsv.
    """
    data_files = {
        "train": str(path / "train.tsv"),
        "test": str(path / "test.tsv"),
        "valid": str(path / "valid.tsv"),
    }
    return load_dataset("csv", data_files=data_files, sep="\t")


def get_label_list(labels):
    unique_labels = set()
    for label in labels:
        try:
            unique_labels.add(label)
        except TypeError:
            unique_labels.update(set(label))
    label_list = list(unique_labels)
    label_list.sort()
    return label_list


raw_datasets = load_tsv_data(DATASETS_PATH / "computerscreens2023")
# raw_datasets = bac_raw_datasets

# features = raw_datasets["train"].features

# If the labels are of type ClassLabel, they are already integers and we have the map stored somewhere.
# Otherwise, we have to get the list of labels manually.
label_column_name = "ner_tags"
label_list = get_label_list(raw_datasets["train"][label_column_name])
label_to_id = {l: i for i, l in enumerate(label_list)}
num_labels = len(label_list)


def preprocess_function(examples) -> dict:
    """Tokenizes the sentences and convert labels to label IDs."""

    while examples["tokens"] is None:
        print("Waiting for tokens")
        print(examples["tokens"])
        sleep(1)

    tokenized_inputs = tokenizer(
        [examples["tokens"]],  # TODO remove the list, when inputs are grouped per 'sentences'
        is_split_into_words=True,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=MODEL_MAX_LENGTH,  # Adjust the max length as needed
    )

    # Convert NER tags to a list of lists of strings
    while examples["ner_tags"] is None:
        print("Waiting for ner_tags")
        sleep(1)

    labels = []
    for sentence_tags in [examples["ner_tags"]]:  # TODO remove the list, when inputs are grouped per 'sentences'
        label_ids = []
        for tag in sentence_tags:
            if tag in label_to_id:
                label_ids.append(label_to_id[tag])
            else:
                # Use the label ID for 'O' for unknown tags
                label_ids.append(label_to_id["O"])
        labels.append([label_list[label_id] for label_id in label_ids])

    tokenized_labels = tokenizer(
        labels,
        is_split_into_words=True,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=MODEL_MAX_LENGTH,  # Adjust the max length as needed
    )

    return {
        "input_ids": tokenized_inputs["input_ids"],
        "attention_mask": tokenized_inputs["attention_mask"],
        "labels": tokenized_labels["input_ids"],
    }


# bac_raw_datasets = bac_raw_datasets.map(preprocess_function, batched=True)
# tokenized_datasets = raw_datasets.map(preprocess_function)
# tokenized_datasets = raw_datasets.items()


model = AutoModelForTokenClassification.from_pretrained(model_checkpoint, num_labels=len(label_list))

args = TrainingArguments(
    "ner_model",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    num_train_epochs=3,
    weight_decay=0.01,
)

# metric = evaluate.load("seqeval")

data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

trainer = Trainer(
    model,
    args,
    train_dataset=raw_datasets["train"],
    eval_dataset=raw_datasets["valid"],
    data_collator=data_collator,
    tokenizer=tokenizer,
)
trainer.train()
