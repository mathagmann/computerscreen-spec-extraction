def convert_to_original_length(labeled_data: list[dict]) -> list[dict]:
    word = None
    active_label = None
    start, end = None, None
    last_char = 0

    merged_data = []
    for entry in labeled_data:
        entity = entry["entity"]
        entry_word = entry["word"]
        entry_start, entry_end = entry["start"], entry["end"]

        if entity.startswith("B-"):
            if start is not None and word:
                merged_data.append({"entity": active_label, "word": word, "start": start, "end": end})
            word = entry_word
            active_label = entity.replace("B-", "")
            start = entry_start
        elif entity.startswith("I-"):
            spaces = entry_start - last_char if last_char < entry_start else 0
            word += " " * spaces + entry_word.replace("##", "")
            end = entry_end
        last_char = entry_end

    if start is not None:
        merged_data.append({"entity": active_label, "word": word, "start": start, "end": end})

    return merged_data


def process_labels(labels: list[dict], preprocess=None) -> dict:
    structured_data = []
    if preprocess:
        labels = preprocess(labels)
    for label in labels:
        structured_data.append({label["entity"]: label["word"]})

    return structured_data
