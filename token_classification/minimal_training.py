from pathlib import Path

from transformers import AutoModelForTokenClassification
from transformers import AutoTokenizer
from transformers import DataCollatorForTokenClassification
from transformers import Trainer
from transformers import TrainingArguments

from ner_data.computerscreens2023.brise_dataset import label2id
from ner_data.computerscreens2023.prepare_data import get_dataset

DATASETS_PATH = Path(__file__).parent.parent / "ner_data"

model_checkpoint = "bert-base-cased"  # Use an appropriate token classification model
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

train_dataset = get_dataset("train")
test_dataset = get_dataset("test")
valid_dataset = get_dataset("valid")

num_labels = len(label2id)
model = AutoModelForTokenClassification.from_pretrained(model_checkpoint, num_labels=num_labels)

args = TrainingArguments(
    "ner_model",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    num_train_epochs=3,
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
)
trainer.train()
