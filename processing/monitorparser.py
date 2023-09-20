from enum import Enum

from processing.extraction import DataExtractor
from processing.extraction import Feature
from processing.extraction import FeatureGroup
from processing.extraction import Parser


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class MonitorSpecifications(ExtendedEnum):
    EAN = "EAN"
    DIAGONAL_INCH = "Bilddiagonale (Zoll)"
    DIAGONAL_CM = "Bilddiagonale (cm)"
    BRAND = "Marke"
    RESOLUTION = "Auflösung"
    BRIGHTNESS = "Helligkeit"
    CONTRAST = "Kontrast"
    REACTION_TIME = "Reaktionszeit"
    VIEWING_ANGLE_HOR = "Blickwinkel horizontal"
    VIEWING_ANGLE_VER = "Blickwinkel vertikal"
    PANEL = "Panel"
    FORM = "Form"
    CURVATURE = "Krümmung"
    COATING = "Beschichtung"
    HDR = "HDR"
    ASPECT_RATIO = "Seitenverhältnis"
    COLOR_DEPTH = "Farbtiefe"
    COLOR_SPACE_SRGB = "Farbraum sRGB"
    COLOR_SPACE_DCIP3 = "Farbraum DCI-P3"
    COLOR_SPACE_ARGB = "Farbraum Adobe RGB"
    COLOR_SPACE_REC709 = "Farbraum REC 709"
    COLOR_SPACE_REC2020 = "Farbraum REC 2020"
    COLOR_SPACE_NTSC = "Farbraum NTSC"
    REFRESH_RATE = "Bildwiederholfrequenz"
    VARIABLE_SYNC = "Variable Synchronisierung"
    PORTS_HDMI = "Anschlüsse HDMI"
    PORTS_DP = "Anschlüsse DisplayPort"
    PORTS_MINI_DP = "Anschlüsse Mini DisplayPort"
    PORTS_DVI = "Anschlüsse DVI"
    PORTS_VGA = "Anschlüsse VGA"
    PORTS_DISPLAY_OUT = "Ausgänge Display"
    PORTS_USB_C = "Anschlüsse USB-C"
    PORTS_USB_A = "Anschlüsse USB-A"
    PORTS_THUNDERBOLT = "Thunderbolt"
    PORTS_AUDIO = "Anschlüsse Klinke"
    PORTS_LAN = "Anschlüsse LAN"
    USB_HUB_OUT = "USB-Hub Ausgang"
    USB_HUB_IN_USBC = "USB-Hub Eingänge USB-C"
    USB_HUB_IN_USBB = "USB-Hub Eingänge USB-B"
    ERGONOMICS_HEIGHT_ADJUSTABLE = "Höhenverstellbar"
    ERGONOMICS_TILT_ANGLE = "Neigungswinkelbereich"
    ERGONOMICS_PIVOT_ANGLE = "Schwenkwinkelbereich"
    COLOR = "Farbe"
    VESA = "VESA"
    POWER_CONSUMPTION_SDR = "Leistungsaufnahme (SDR)"
    POWER_CONSUMPTION_SLEEP = "Leistungsaufnahme (Sleep)"
    POWER_SUPPLY = "Stromversorgung"
    ENERGY_EFFICIENCY = "Energieeffizienzklasse"
    WEIGHT = "Gewicht"
    DIMENSIONS = "Abmessungen"
    BEZEL_TOP = "Rahmenstärke oben"
    BEZEL_SIDE = "Rahmenstärke seitlich"
    BEZEL_BOTTOM = "Rahmenstärke unten"
    FEATURES = "Besonderheiten"
    CABLES_HDMI = "Kabel HDMI"
    CABLES_DP = "Kabel DisplayPort"
    CABLES_DVI = "Kabel DVI"
    CABLES_VGA = "Kabel VGA"
    CABLES_AC_POWER = "Kabel Strom"
    WARRANTY = "Herstellergarantie"


class MonitorParser(Parser):
    def __init__(self):
        monitor_spec = [
            FeatureGroup(
                "EAN",
                [
                    Feature(
                        MonitorSpecifications.EAN.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d{12}\d?)",
                    ),
                ],
            ),
            FeatureGroup(
                "Diagonale",
                [
                    Feature(
                        MonitorSpecifications.DIAGONAL_INCH.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+[.,]*\d*)\s*(\"|Zoll)",  # 27 "
                        ["1_value", "z_unit"],
                        separator="",
                    ),
                    Feature(
                        MonitorSpecifications.DIAGONAL_CM.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+[.,]*\d*)\s*(mm|cm|m)",  # 68.6 cm
                        ["1_value", "z_unit"],
                    ),
                ],
            ),
            FeatureGroup(
                "Marke",
                [
                    Feature(MonitorSpecifications.BRAND.value),
                ],
            ),
            FeatureGroup(
                "Auflösung",
                [
                    Feature(
                        MonitorSpecifications.RESOLUTION.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)[^\d]*[x*]\D*(\d+)",
                        ["1_width", "2_height"],
                        separator="x",
                    ),
                    Feature(
                        MonitorSpecifications.ASPECT_RATIO.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.BRIGHTNESS.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\D*(cd\/m\u00b2)",
                        ["1_value", "z_unit"],
                    ),
                ],
            ),
            FeatureGroup(
                "Kontrast",
                [
                    Feature(
                        MonitorSpecifications.CONTRAST.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.REACTION_TIME.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+.?\d*)\s*\(?\S*\)?\s*(ms)",  # 0,5 (MPRT) ms
                        ["1_value", "z_unit"],
                    ),
                ],
            ),
            FeatureGroup(
                "Blickwinkel",
                [
                    Feature(
                        MonitorSpecifications.VIEWING_ANGLE_HOR.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)",  # r"(\d+)\s?(\\u00b0)",
                        ["1_value"],
                    ),
                    Feature(
                        MonitorSpecifications.VIEWING_ANGLE_VER.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)",  # r"(\d+)\s?(\\u00b0)",
                        ["1_value"],
                    ),
                ],
            ),
            FeatureGroup(
                "Panel",
                [
                    Feature(
                        MonitorSpecifications.PANEL.value,
                        DataExtractor.apply_synonyms,
                    ),
                ],
            ),
            FeatureGroup(
                "Form",
                [
                    Feature(
                        MonitorSpecifications.FORM.value,
                        DataExtractor.apply_synonyms,
                    ),
                    Feature(
                        MonitorSpecifications.CURVATURE.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.COATING.value,
                        DataExtractor.apply_synonyms,
                    ),
                ],
            ),
            FeatureGroup(
                "HDR",
                [
                    Feature(
                        MonitorSpecifications.HDR.value,
                        DataExtractor.create_pattern_structure,
                        r"(HDR)\W*(\d+)",  # HDR 400
                        ["1_name", "2_value"],
                    ),
                ],
            ),
            FeatureGroup(
                "Farbtiefe",
                [
                    Feature(
                        MonitorSpecifications.COLOR_DEPTH.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s*(\D*[bB]it)",
                        ["1_value", "z_unit"],
                    )
                ],
            ),
            FeatureGroup(
                "Farbraum",
                [
                    Feature(
                        MonitorSpecifications.COLOR_SPACE_SRGB.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?(%) \(?(sRGB)\)?",
                        ["1_value", "2_unit", "z_name"],
                        separator=["", " "],
                    ),
                    Feature(
                        MonitorSpecifications.COLOR_SPACE_ARGB.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?(%) \(?(Adobe RGB)\)?",
                        ["1_value", "2_unit", "z_name"],
                        separator=["", " "],
                    ),
                    Feature(
                        MonitorSpecifications.COLOR_SPACE_DCIP3.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?(%) \(?(DCI-P3)\)?",
                        ["1_value", "2_unit", "z_name"],
                        separator=["", " "],
                    ),
                    Feature(
                        MonitorSpecifications.COLOR_SPACE_REC709.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?(%) \(?(R.. 709)\)?",
                        ["1_value", "2_unit", "z_name"],
                        separator=["", " "],
                    ),
                    Feature(
                        MonitorSpecifications.COLOR_SPACE_REC2020.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?(%) \(?(R.. 2020)\)",
                        ["1_value", "2_unit", "z_name"],
                        separator=["", " "],
                    ),
                    Feature(
                        MonitorSpecifications.COLOR_SPACE_NTSC.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.REFRESH_RATE.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?(Hz)",
                        ["1_value", "z_unit"],
                    ),
                ],
            ),
            FeatureGroup(
                "Variable Synchronisierung",
                [
                    Feature(
                        MonitorSpecifications.VARIABLE_SYNC.value,
                        DataExtractor.create_listing,
                    ),
                ],
            ),
            FeatureGroup(
                "Anschlüsse",
                [
                    Feature(
                        MonitorSpecifications.PORTS_HDMI.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(HDMI)",
                        ["1_count", "2_value"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.PORTS_DP.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(Display[P|p]ort)",
                        ["1_count", "2_value"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.PORTS_MINI_DP.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(Mini Display[P|p]ort)",
                        ["1_count", "2_value"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.PORTS_DVI.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(DVI)",
                        ["1_count", "2_value"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.PORTS_VGA.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(VGA)",
                        ["1_count", "2_value"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.PORTS_USB_A.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(USB-A)",
                        ["1_count", "2_value"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.PORTS_USB_C.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(USB-C)",
                        ["1_count", "2_value"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.PORTS_THUNDERBOLT.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.PORTS_DISPLAY_OUT.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.PORTS_LAN.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.PORTS_AUDIO.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.USB_HUB_IN_USBC.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x\s?(USB Typ.C|USB.C)",  # e.g. 1x USB Typ C, 2x USB-C
                        ["1_count", "2_type"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.USB_HUB_IN_USBB.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.USB_HUB_OUT.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.ERGONOMICS_HEIGHT_ADJUSTABLE.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+[[.|,]?\d]*)\s?(mm|cm)",
                        ["1_value", "2_unit"],
                    ),
                    Feature(
                        MonitorSpecifications.ERGONOMICS_PIVOT_ANGLE.value,
                        DataExtractor.create_pattern_structure,
                        r"([+|-]?\d+)\s?-\s?([+|-]?\d+)",
                        ["1_value", "2_value"],
                        separator="/",
                    ),
                    Feature(
                        MonitorSpecifications.ERGONOMICS_TILT_ANGLE.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.COLOR.value,
                        DataExtractor.create_listing,
                    ),
                ],
            ),
            FeatureGroup(
                "Gewicht",
                [
                    Feature(
                        MonitorSpecifications.WEIGHT.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+.?\d*)\s?(kg|g)",
                        ["1_value", "z_unit"],
                    ),
                ],
            ),
            FeatureGroup(
                "VESA",
                [
                    Feature(
                        MonitorSpecifications.VESA.value,
                        DataExtractor.create_pattern_structure,
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
                        name=MonitorSpecifications.ENERGY_EFFICIENCY.value,
                        formatter=DataExtractor.create_pattern_structure,
                        pattern=r"[A-G][+]*",
                    ),
                ],
            ),
            FeatureGroup(
                "Leistungsaufnahme (SDR)",
                [
                    Feature(
                        MonitorSpecifications.POWER_CONSUMPTION_SDR.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+[.|,]?\d*)\s?(mW|W)",
                        ["1_value", "2_unit"],
                    ),
                ],
            ),
            FeatureGroup(
                "Leistungsaufnahme (Sleep)",
                [
                    Feature(
                        MonitorSpecifications.POWER_CONSUMPTION_SLEEP.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+[.|,]?\d*)\s?(mW|W)",
                        ["1_value", "2_unit"],
                    ),
                ],
            ),
            FeatureGroup(
                "Stromversorgung",
                [
                    Feature(
                        MonitorSpecifications.POWER_SUPPLY.value,
                        DataExtractor.apply_synonyms,
                    ),
                ],
            ),
            FeatureGroup(
                "Abmessungen",
                [
                    Feature(
                        MonitorSpecifications.DIMENSIONS.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.BEZEL_BOTTOM.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+.?[\d]*)\D*(mm|cm)",
                        ["1_width", "z_unit"],
                    ),
                    Feature(
                        MonitorSpecifications.BEZEL_SIDE.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+.?[\d]*)\D*(mm|cm)",
                        ["1_width", "z_unit"],
                    ),
                    Feature(
                        MonitorSpecifications.BEZEL_TOP.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+.?[\d]*)\D*(mm|cm)",
                        ["1_width", "z_unit"],
                    ),
                ],
            ),
            FeatureGroup(
                "Besonderheiten",
                [
                    Feature(
                        MonitorSpecifications.FEATURES.value,
                        DataExtractor.create_listing,
                    ),
                ],
            ),
            FeatureGroup(
                "Kabel im Lieferumfang",
                [
                    Feature(
                        MonitorSpecifications.CABLES_HDMI.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(HDMI-Kabel)",
                        ["1_count", "2_name"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.CABLES_DP.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(DisplayPort-Kabel)",
                        ["1_count", "2_name"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.CABLES_DVI.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(DVI-Kabel)",
                        ["1_count", "2_name"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.CABLES_VGA.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(VGA-Kabel)",
                        ["1_count", "2_name"],
                        separator="x ",
                    ),
                    Feature(
                        MonitorSpecifications.CABLES_AC_POWER.value,
                        DataExtractor.create_pattern_structure,
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
                        MonitorSpecifications.WARRANTY.value,
                        DataExtractor.create_pattern_structure,
                        r"(\d+)\s?x?\s?(Jahr|Monate)",
                        ["1_value", "2_unit"],
                    ),
                ],
            ),
        ]
        super().__init__(monitor_spec)
