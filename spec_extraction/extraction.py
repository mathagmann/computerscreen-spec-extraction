import json
from functools import lru_cache
from pathlib import Path
from typing import List

from loguru import logger

from spec_extraction import exceptions
from spec_extraction.bag_of_words import BagOfWords

CONFIG_DIR = Path(__file__).parent / "preparation"


def clean_text(text):
    """Removes invisible characters."""
    text = text.replace("cd/m2", "cd/m\u00b2")
    return text.replace("\u200b", "").strip()  # remove zero-width space


def apply_synonyms(text: str) -> str:
    """Replaces synonyms in a text."""
    synonyms = load_synonyms()
    for key, value in synonyms.items():
        if key.lower() == text.lower():
            logger.debug(f"Synonym found '{text}' replaced with '{value}'")
            return value
    return text


@lru_cache(maxsize=1)
def load_synonyms():
    """Loads synonyms from a file."""
    with open(CONFIG_DIR / "synonyms.json") as json_file:
        data = json.load(json_file)
    return data


class Feature:
    def __init__(
        self,
        name,  # MonitorSpecifications
        formatter=apply_synonyms,
        pattern=None,
        match_to=None,
        string_repr: [str] = None,
    ):
        self.name = name.value
        self.formatter = formatter  # DataExtractor function
        self.pattern = pattern  # regex pattern
        self.match_to = match_to  # list of keys to map to
        self.string_repr = string_repr  # string format placeholder

    def parse(self, text: str) -> object:
        """Parses a text to a structured value.

        Raises ParserError if parsing fails.
        """
        try:
            if self.formatter and self.match_to and self.pattern:
                return self.formatter(text, self.pattern, self.match_to)
            elif self.formatter and self.pattern:
                return self.formatter(text, self.pattern)
            elif self.formatter:
                return self.formatter(text)
        except exceptions.TextExtractionError as e:
            raise exceptions.ParserError(f"ParseError, Could not parse from text '{text}'") from e
        except KeyError as e:
            raise exceptions.ParserError(f"KeyError, Could not parse from text '{text}'") from e
        except TypeError as e:
            raise exceptions.ParserError(f"TypeError, Could not parse from text '{text}'") from e
        raise exceptions.ParserError(f"No parser specified to get from text '{text}'")

    def nice_output(self, data) -> str:
        """Returns a nice output of the data."""
        output = []
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            return ", ".join(data)
        elif isinstance(data, dict):
            for k in sorted(data.keys()):
                value = data[k]
                output.append(f"{value}")

        if self.string_repr:
            return self.string_repr.format(**data)
        return "\u00a0".join(output)


class MLFeature:
    def __init__(self, name, string_repr: [str] = None, repr_optional: [str] = None):
        self.name = name.value
        self.string_repr = string_repr  # string format placeholder
        self.repr_optional = repr_optional

    def nice_output(self, data) -> str:
        """Returns a nice output of the data."""
        formatted_string = self.string_repr.format(**data)
        for optional_part in self.repr_optional:
            try:
                formatted_string += optional_part.format(**data)
            except KeyError:
                continue

        return formatted_string


class FeatureGroup:
    """Groups related features together."""

    def __init__(self, name: str, features: List[Feature | MLFeature] = None):
        self.name = name
        if features is None:
            features = []
        self.features = features

    def nice_output(self, full_data: dict, separator: str = ", ") -> str:
        """Returns a nicely formatted output of the data."""
        output = []
        for feature in self.features:
            try:
                data = full_data[feature.name]
                output.append(feature.nice_output(data))
            except KeyError:
                pass
            except TypeError:
                logger.warning(f"Type error '{feature.name}'")
                raise exceptions.NicePlotError
        if not output:
            raise exceptions.NicePlotError("Empty output")
        return separator.join(output)


class Parser:
    """Parses a semi-structured specifications to structured specifications."""

    def __init__(
        self,
        specifications: List[FeatureGroup],
        separator: str = "\n",
        bow_file: Path = Path(__file__).parent / "preparation" / "bow.json",
    ):
        self.specifications = specifications
        self.separator = separator
        self.bow_file = bow_file
        self.parser = {}
        self.last_data = None
        self.bow = None
        self.parse_count = 0

        self._setup()

    def _setup(self):
        """Build parser configuration from feature groups.

        Initializes the bag of words.
        """
        for feature_group in self.specifications:
            for feature in feature_group.features:
                self.parser[feature.name] = feature
        self.bow = BagOfWords(self.bow_file)

    def parse(self, raw_specifications: dict) -> dict:
        """Parses features from raw specifications and returns a plain dict."""
        result = {}
        for feature_name, feature_value in raw_specifications.items():
            clean_value = clean_text(feature_value)
            if feature_name in self.parser and isinstance(self.parser[feature_name], Feature):
                try:
                    result[feature_name] = self.parser[feature_name].parse(clean_value)
                except KeyError as e:
                    logger.warning(f"No parser for feature '{feature_name}': {e}")
                    self.bow.add_word(feature_name, feature_value)
                except exceptions.ParserError as e:
                    logger.warning(f"Parsing of feature '{feature_name}' failed: {e}")
                    self.bow.add_word(feature_name, feature_value)
        self.parse_count += 1
        if self.parse_count % 1000 == 0:  # last entries not written to file
            self.bow.save_to_disk()
        return result

    def nice_output(self, parsed_data: dict) -> str:
        output = []
        for feature_group in self.specifications:
            try:
                output.append(f"{feature_group.name + ':':<30} {feature_group.nice_output(parsed_data)}")
            except KeyError:
                pass
            except exceptions.NicePlotError:
                pass
        output = [item for item in output if item]
        return self.separator.join(output)

    def items(self, parsed_data: dict) -> dict:
        output = {}
        for feature_group in self.specifications:
            try:
                output[feature_group.name] = feature_group.nice_output(parsed_data)
            except KeyError:
                pass
            except exceptions.NicePlotError:
                pass
        return output
