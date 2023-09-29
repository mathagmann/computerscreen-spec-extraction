from typing import Any

from datasets import load_metric
from seqeval.metrics import accuracy_score
from seqeval.metrics import f1_score
from seqeval.metrics import precision_score
from seqeval.metrics import recall_score
from transformers import AutoConfig
from transformers import AutoModelForTokenClassification
from transformers import AutoTokenizer
from transformers import DataCollatorForTokenClassification
from transformers import Trainer
from transformers import TrainingArguments

from ner_data.computerscreens2023.prepare_data import get_dataset


def create_label2id(labels: list[str]) -> dict[str, int]:
    """Create label2id mapping from a list of labels.

    Returns
    -------
    dict[str, int]
        Mapping from label to id.

    Examples
    --------
    >>> create_label2id(["type-hdmi", "count-hdmi"])
    {'B-type-hdmi': 1, 'I-type-hdmi': 2, 'B-count-hdmi': 3, 'I-count-hdmi': 4, 'O': 0}
    """
    label_to_id = {}
    for i, label in enumerate(labels):
        label_to_id[f"B-{label}"] = i * 2 + 1
        label_to_id[f"I-{label}"] = i * 2 + 2
    label_to_id["O"] = 0
    return label_to_id


model_checkpoint = "dslim/bert-base-NER"  # Use an appropriate token classification model
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

custom_labels = [
    "type-hdmi",
    "count-hdmi",
    "version-hdmi",
    "details-hdmi",
]
label2id = create_label2id(custom_labels)
id2label = {i: label for label, i in label2id.items()}  # label2id is your label mapping

train_dataset = get_dataset("train")
test_dataset = get_dataset("test")
valid_dataset = get_dataset("valid")

metric = load_metric("seqeval")


def compute_metrics(p) -> dict[str, Any]:
    predictions, labels = p

    predictions = predictions.argmax(axis=2)

    # Convert ids to labels
    pred_labels = []
    true_labels = []
    for i in range(len(labels)):
        pred = [id2label[pred_id] for pred_id in predictions[i]]
        true = [id2label[true_id] for true_id in labels[i]]
        pred_labels.extend(pred)
        true_labels.extend(true)

    # Calculate and return evaluation metrics
    accuracy = accuracy_score([true_labels], [pred_labels])
    f1 = f1_score([true_labels], [pred_labels])
    precision = precision_score([true_labels], [pred_labels])
    recall = recall_score([true_labels], [pred_labels])
    # classification_rep = classification_report([true_labels], [pred_labels])

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        # "classification_report": classification_rep,
    }


def run_training(epochs: int = 3, name: str = "ner_model"):
    # Create a new model with a custom number of labels
    config = AutoConfig.from_pretrained(model_checkpoint)
    config.id2label = id2label
    config.label2id = label2id
    config.num_labels = len(label2id)
    model = AutoModelForTokenClassification.from_pretrained(model_checkpoint, config=config)

    args = TrainingArguments(
        name,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        num_train_epochs=epochs,
        weight_decay=0.01,
    )

    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

    trainer = Trainer(
        model,
        args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    trainer.train()

    # Evaluate on the test dataset
    results = trainer.evaluate(eval_dataset=test_dataset)
    print("Evaluation results:", results)

    print(f"Best model: {trainer.state.best_model_checkpoint}")


if __name__ == "__main__":
    run_training()
