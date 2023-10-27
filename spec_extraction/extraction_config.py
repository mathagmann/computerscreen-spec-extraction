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
    FeatureGroup("EAN", [Feature(MonitorSpecifications.EAN, create_pattern_structure, r"(\d{12}\d?)")]),
    FeatureGroup(
        "Diagonale",
        [
            Feature(
                MonitorSpecifications.DIAGONAL_INCH,
                create_pattern_structure,
                r"(\d+[.,]*\d*)\s*(\"|Zoll)",  # 27 "
                ["value", "unit"],
                string_repr="{value}{unit}",
            ),
            Feature(
                MonitorSpecifications.DIAGONAL_CM,
                create_pattern_structure,
                r"(\d+[.,]*\d*)\s*(mm|cm|m)",  # 68.6 cm
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
            ),
        ],
    ),
    FeatureGroup("Marke", [Feature(MonitorSpecifications.BRAND)]),
    FeatureGroup(
        "Auflösung",
        [
            Feature(
                MonitorSpecifications.RESOLUTION,
                create_pattern_structure,
                r"(\d+)[^\d]*[x*]\D*(\d+)",
                ["width", "height"],
                string_repr="{width}x{height}",
            ),
            Feature(
                MonitorSpecifications.ASPECT_RATIO,
                create_pattern_structure,
                r"(\d+):(\d+)",
                ["width", "height"],
                string_repr="{width}:{height}",
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
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
            )
        ],
    ),
    FeatureGroup(
        "Kontrast",
        [
            Feature(
                MonitorSpecifications.CONTRAST,
                create_pattern_structure,
                r"(\d+)\s?:\s?(\d+)",
                ["dividend", "divisor"],
                string_repr="{dividend}:{divisor}",
            )
        ],
    ),
    FeatureGroup(
        "Reaktionszeit",
        [
            Feature(
                MonitorSpecifications.REACTION_TIME,
                create_pattern_structure,
                r"(\d+.?\d*)\s*\(?\S*\)?\s*(ms)",  # 0,5 (MPRT) ms
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
            )
        ],
    ),
    FeatureGroup(
        "Blickwinkel",
        [
            Feature(
                MonitorSpecifications.VIEWING_ANGLE_HOR,
                create_pattern_structure,
                r"(\d+)",  # r"(\d+)\s?(\\u00b0)",
                ["value"],
            ),
            Feature(
                MonitorSpecifications.VIEWING_ANGLE_VER,
                create_pattern_structure,
                r"(\d+)",  # r"(\d+)\s?(\\u00b0)",
                ["value"],
            ),
        ],
    ),
    FeatureGroup("Panel", [Feature(MonitorSpecifications.PANEL, apply_synonyms)]),
    FeatureGroup(
        "Form",
        [
            Feature(MonitorSpecifications.FORM, apply_synonyms),
            Feature(MonitorSpecifications.CURVATURE, create_pattern_structure, r"(\d+)\s?[R]", ["value"]),
        ],
    ),
    FeatureGroup("Beschichtung", [Feature(MonitorSpecifications.COATING, apply_synonyms)]),
    FeatureGroup(
        "HDR",
        [
            Feature(
                MonitorSpecifications.HDR,
                create_pattern_structure,
                r"(HDR)\W*(\d+)",
                ["name", "value"],
                string_repr="{name}\u00a0{value}",
            )
        ],
        # HDR 400
    ),
    FeatureGroup(
        "Farbtiefe",
        [
            Feature(
                MonitorSpecifications.COLOR_DEPTH,
                create_pattern_structure,
                r"(\d+)\s*(\D*[bB]it)",
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
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
                ["value", "unit", "name"],
                string_repr="{value}{unit} {name}",
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_ARGB,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(Adobe RGB)\)?",
                ["value", "unit", "name"],
                string_repr="{value}{unit} {name}",
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_DCIP3,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(DCI-P3)\)?",
                ["value", "unit", "name"],
                string_repr="{value}{unit} {name}",
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_REC709,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(R.. 709)\)?",
                ["value", "unit", "name"],
                string_repr="{value}{unit} {name}",
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_REC2020,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(R.. 2020)\)",
                ["value", "unit", "name"],
                string_repr="{value}{unit} {name}",
            ),
            Feature(
                MonitorSpecifications.COLOR_SPACE_NTSC,
                create_pattern_structure,
                r"(\d+)\s?(%) \(?(NTSC)\)?",
                ["value", "unit", "name"],
                string_repr="{value}{unit} {name}",
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
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
            )
        ],
    ),
    FeatureGroup("Variable Synchronisierung", [Feature(MonitorSpecifications.VARIABLE_SYNC, create_listing)]),
    FeatureGroup(
        "Anschlüsse",
        [
            Feature(
                MonitorSpecifications.PORTS_HDMI,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(HDMI)",
                ["count", "value"],
                string_repr="{count}x {value}",
            ),
            Feature(
                MonitorSpecifications.PORTS_DP,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(Display[P|p]ort)",
                ["count", "value"],
                string_repr="{count}x {value}",
            ),
            Feature(
                MonitorSpecifications.PORTS_MINI_DP,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(Mini Display[P|p]ort)",
                ["count", "value"],
                string_repr="{count}x {value}",
            ),
            Feature(
                MonitorSpecifications.PORTS_DVI,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(DVI)",
                ["count", "value"],
                string_repr="{count}x {value}",
            ),
            Feature(
                MonitorSpecifications.PORTS_VGA,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(VGA)",
                ["count", "value"],
                string_repr="{count}x {value}",
            ),
            Feature(
                MonitorSpecifications.PORTS_USB_A,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(USB-A)",
                ["count", "value"],
                string_repr="{count}x {value}",
            ),
            Feature(
                MonitorSpecifications.PORTS_USB_C,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(USB-C)",
                ["count", "value"],
                string_repr="{count}x {value}",
            ),
            Feature(
                MonitorSpecifications.PORTS_THUNDERBOLT,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(Thunderbolt)",
                ["count", "value"],
                string_repr="{count}x {value}",
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
                ["count", "type", "version"],
                string_repr="{count}x {type}{version}",
            )
        ],
    ),
    FeatureGroup(
        "Weitere Anschlüsse",
        [
            Feature(
                MonitorSpecifications.PORTS_LAN,
                create_pattern_structure,
                r"(\d+)\s?x\s?(\w+\s?LAN)",  # 1x Gb LAN (RJ-45)
                ["count", "type"],
                string_repr="{count}x {type}",
            )
        ],
    ),
    FeatureGroup(
        "Audio",
        [
            Feature(
                MonitorSpecifications.PORTS_AUDIO,
                create_pattern_structure,
                r"(\d+)\s?x\s?(Line.Out)",
                ["count", "type"],
                string_repr="{count}x {type}",
            )
        ],
    ),
    FeatureGroup(
        "USB-Hub In",
        [
            Feature(
                MonitorSpecifications.USB_HUB_IN_USBC,
                create_pattern_structure,
                r"(\d+)\s?x\s?(USB Typ.C|USB.C)",  # e.g. 1x USB Typ C, 2x USB-C
                ["count", "type"],
                string_repr="{count}x {type}",
            ),
            Feature(
                MonitorSpecifications.USB_HUB_IN_USBB,
                create_pattern_structure,
                r"(\d+)\s?x\s?(USB-B) (\d.\d)",
                ["count", "type", "version"],
                string_repr="{count}x {type} {version}",
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
                ["count", "type", "version"],
                string_repr="{count}x {type} {version}",
            )
        ],
    ),
    FeatureGroup(
        "Ergonomie",
        [
            Feature(
                MonitorSpecifications.ERGONOMICS_HEIGHT_ADJUSTABLE,
                create_pattern_structure,
                r"(\d+[[.|,]?\d]*)\s?(mm|cm)",
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
            ),
            Feature(
                MonitorSpecifications.ERGONOMICS_PIVOT_ANGLE,
                create_pattern_structure,
                r"([+|-]?\d+)\s?-\s?([+|-]?\d+)",
                ["value1", "value2"],
                string_repr="{value1}/{value2}",
            ),
            Feature(
                MonitorSpecifications.ERGONOMICS_TILT_ANGLE,
                create_pattern_structure,
                r"([+|-]?\d+)\s?[-|\/]\s?([+|-]?\d+)",
                ["value1", "value2"],
                string_repr="{value1}/{value2}",
            ),
        ],
    ),
    FeatureGroup("Farbe", [Feature(MonitorSpecifications.COLOR, create_listing)]),
    FeatureGroup(
        "Gewicht",
        [
            Feature(
                MonitorSpecifications.WEIGHT,
                create_pattern_structure,
                r"(\d+.?\d*)\s?(kg|g)",
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
            )
        ],
    ),
    FeatureGroup(
        "VESA",
        [
            Feature(
                MonitorSpecifications.VESA,
                create_pattern_structure,
                r"(\d+)\s?x\s?(\d+)",
                ["width", "height"],
                string_repr="{width}x{height}",
            )
        ],
    ),
    FeatureGroup(
        "Energieeffizienzklasse",
        [
            Feature(
                name=MonitorSpecifications.ENERGY_EFFICIENCY, formatter=create_pattern_structure, pattern=r"[A-G][+]*"
            )
        ],
    ),
    FeatureGroup(
        "Leistungsaufnahme (SDR)",
        [
            Feature(
                MonitorSpecifications.POWER_CONSUMPTION_SDR,
                create_pattern_structure,
                r"(\d+[.|,]?\d*)\s?(mW|W)",
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
            )
        ],
    ),
    FeatureGroup(
        "Leistungsaufnahme (Sleep)",
        [
            Feature(
                MonitorSpecifications.POWER_CONSUMPTION_SLEEP,
                create_pattern_structure,
                r"(\d+[.|,]?\d*)\s?(mW|W)",
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
            )
        ],
    ),
    FeatureGroup("Stromversorgung", [Feature(MonitorSpecifications.POWER_SUPPLY, apply_synonyms)]),
    FeatureGroup(
        "Abmessungen",
        [
            Feature(
                MonitorSpecifications.DIMENSIONS,
                create_pattern_structure,
                r"(\d+\.?[\d]*)\D*x\D*(\d+\.?[\d]*)\D*x\D*(\d+\.?[\d]*)\D*(mm|cm)",
                ["width", "height", "depth", "unit"],
                string_repr="{width}x{height}x{depth}\u00a0{unit}",
            )
        ],
    ),
    FeatureGroup(
        "Rahmen",
        [
            Feature(
                MonitorSpecifications.BEZEL_BOTTOM,
                create_pattern_structure,
                r"(\d+\.?[\d]*)\D*(mm|cm)",
                ["width", "unit"],
                string_repr="{width}\u00a0{unit}",
            ),
            Feature(
                MonitorSpecifications.BEZEL_SIDE,
                create_pattern_structure,
                r"(\d+\.?[\d]*)\D*(mm|cm)",
                ["width", "unit"],
                string_repr="{width}\u00a0{unit}",
            ),
            Feature(
                MonitorSpecifications.BEZEL_TOP,
                create_pattern_structure,
                r"(\d+\.?[\d]*)\D*(mm|cm)",
                ["width", "unit"],
                string_repr="{width}\u00a0{unit}",
            ),
        ],
    ),
    FeatureGroup("Besonderheiten", [Feature(MonitorSpecifications.FEATURES, create_listing)]),
    FeatureGroup(
        "Kabel im Lieferumfang",
        [
            Feature(
                MonitorSpecifications.CABLES_HDMI,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(HDMI-Kabel)",
                ["count", "name"],
                string_repr="{count}x {name}",
            ),
            Feature(
                MonitorSpecifications.CABLES_DP,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(DisplayPort-Kabel)",
                ["count", "name"],
                string_repr="{count}x {name}",
            ),
            Feature(
                MonitorSpecifications.CABLES_DVI,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(DVI-Kabel)",
                ["count", "name"],
                string_repr="{count}x {name}",
            ),
            Feature(
                MonitorSpecifications.CABLES_VGA,
                create_pattern_structure,
                r"(\d+)\s?x?\s?(VGA-Kabel)",
                ["count", "name"],
                string_repr="{count}x {name}",
            ),
            Feature(
                MonitorSpecifications.CABLES_AC_POWER,
                create_pattern_structure,
                r"(\d+)\s?x?\s?([Strom|Netz|AC]+[-]*[K|]abel)",
                ["count", "name"],
                string_repr="{count}x {name}",
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
                ["value", "unit"],
                string_repr="{value}\u00a0{unit}",
            )
        ],
    ),
]


class MonitorParser(Parser):
    def __init__(self):
        specs: list[FeatureGroup[str, list[Feature]]] = monitor_spec
        super().__init__(specs)


monitor_parser = MonitorParser()
monitor_parser.init()
