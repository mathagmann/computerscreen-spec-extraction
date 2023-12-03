import os
from typing import Any

import torch
from loguru import logger
from seqeval import metrics
from transformers import AutoConfig
from transformers import AutoModelForTokenClassification
from transformers import AutoTokenizer
from transformers import DataCollatorForTokenClassification
from transformers import Trainer
from transformers import TrainingArguments
from transformers import get_linear_schedule_with_warmup

from ner_data.computerscreens2023.prepare_data import get_dataset
from token_classification.utilities import create_label2id

os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "true"

model = "dslim/bert-base-NER"  # Use an appropriate token classification model
tokenizer = AutoTokenizer.from_pretrained(model)

custom_labels = [
    "type-hdmi",
    "count-hdmi",
    "version-hdmi",
    "details-hdmi",
    "type-displayport",
    "count-displayport",
    "version-displayport",
    "details-displayport",
]
label2id = create_label2id(custom_labels)
id2label = {i: label for label, i in label2id.items()}  # label2id is your label mapping

train_dataset = get_dataset("train")
test_dataset = get_dataset("test")
valid_dataset = get_dataset("valid")


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

    logger.debug(f"Sentence length {len(pred_labels)}")

    # Calculate and return evaluation metrics
    accuracy = metrics.accuracy_score([true_labels], [pred_labels])
    f1 = metrics.f1_score([true_labels], [pred_labels])
    precision = metrics.precision_score([true_labels], [pred_labels])
    recall = metrics.recall_score([true_labels], [pred_labels])

    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}


def run_training(model_checkpoint, epochs: int = 30, name: str = "ner_model"):
    # Create a new model with a custom number of labels
    config = AutoConfig.from_pretrained(model_checkpoint)
    config.id2label = id2label
    config.label2id = label2id
    config.num_labels = len(label2id)
    base_model = AutoModelForTokenClassification.from_pretrained(
        model_checkpoint, config=config, ignore_mismatched_sizes=True
    )

    args = TrainingArguments(
        name,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        num_train_epochs=epochs,
        save_total_limit=2,
        load_best_model_at_end=True,
    )

    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

    # Create AdamW Optimizer
    optimizer = torch.optim.AdamW(base_model.parameters(), lr=2e-5, weight_decay=0.01)

    # Create a learning rate scheduler
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=0, num_training_steps=len(train_dataset) * epochs
    )

    trainer = Trainer(
        base_model,
        args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        optimizers=(optimizer, scheduler),
    )
    trainer.train()

    # Evaluate on the test dataset
    results = trainer.evaluate(eval_dataset=test_dataset)
    logger.info(f"Evaluation results:\n{results}")

    print(f"Best model: {trainer.state.best_model_checkpoint}")

    # save name of best model
    with open("best_model.txt", "w") as f:
        f.write(trainer.state.best_model_checkpoint)


run_training(model)
