from unittest import mock

import pytest


@pytest.fixture
def mock_synonyms():
    def apply_synonyms(text: str) -> str:
        synonyms = {
            "zero frame": "Slim Bezel",
            "schmaler Rahmen": "Slim Bezel",
            "entspiegelt": "matt",
        }
        for key, value in synonyms.items():
            if key.lower() == text.lower():
                return value
        return text

    with mock.patch("spec_extraction.extraction_config.apply_synonyms", apply_synonyms):
        yield
