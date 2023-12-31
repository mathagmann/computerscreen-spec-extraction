from pathlib import Path
from typing import Any

from loguru import logger


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


def specs_to_text(raw_specifications: dict[str, Any]) -> str:
    """Converts raw specifications into plain text for token classification.

    Formats the text in the following format:

    <property name>: <property value>
    <property name>: <property value>
    """
    return "\n".join([f"{key}: {value}" for key, value in raw_specifications.items()])


def get_best_checkpoint() -> Path:
    """Returns the best model checkpoint."""
    checkpointname_file = Path(__file__).parent / "best_model.txt"
    with open(checkpointname_file, "r") as f:
        best_checkpoint = f.read().strip()
    return Path(__file__).parent / best_checkpoint


def reconstruct_text_from_labels(labeled_data: list[dict], min_score: [float] = 0.5) -> list[dict]:
    """Reconstructs the original text from the labeled data.

    Returns a list of dicts with keys "entity", "word", "start", "end".
    """
    word = ""
    active_label = None
    start, end = None, None
    last_char = -1
    lowest_score = 1

    merged_data = []
    for entry in labeled_data:
        entity = entry["entity"]
        entry_word = entry["word"]
        entry_end = entry["end"]
        entry_start = entry["start"]
        entry_score = entry["score"]

        if entity.startswith("I-"):
            lowest_score = min(lowest_score, entry_score)
            spaces = entry_start - last_char if last_char < entry_start else 0
            word += " " * spaces + entry_word.replace("##", "")
            end = entry_end
            last_char = entry_end
        elif entity.startswith("B-") and entry_start == last_char:
            lowest_score = min(lowest_score, entry_score)
            spaces = entry_start - last_char if last_char < entry_start else 0
            word += " " * spaces + entry_word.replace("##", "")
            end = entry_end
            last_char = entry_end

        elif entity.startswith("B-"):
            if word:
                if lowest_score >= min_score:
                    merged_data.append({"entity": active_label, "word": word, "start": start, "end": end})
                else:
                    logger.debug(f"Dismiss '{word}', due score {lowest_score:.2f}<{min_score:.2f}")
            lowest_score = entry_score
            word = entry_word
            active_label = entity.replace("B-", "")
            start = entry_start
            last_char = entry_end

    if word is not None:
        if lowest_score >= min_score:
            merged_data.append({"entity": active_label, "word": word, "start": start, "end": end})
        else:
            logger.debug(f"Dismiss '{word}', due score {lowest_score}<{min_score}")

    return merged_data


def process_labels(labeled_data: list[dict], min_score: [float] = 0.5) -> dict:
    """Processes the labeled data to structured data.

    Returns a dict with keys "entity" and values "word".

    Example
    -------
    >>> labeled_data = [
    ...     {"entity": "B-NAME", "word": "HDMI", "start": 0, "end": 4},
    ...     {"entity": "I-NAME", "word": "Eingänge", "start": 5, "end": 12},
    ...     {"entity": "B-VALUE", "word": "3x", "start": 14, "end": 15},
    ... ]
    >>> process_labels(labeled_data)
    {"type-hdmi": "HDMI", "count-hdmi": "3x"}
    """
    structured_data = {}
    labels = reconstruct_text_from_labels(labeled_data, min_score)
    for label in labels:
        key = label["entity"]
        value = label["word"]
        if key in structured_data:
            if structured_data[key] != value:
                if len(value) > len(structured_data[key]):
                    logger.debug(f"Overwrite value for {key}: {structured_data[key]} replaced by {value}")
                    structured_data[key] = value
                else:
                    logger.error(f"Multiple values for {key}: {structured_data[key]} and {value}")
        else:
            structured_data[key] = value

    return structured_data
