from pathlib import Path

import transformers

from token_classification.utilities import get_best_checkpoint


def bootstrap(model_checkpoint: Path = None) -> transformers.Pipeline:
    """Returns a pipeline for token classification."""
    if model_checkpoint is None:
        # late evaluation of model checkpoint simplifies testing
        model_checkpoint = get_best_checkpoint()
    model = transformers.AutoModelForTokenClassification.from_pretrained(model_checkpoint)
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_checkpoint)
    return transformers.pipeline(task="ner", model=model, tokenizer=tokenizer)
