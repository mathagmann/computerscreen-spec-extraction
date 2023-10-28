from transformers import AutoModelForTokenClassification
from transformers import AutoTokenizer
from transformers import pipeline

from token_classification.utilities import get_best_checkpoint


def setup():
    """Returns a pipeline for token classification."""
    checkpoint = get_best_checkpoint()
    model = AutoModelForTokenClassification.from_pretrained(checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    return pipeline(task="ner", model=model, tokenizer=tokenizer)
