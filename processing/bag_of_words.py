import json
from pathlib import Path
from typing import Dict

from loguru import logger


class BagOfWords:
    def __init__(self):
        self.bagofwords: Dict[str:set] = {}
        self.filepath = Path(".") / "src" / "processing" / "bow.json"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()

    def add_word(self, cat_key: str, text: str):
        """Adds mapping from merchant key to catalog key."""
        word_list = self.bagofwords.get(cat_key, set())
        logger.info(f"Add bow to '{cat_key}': '{text}'")
        word_list.add(text)
        self.bagofwords[cat_key] = word_list

    def flush(self):
        bow = {key: list(value_set) for key, value_set in self.bagofwords.items()}
        with open(self.filepath, "w") as outfile:
            json.dump(bow, outfile, indent=4, sort_keys=True)
        filename = str(self.filepath).split("/")[-1]
        logger.debug(f"Flushed mappings to {filename}")
