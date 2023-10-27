import json
import re
from functools import lru_cache
from typing import List

from loguru import logger

from spec_extraction import exceptions
from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.extraction import Feature
from spec_extraction.extraction import FeatureGroup
from spec_extraction.extraction import Parser

"""Data extraction functions for the Parser."""


def create_pattern_structure(text: str, pattern, map_to: List[str] = None) -> str:
    """Returns the mapped of a regex pattern."""

    def findall(pattern_: str, text_: str, mapping) -> List:
        """Returns all matches of a regex pattern in a list."""
        regex_matches = []
        while True:
            match_res = re.search(pattern_, text_)
            if not match_res:
                break

            result = {}
            for key in mapping:
                result[key] = match_res.group(mapping.index(key) + 1)
            regex_matches.append(result)

            text_ = text_[match_res.end() :]
        return regex_matches

    extracted = re.search(pattern, text)
    if not map_to:
        try:
            return extracted.group()
        except AttributeError:
            logger.error("No match found for pattern: %s", pattern)

    if extracted:
        if map_to:
            if isinstance(map_to[0], list):  # map to a List of entries
                return findall(pattern, text, map_to[0])
            else:  # map to dict
                res = {}
                for idx, value in enumerate(extracted.groups()):
                    res[map_to[idx]] = value
                return res
    raise exceptions.TextExtractionError(f"Could not extract data from '{text}' with pattern '{pattern}'")


def create_listing(text: str) -> List:
    """Creates a listing from a text and strips white space."""
    return [apply_synonyms(item.strip()).strip() for item in text.split(", ")]


def apply_synonyms(text: str) -> str:
    """Replaces synonyms in a text."""
    # synonyms = load_synonyms()
    # for key, value in synonyms.items():
    #     if key.lower() == text.lower():
    #         logger.debug(f"Synonym found '{text}' replaced with '{value}'")
    #         return value
    return text


@lru_cache(maxsize=1)
def load_synonyms():
    """Loads synonyms from a file."""
    with open("synonyms.json") as json_file:
        data = json.load(json_file)
    return data


monitor_spec = [
    FeatureGroup(
        "EAN",
        [
            Feature(
                MonitorSpecifications.EAN,
                create_pattern_structure,
                r"(\d{12}\d?)",
            ),
        ],
    ),
    FeatureGroup(
        "Diagonale",
        [
            Feature(
                MonitorSpecifications.DIAGONAL_INCH,
                create_pattern_structure,
                r"(\d+[.,]*\d*)\s*(\"|Zoll)",  # 27 "
                ["1_value", "z_unit"],
                separator="",
            ),
            Feature(
                MonitorSpecifications.DIAGONAL_CM,
                create_pattern_structure,
                r"(\d+[.,]*\d*)\s*(mm|cm|m)",  # 68.6 cm
                ["1_value", "z_unit"],
            ),
        ],
    ),
    FeatureGroup(
        "Marke",
        [
            Feature(MonitorSpecifications.BRAND),
        ],
    ),
    FeatureGroup(
        "Auflösung",
        [
            Feature(
                MonitorSpecifications.RESOLUTION,
                create_pattern_structure,
                r"(\d+)[^\d]*[x*]\D*(\d+)",
                ["1_width", "2_height"],
                separator="x",
            ),
            Feature(
                MonitorSpecifications.ASPECT_RATIO,
                create_pattern_structure,
                r"(\d+):(\d+)",
                ["1_width", "2_height"],
                separator=":",
            ),
        ],
    ),
    FeatureGroup(
        "Helligkeit",
        [
            Feature(
                MonitorSpecifications.BRIGHTNESS,
                create_pattern_structure,
                r"(\d+)\D*(cd\/m\u00b2)",
                ["1_value", "z_unit"],
            ),
        ],
    ),
    FeatureGroup(
        "Kontrast",
        [
            Feature(
                MonitorSpecifications.CONTRAST,
                create_pattern_structure,
                r"(\d+)\s?:\s?(\d+)",
                ["1_dividend", "2_divisor"],
                separator=":",
            ),
        ],
    ),
    FeatureGroup(
        "Reaktionszeit",
        [
            Feature(
                MonitorSpecifications.REACTION_TIME,
                create_pattern_structure,
                r"(\d+.?\d*)\s*\(?\S*\)?\s*(ms)",  # 0,5 (MPRT) ms
                ["1_value", "z_unit"],
            ),
        ],
    ),
    FeatureGroup(
        "Blickwinkel",
        [
            Feature(
                MonitorSpecifications.VIEWING_ANGLE_HOR,
                create_pattern_structure,
                r"(\d+)",  # r"(\d+)\s?(\\u00b0)",
                ["1_value"],
            ),
            Feature(
                MonitorSpecifications.VIEWING_ANGLE_VER,
                create_pattern_structure,
                r"(\d+)",  # r"(\d+)\s?(\\u00b0)",
                ["1_value"],
            ),
        ],
    ),
    FeatureGroup(
        "Panel",
        [
            Feature(
                MonitorSpecifications.PANEL,
                apply_synonyms,
            ),
        ],
    ),
    FeatureGroup(
        "Form",
        [
            Feature(
                MonitorSpecifications.FORM,
                apply_synonyms,
            ),
            Feature(
                MonitorSpecifications.CURVATURE,
                create_pattern_structure,
                r"(\d+)\s?[R]",
                ["1_value"],
                separator="",
            ),
        ],
    ),
    FeatureGroup(
        "Beschichtung",
        [
            Feature(
                MonitorSpecifications.COATING,
                apply_synonyms,
            ),
        ],
    ),
    FeatureGroup(
        "HDR",
        [
            Feature(
                MonitorSpecifications.HDR,
                create_pattern_structure,
                r"(HDR)\W*(\d+)",  # HDR 400
                ["1_name", "2_value"],
            ),
        ],
    ),
    FeatureGroup(
        "Farbtiefe",
        [
            Feature(
                MonitorSpecifications.COLOR_DEPTH,
                create_pattern_structure,
                r"(\d+)\s*(\D*[bB]it)",
                ["1_value", "z_unit"],
            )
        ],
    ),
    FeatureGroup(
        "Farbraum",
        [
            Feature(
                MonitorSpecifications.COLOR_SPACE_SRGB,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(sRGB)\)?",
                ["1_value", "2_unit", "z_name"],
                separator=["", " "],
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_ARGB,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(Adobe RGB)\)?",
                ["1_value", "2_unit", "z_name"],
                separator=["", " "],
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_DCIP3,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(DCI-P3)\)?",
                ["1_value", "2_unit", "z_name"],
                separator=["", " "],
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_REC709,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(R.. 709)\)?",
                ["1_value", "2_unit", "z_name"],
                separator=["", " "],
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_REC2020,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(R.. 2020)\)",
                ["1_value", "2_unit", "z_name"],
                separator=["", " "],
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_NTSC,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(NTSC)\)?",
                ["1_value", "2_unit", "z_name"],
                separator=["", " "],
            ),
        ],
    ),
    FeatureGroup(
        "Bildwiederholfrequenz",
        [
            Feature(
                MonitorSpecifications.REFRESH_RATE,
                create_pattern_structure,
                r"(\d+)\s?(Hz)",
                ["1_value", "z_unit"],
            ),
        ],
    ),
    FeatureGroup(
        "Variable Synchronisierung",
        [
            Feature(
                MonitorSpecifications.VARIABLE_SYNC,
                create_listing,
            ),
        ],
    ),
    FeatureGroup(
        "Anschlüsse",
        [
            Feature(
                MonitorSpecifications.PORTS_HDMI,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(HDMI)",
                ["1_count", "2_value"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.PORTS_DP,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(Display[P|p]ort)",
                ["1_count", "2_value"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.PORTS_MINI_DP,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(Mini Display[P|p]ort)",
                ["1_count", "2_value"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.PORTS_DVI,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(DVI)",
                ["1_count", "2_value"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.PORTS_VGA,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(VGA)",
                ["1_count", "2_value"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.PORTS_USB_A,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(USB-A)",
                ["1_count", "2_value"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.PORTS_USB_C,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(USB-C)",
                ["1_count", "2_value"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.PORTS_THUNDERBOLT,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(Thunderbolt)",
                ["1_count", "2_value"],
                separator="x ",
            ),
        ],
    ),
    FeatureGroup(
        "Anschlüsse Display Out",
        [
            Feature(
                MonitorSpecifications.PORTS_DISPLAY_OUT,
                create_pattern_structure,
                r"(\d+)\s?x\s?(DisplayPort-?Out).?(\d.\d)",
                ["1_count", "2_type", "3_version"],
                separator=["x ", ""],
            ),
        ],
    ),
    FeatureGroup(
        "Weitere Anschlüsse",
        [
            Feature(
                MonitorSpecifications.PORTS_LAN,
                create_pattern_structure,
                r"(\d+)\s?x\s?(\w+\s?LAN)",  # 1x Gb LAN (RJ-45)
                ["1_count", "2_type"],
                separator="x ",
            ),
        ],
    ),
    FeatureGroup(
        "Audio",
        [
            Feature(
                MonitorSpecifications.PORTS_AUDIO,
                create_pattern_structure,
                r"(\d+)\s?x\s?(Line.Out)",
                ["1_count", "2_type"],
                separator="x ",
            ),
        ],
    ),
    FeatureGroup(
        "USB-Hub In",
        [
            Feature(
                MonitorSpecifications.USB_HUB_IN_USBC,
                create_pattern_structure,
                r"(\d+)\s?x\s?(USB Typ.C|USB.C)",  # e.g. 1x USB Typ C, 2x USB-C
                ["1_count", "2_type"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.USB_HUB_IN_USBB,
                create_pattern_structure,
                r"(\d+)\s?x\s?(USB-B) (\d.\d)",
                ["1_count", "2_type", "3_version"],
                separator=["x ", " "],
            ),
        ],
    ),
    FeatureGroup(
        "USB-Hub Out",
        [
            Feature(
                MonitorSpecifications.USB_HUB_OUT,
                create_pattern_structure,
                r"(\d+)\s?x\s?(USB-?.?).?(\d.\d)",
                ["1_count", "2_type", "3_version"],
                separator=["x ", " "],
            ),
        ],
    ),
    FeatureGroup(
        "Ergonomie",
        [
            Feature(
                MonitorSpecifications.ERGONOMICS_HEIGHT_ADJUSTABLE,
                create_pattern_structure,
                r"(\d+[[.|,]?\d]*)\s?(mm|cm)",
                ["1_value", "2_unit"],
            ),
            Feature(
                MonitorSpecifications.ERGONOMICS_PIVOT_ANGLE,
                create_pattern_structure,
                r"([+|-]?\d+)\s?-\s?([+|-]?\d+)",
                ["1_value", "2_value"],
                separator="/",
            ),
            Feature(
                MonitorSpecifications.ERGONOMICS_TILT_ANGLE,
                create_pattern_structure,
                r"([+|-]?\d+)\s?[-|\/]\s?([+|-]?\d+)",
                ["1_value", "2_value"],
                separator="/",
            ),
        ],
    ),
    FeatureGroup(
        "Farbe",
        [
            Feature(
                MonitorSpecifications.COLOR,
                create_listing,
            ),
        ],
    ),
    FeatureGroup(
        "Gewicht",
        [
            Feature(
                MonitorSpecifications.WEIGHT,
                create_pattern_structure,
                r"(\d+.?\d*)\s?(kg|g)",
                ["1_value", "z_unit"],
            ),
        ],
    ),
    FeatureGroup(
        "VESA",
        [
            Feature(
                MonitorSpecifications.VESA,
                create_pattern_structure,
                r"(\d+)\s?x\s?(\d+)",
                ["1_value", "2_value"],
                separator=" x ",
            ),
        ],
    ),
    FeatureGroup(
        "Energieeffizienzklasse",
        [
            Feature(
                name=MonitorSpecifications.ENERGY_EFFICIENCY,
                formatter=create_pattern_structure,
                pattern=r"[A-G][+]*",
            ),
        ],
    ),
    FeatureGroup(
        "Leistungsaufnahme (SDR)",
        [
            Feature(
                MonitorSpecifications.POWER_CONSUMPTION_SDR,
                create_pattern_structure,
                r"(\d+[.|,]?\d*)\s?(mW|W)",
                ["1_value", "2_unit"],
            ),
        ],
    ),
    FeatureGroup(
        "Leistungsaufnahme (Sleep)",
        [
            Feature(
                MonitorSpecifications.POWER_CONSUMPTION_SLEEP,
                create_pattern_structure,
                r"(\d+[.|,]?\d*)\s?(mW|W)",
                ["1_value", "2_unit"],
            ),
        ],
    ),
    FeatureGroup(
        "Stromversorgung",
        [
            Feature(
                MonitorSpecifications.POWER_SUPPLY,
                apply_synonyms,
            ),
        ],
    ),
    FeatureGroup(
        "Abmessungen",
        [
            Feature(
                MonitorSpecifications.DIMENSIONS,
                create_pattern_structure,
                r"(\d+.?[\d]*)\D*x\D*(\d+.?[\d]*)\D*x\D*(\d+.?[\d]*)\D*(mm|cm)",
                ["1_width", "2_height", "3_depth", "z_unit"],
                separator=[" x ", " x ", " "],
            ),
        ],
    ),
    FeatureGroup(
        "Rahmen",
        [
            Feature(
                MonitorSpecifications.BEZEL_BOTTOM,
                create_pattern_structure,
                r"(\d+.?[\d]*)\D*(mm|cm)",
                ["1_width", "z_unit"],
            ),
            Feature(
                MonitorSpecifications.BEZEL_SIDE,
                create_pattern_structure,
                r"(\d+.?[\d]*)\D*(mm|cm)",
                ["1_width", "z_unit"],
            ),
            Feature(
                MonitorSpecifications.BEZEL_TOP,
                create_pattern_structure,
                r"(\d+.?[\d]*)\D*(mm|cm)",
                ["1_width", "z_unit"],
            ),
        ],
    ),
    FeatureGroup(
        "Besonderheiten",
        [
            Feature(
                MonitorSpecifications.FEATURES,
                create_listing,
            ),
        ],
    ),
    FeatureGroup(
        "Kabel im Lieferumfang",
        [
            Feature(
                MonitorSpecifications.CABLES_HDMI,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(HDMI-Kabel)",
                ["1_count", "2_name"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.CABLES_DP,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(DisplayPort-Kabel)",
                ["1_count", "2_name"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.CABLES_DVI,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(DVI-Kabel)",
                ["1_count", "2_name"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.CABLES_VGA,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(VGA-Kabel)",
                ["1_count", "2_name"],
                separator="x ",
            ),
            Feature(
                MonitorSpecifications.CABLES_AC_POWER,
                create_pattern_structure,
                r"(\d+)\s?x?\s?([Strom|Netz|AC]+[-]*[K|]abel)",
                ["1_count", "2_name"],
                separator="x ",
            ),
        ],
    ),
    FeatureGroup(
        "Herstellergarantie",
        [
            Feature(
                MonitorSpecifications.WARRANTY,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(Jahr|Monate)",
                ["1_value", "2_unit"],
            ),
        ],
    ),
]


class MonitorParser(Parser):
    def __init__(self):
        specs: list[FeatureGroup[str, list[Feature]]] = monitor_spec
        super().__init__(specs)


monitor_parser = MonitorParser()
monitor_parser.init()
