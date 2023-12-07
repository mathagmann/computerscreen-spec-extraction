from data_generation import build_corpus


def test_flatten_specification_dict():
    expected_str = "size:27;resolution:1920x1080"
    specs = {"size": "27", "resolution": "1920x1080"}

    flattened_res = build_corpus.flatten_specification_dict(specs)

    assert flattened_res == expected_str
