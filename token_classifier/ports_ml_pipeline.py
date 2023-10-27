def convert_to_original_length(labeled_data: list[dict]) -> list[dict]:
    word = ""
    active_label = None
    start, end = None, None
    last_char = -1

    merged_data = []
    for entry in labeled_data:
        entity = entry["entity"]
        entry_word = entry["word"]
        entry_end = entry["end"]
        entry_start = entry["start"]

        if entity.startswith("I-"):
            spaces = entry_start - last_char if last_char < entry_start else 0
            word += " " * spaces + entry_word.replace("##", "")
            end = entry_end
            last_char = entry_end
        elif entity.startswith("B-") and entry_start == last_char:
            spaces = entry_start - last_char if last_char < entry_start else 0
            word += " " * spaces + entry_word.replace("##", "")
            end = entry_end
            last_char = entry_end
        elif entity.startswith("B-"):
            if word:
                merged_data.append({"entity": active_label, "word": word, "start": start, "end": end})
            word = entry_word
            active_label = entity.replace("B-", "")
            start = entry_start
            last_char = entry_end

    if start is not None:
        merged_data.append({"entity": active_label, "word": word, "start": start, "end": end})

    return merged_data


def process_labels(labels: list[dict], preprocess=None) -> dict:
    structured_data = {}
    if preprocess:
        labels = preprocess(labels)
    for label in labels:
        key = label["entity"]
        value = label["word"]
        if key in structured_data:
            if structured_data[key] != value:
                raise ValueError(f"Key {key} has multiple values: {structured_data[key]} and {value}")
        else:
            structured_data[key] = value

    return structured_data
