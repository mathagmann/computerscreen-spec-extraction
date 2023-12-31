import json
from pathlib import Path
from typing import Dict

from loguru import logger


class BagOfWords:
    def __init__(self, bow_file: Path = None):
        self.bagofwords: Dict[str:set] = {}
        self.bow_file: Path = bow_file

    def add_word(self, cat_key: str, text: str):
        """Adds mapping from merchant key to catalog key."""
        word_list = self.bagofwords.get(cat_key, set())
        word_list.add(text)
        self.bagofwords[cat_key] = word_list

    def save_to_disk(self):
        """Saves BagOfWords to file."""
        bow = {key: list(value_set) for key, value_set in self.bagofwords.items()}
        with open(self.bow_file, "w") as outfile:
            json.dump(bow, outfile, indent=4, sort_keys=True)
        filename = str(self.bow_file).split("/")[-1]
        logger.debug(f"Flushed mappings to {filename}")
