from token_classifier.ports_ml_pipeline import classify_tokens
from token_classifier.ports_ml_pipeline import convert_to_original_length
from token_classifier.ports_ml_pipeline import process_labels


def test_classify_tokens():
    text = "1x USB-C 4.0 (DisplayPort, PowerDelivery)"

    labeled_data = classify_tokens(text)

    assert len(labeled_data) > 0
    assert isinstance(labeled_data[0], dict)


def test_recover_text():
    expected_text = "1x USB-C 4.0 (DisplayPort, PowerDelivery)"
    labeled_data_output = [
        {"entity": "USBC-COUNT", "word": "1x", "start": 0, "end": 2},
        {"entity": "USBC-TYPE", "index": 3, "word": "USB-C", "start": 3, "end": 8},
        {"entity": "USBC-VERSION", "index": 6, "word": "4.0", "start": 9, "end": 12},
        {"entity": "USBC-DETAILS", "word": "(DisplayPort, PowerDelivery)", "start": 13, "end": 41},
    ]

    recovered_text = " ".join([entry["word"] for entry in labeled_data_output])

    assert expected_text == recovered_text


def test_process_labels():
    expected = {
        "USBC-COUNT": "1x",
        "USBC-TYPE": "USB-C",
        "USBC-VERSION": "4.0",
        "USBC-DETAILS": "(DisplayPort, PowerDelivery)",
    }
    labeled_data = [
        {"entity": "B-USBC-COUNT", "score": 0.64608246, "index": 1, "word": "1", "start": 0, "end": 1},
        {"entity": "I-USBC-COUNT", "score": 0.5844179, "index": 2, "word": "##x", "start": 1, "end": 2},
        {"entity": "B-USBC-TYPE", "score": 0.5901264, "index": 3, "word": "USB", "start": 3, "end": 6},
        {"entity": "I-USBC-TYPE", "score": 0.6191978, "index": 4, "word": "-", "start": 6, "end": 7},
        {"entity": "I-USBC-TYPE", "score": 0.539503, "index": 5, "word": "C", "start": 7, "end": 8},
        {"entity": "B-USBC-VERSION", "score": 0.5824647, "index": 6, "word": "4", "start": 9, "end": 10},
        {"entity": "I-USBC-VERSION", "score": 0.6756833, "index": 7, "word": ".", "start": 10, "end": 11},
        {"entity": "I-USBC-VERSION", "score": 0.5847175, "index": 8, "word": "0", "start": 11, "end": 12},
        {"entity": "B-USBC-DETAILS", "score": 0.51737446, "index": 9, "word": "(", "start": 13, "end": 14},
        {"entity": "I-USBC-DETAILS", "score": 0.55570287, "index": 10, "word": "Di", "start": 14, "end": 16},
        {"entity": "I-USBC-DETAILS", "score": 0.5763879, "index": 11, "word": "##sp", "start": 16, "end": 18},
        {"entity": "I-USBC-DETAILS", "score": 0.59236693, "index": 12, "word": "##lay", "start": 18, "end": 21},
        {"entity": "I-USBC-DETAILS", "score": 0.6441429, "index": 13, "word": "##P", "start": 21, "end": 22},
        {"entity": "I-USBC-DETAILS", "score": 0.5990919, "index": 14, "word": "##ort", "start": 22, "end": 25},
        {"entity": "I-USBC-DETAILS", "score": 0.58541834, "index": 15, "word": ",", "start": 25, "end": 26},
        {"entity": "I-USBC-DETAILS", "score": 0.53272796, "index": 16, "word": "Power", "start": 27, "end": 32},
        {"entity": "I-USBC-DETAILS", "score": 0.6130982, "index": 17, "word": "##D", "start": 32, "end": 33},
        {"entity": "I-USBC-DETAILS", "score": 0.52559006, "index": 18, "word": "##eli", "start": 33, "end": 36},
        {"entity": "I-USBC-DETAILS", "score": 0.5647807, "index": 19, "word": "##ver", "start": 36, "end": 39},
        {"entity": "I-USBC-DETAILS", "score": 0.52573746, "index": 20, "word": "##y", "start": 39, "end": 40},
        {"entity": "I-USBC-DETAILS", "score": 0.5365093, "index": 21, "word": ")", "start": 40, "end": 41},
    ]

    res = process_labels(labeled_data, preprocess=convert_to_original_length)

    assert res == expected


def test_convert_to_original_length():
    expected = [
        {"entity": "USBC-COUNT", "word": "1x", "start": 0, "end": 2},
        {"entity": "USBC-TYPE", "word": "USB-C", "start": 3, "end": 8},
        {"entity": "USBC-VERSION", "word": "4.0", "start": 9, "end": 12},
        {"entity": "USBC-DETAILS", "word": "(DisplayPort, PowerDelivery)", "start": 13, "end": 41},
    ]
    labeled_data_output = [
        {"entity": "B-USBC-COUNT", "score": 0.64608246, "index": 1, "word": "1", "start": 0, "end": 1},
        {"entity": "I-USBC-COUNT", "score": 0.5844179, "index": 2, "word": "##x", "start": 1, "end": 2},
        {"entity": "B-USBC-TYPE", "score": 0.5901264, "index": 3, "word": "USB", "start": 3, "end": 6},
        {"entity": "I-USBC-TYPE", "score": 0.6191978, "index": 4, "word": "-", "start": 6, "end": 7},
        {"entity": "I-USBC-TYPE", "score": 0.539503, "index": 5, "word": "C", "start": 7, "end": 8},
        {"entity": "B-USBC-VERSION", "score": 0.5824647, "index": 6, "word": "4", "start": 9, "end": 10},
        {"entity": "I-USBC-VERSION", "score": 0.6756833, "index": 7, "word": ".", "start": 10, "end": 11},
        {"entity": "I-USBC-VERSION", "score": 0.5847175, "index": 8, "word": "0", "start": 11, "end": 12},
        {"entity": "B-USBC-DETAILS", "score": 0.51737446, "index": 9, "word": "(", "start": 13, "end": 14},
        {"entity": "I-USBC-DETAILS", "score": 0.55570287, "index": 10, "word": "Di", "start": 14, "end": 16},
        {"entity": "I-USBC-DETAILS", "score": 0.5763879, "index": 11, "word": "##sp", "start": 16, "end": 18},
        {"entity": "I-USBC-DETAILS", "score": 0.59236693, "index": 12, "word": "##lay", "start": 18, "end": 21},
        {"entity": "I-USBC-DETAILS", "score": 0.6441429, "index": 13, "word": "##P", "start": 21, "end": 22},
        {"entity": "I-USBC-DETAILS", "score": 0.5990919, "index": 14, "word": "##ort", "start": 22, "end": 25},
        {"entity": "I-USBC-DETAILS", "score": 0.58541834, "index": 15, "word": ",", "start": 25, "end": 26},
        {"entity": "I-USBC-DETAILS", "score": 0.53272796, "index": 16, "word": "Power", "start": 27, "end": 32},
        {"entity": "I-USBC-DETAILS", "score": 0.6130982, "index": 17, "word": "##D", "start": 32, "end": 33},
        {"entity": "I-USBC-DETAILS", "score": 0.52559006, "index": 18, "word": "##eli", "start": 33, "end": 36},
        {"entity": "I-USBC-DETAILS", "score": 0.5647807, "index": 19, "word": "##ver", "start": 36, "end": 39},
        {"entity": "I-USBC-DETAILS", "score": 0.52573746, "index": 20, "word": "##y", "start": 39, "end": 40},
        {"entity": "I-USBC-DETAILS", "score": 0.5365093, "index": 21, "word": ")", "start": 40, "end": 41},
    ]

    res = convert_to_original_length(labeled_data_output)

    assert res == expected
