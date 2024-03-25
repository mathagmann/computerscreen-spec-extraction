import pytest

from spec_extraction.catalog_model import CATALOG_EXAMPLE
from spec_extraction.catalog_model import MonitorSpecifications
from spec_extraction.process import classify_specifications_with_ml
from spec_extraction.process import convert_machine_learning_labels_to_structured_data
from spec_extraction.process import value_fusion
from token_classification import bootstrap as ml_bootstrap


def test_catalog_values_exist():
    min_expected_values = len(MonitorSpecifications.list()) * 0.95

    example_values = 0
    for feature in MonitorSpecifications.list():
        if feature in CATALOG_EXAMPLE:
            example_values += 1

    assert min_expected_values <= example_values


@pytest.mark.skip(reason="Requires equally trained model each time")
def test_classify_specifications():
    expected = {"count-hdmi": "1", "type-hdmi": "HDMI"}
    test_data = {
        "Anschlüsse - DisplayPort 1.2 (75Hz@1920x1080)": "1",
        "Anschlüsse - HDMI Version 1.4 (75Hz@1920x1080)": "1",
        "Anschlüsse - VGA (60Hz@1920x1080)": "1",
        "Anwendung": "stationär",
    }

    token_labeling = ml_bootstrap.bootstrap()
    result = classify_specifications_with_ml(test_data, token_labeling)

    assert result == expected


@pytest.mark.parametrize(
    "labeled_data,expected",
    [
        (
            {"count-hdmi": "1", "type-hdmi": "HDMI"},
            {MonitorSpecifications.PORTS_HDMI.value: {"value": "HDMI", "count": "1"}},
        ),
        (
            {"count-displayport": "1", "type-displayport": "DisplayPort", "version-displayport": "1.2"},
            {MonitorSpecifications.PORTS_DP.value: {"value": "DisplayPort", "count": "1", "version": "1.2"}},
        ),
        (
            {
                "count-displayport": "1",
                "type-displayport": "DisplayPort",
                "version-displayport": "1.2",
                "type-hdmi": "HDMI",
            },
            {
                MonitorSpecifications.PORTS_DP.value: {"value": "DisplayPort", "count": "1", "version": "1.2"},
                MonitorSpecifications.PORTS_HDMI.value: {"count": "1", "value": "HDMI"},
            },
        ),
    ],
)
def test_convert_machine_learning_labels_to_structured_data(labeled_data, expected):
    assert convert_machine_learning_labels_to_structured_data(labeled_data) == expected


def test_value_fusion():
    shop_data = {
        "playox (AT)": {},
        "1ashop.at": {},
        "e-tec.at": {
            "Auflösung": {"width": "1920", "height": "1080"},
            "Helligkeit": {"value": "250", "unit": "cd/m²"},
            "Kontrast": {"dividend": "1.000", "divisor": "1"},
            "Reaktionszeit": {"value": "5", "unit": "ms"},
            "Panel": "IPS",
            "Form": "gerade",
            "Beschichtung": "matt (non-glare),  Härtegrad 3H",
            "Seitenverhältnis": {"width": "16", "height": "9"},
            "Farbtiefe": {"value": "8", "unit": "bit"},
            "Bildwiederholfrequenz": {"value": "75", "unit": "Hz"},
            "Anschlüsse Klinke": {"count": "1", "type": "Line-Out"},
            "Farbe": ["schwarz"],
            "VESA": {"width": "100", "height": "100"},
            "Leistungsaufnahme (SDR)": {"value": "22", "unit": "W"},
            "Leistungsaufnahme (Sleep)": {"value": "22", "unit": "W"},
            "Stromversorgung": "AC-In (internes Netzteil)",
            "Gewicht": {"value": "4.30", "unit": "kg"},
            "Besonderheiten": ["Slim Bezel", "EPEAT Bronze", "mechanische Tasten", "Sicherheitsschloss (Kensington)"],
            "Anschlüsse HDMI": {"value": "HDMI", "count": "1", "version": "1.4              80"},
        },
        "CSV-Direct.de": {
            "Höhenverstellbar": {"value": "13", "unit": "cm"},
            "Neigungswinkelbereich": {"value1": "-5", "value2": "35"},
            "Energieeffizienzklasse": "F",
            "Anschlüsse HDMI": {
                "value": "HDMI    0",
                "count": "1",
                "version": "1.4",
            },
        },
        "DiTech.at": {
            "Auflösung": {"width": "1920", "height": "1080"},
            "Helligkeit": {"value": "250", "unit": "cd/m²"},
            "Kontrast": {"dividend": "1.000", "divisor": "1"},
            "Reaktionszeit": {"value": "5", "unit": "ms"},
            "Panel": "IPS",
            "Form": "gerade",
            "Beschichtung": "matt (non-glare),  Härtegrad 3H",
            "Seitenverhältnis": {"width": "16", "height": "9"},
            "Farbtiefe": {"value": "8", "unit": "bit"},
            "Bildwiederholfrequenz": {"value": "75", "unit": "Hz"},
            "Anschlüsse Klinke": {"count": "1", "type": "Line-Out"},
            "Farbe": ["schwarz"],
            "VESA": {"width": "100", "height": "100"},
            "Leistungsaufnahme (SDR)": {"value": "22", "unit": "W"},
            "Leistungsaufnahme (Sleep)": {"value": "22", "unit": "W"},
            "Stromversorgung": "AC-In (internes Netzteil)",
            "Gewicht": {"value": "4.30", "unit": "kg"},
            "Besonderheiten": ["Slim Bezel", "EPEAT Bronze", "mechanische Tasten", "Sicherheitsschloss (Kensington)"],
            "Anschlüsse HDMI": {"value": "HDMI", "count": "1", "version": "1.4              80"},
        },
        "Amazon.at": {
            "Marke": "\u200eLG Electronics",
            "Auflösung": {"width": "1920", "height": "1080"},
            "Panel": "\u200e24BP450Y-B",
            "Variable Synchronisierung": ["\u200e24BP450Y-B"],
            "Höhenverstellbar": {"value": "10,8", "unit": "cm"},
            "Farbe": ["\u200eSchwarz"],
            "VESA": {"width": "1920", "height": "1080"},
        },
        "office-partner (AT)": {},
        "HEINZSOFT (AT)": {},
        "ElectronicShop24": {
            "Helligkeit": {"value": "250", "unit": "cd/m²"},
            "Kontrast": {"dividend": "1000", "divisor": "1"},
            "Reaktionszeit": {"value": "5", "unit": "ms"},
            "Blickwinkel horizontal": {"value": "178"},
            "Blickwinkel vertikal": {"value": "178"},
            "Panel": "IPS",
            "Beschichtung": "matt",
            "Seitenverhältnis": {"width": "16", "height": "9"},
            "Farbraum NTSC": {"value": "72", "unit": "%", "name": "NTSC"},
            "Neigungswinkelbereich": {"value1": "-5", "value2": "+35"},
            "Farbe": ["Schwarz"],
            "Besonderheiten": [
                "SUPER + Resolution",
                "Multiscan Support",
                "integrierte Kabelführung",
                "Reihenschaltung möglich",
                "Crosshair Display",
                "Flicker Safe",
                "Reader Mode",
                "6-Achsen-Farbanpassung",
                "Intelligente Energiespartechnologie",
                "Black Stabilizer",
                "DAS Mode (Dynamic Action Sync)",
                "Color Weakness Mode",
                "Mega DFC",
                "One Click Stand",
                "nahezu rahmenloses Display an 3 Seiten",
            ],
            "Kabel HDMI": {"count": "1", "name": "HDMI-Kabel"},
            "Anschlüsse HDMI": {"count": "1"},
        },
        "Future-X.at": {
            "Helligkeit": {"value": "250", "unit": "cd/m²"},
            "Kontrast": {"dividend": "1000", "divisor": "1"},
            "Reaktionszeit": {"value": "5", "unit": "ms"},
            "Blickwinkel horizontal": {"value": "178"},
            "Blickwinkel vertikal": {"value": "178"},
            "Panel": "IPS",
            "Beschichtung": "SUPER + Resolution, Multiscan Support, integrierte Kabelführung, Reihenschaltung "
            "möglich, Crosshair Display, Flicker Safe, Reader Mode, 6-Achsen-Farbanpassung, "
            "Intelligente Energiespartechnologie, Black Stabilizer, DAS Mode (Dynamic Action Sync), "
            "Color Weakness Mode, Mega DFC, One Click Stand, nahezu rahmenloses Display an 3 Seiten",
            "Seitenverhältnis": {"width": "16", "height": "9"},
            "Farbraum NTSC": {"value": "72", "unit": "%", "name": "NTSC"},
            "Höhenverstellbar": {"value": "130", "unit": "mm"},
            "Farbe": ["Schwarz"],
            "Besonderheiten": [
                "SUPER + Resolution",
                "Multiscan Support",
                "integrierte Kabelführung",
                "Reihenschaltung möglich",
                "Crosshair Display",
                "Flicker Safe",
                "Reader Mode",
                "6-Achsen-Farbanpassung",
                "Intelligente Energiespartechnologie",
                "Black Stabilizer",
                "DAS Mode (Dynamic Action Sync)",
                "Color Weakness Mode",
                "Mega DFC",
                "One Click Stand",
                "nahezu rahmenloses Display an 3 Seiten",
            ],
            "Kabel HDMI": {"count": "1", "name": "HDMI-Kabel"},
            "Anschlüsse HDMI": {"count": "1"},
        },
        "HiQ24": {
            "Helligkeit": {"value": "250", "unit": "cd/m²"},
            "Kontrast": {"dividend": "1000", "divisor": "1"},
            "Reaktionszeit": {"value": "5", "unit": "ms"},
            "Blickwinkel horizontal": {"value": "178"},
            "Blickwinkel vertikal": {"value": "178"},
            "Panel": "IPS",
            "Beschichtung": "SUPER + Resolution, Multiscan Support, integrierte Kabelführung, Reihenschaltung "
            "möglich, Crosshair Display, Flicker Safe, Reader Mode, 6-Achsen-Farbanpassung, "
            "Intelligente Energiespartechnologie, Black Stabilizer, DAS Mode (Dynamic Action Sync), "
            "Color Weakness Mode, Mega DFC, One Click Stand, nahezu rahmenloses Display an 3 Seiten",
            "Seitenverhältnis": {"width": "16", "height": "9"},
            "Farbraum NTSC": {"value": "72", "unit": "%", "name": "NTSC"},
            "Neigungswinkelbereich": {"value1": "-5", "value2": "+35"},
            "Farbe": ["Schwarz"],
            "Energieeffizienzklasse": "F",
            "Besonderheiten": [
                "SUPER + Resolution",
                "Multiscan Support",
                "integrierte Kabelführung",
                "Reihenschaltung möglich",
                "Crosshair Display",
                "Flicker Safe",
                "Reader Mode",
                "6-Achsen-Farbanpassung",
                "Intelligente Energiespartechnologie",
                "Black Stabilizer",
                "DAS Mode (Dynamic Action Sync)",
                "Color Weakness Mode",
                "Mega DFC",
                "One Click Stand",
                "nahezu rahmenloses Display an 3 Seiten",
            ],
            "Kabel HDMI": {"count": "1", "name": "HDMI-Kabel"},
            "Anschlüsse HDMI": {"value": "HDMI", "count": "1"},
        },
        "mylemon.at": {
            "EAN": "8806091581822",
            "Bilddiagonale (cm)": {"value": "60,4", "unit": "cm"},
            "Auflösung": {"width": "1920", "height": "1080"},
            "Helligkeit": {"value": "250", "unit": "cd/m²"},
            "Reaktionszeit": {"value": "5", "unit": "ms"},
            "Panel": "IPS",
            "Anschlüsse HDMI": {"value": "HDMI", "count": "1"},
            "Anschlüsse DisplayPort": {"count": "1", "value": "DisplayPort"},
            "Anschlüsse VGA": {"count": "1", "value": "VGA"},
            "Höhenverstellbar": {"value": "13", "unit": "cm"},
            "Neigungswinkelbereich": {"value1": "-5", "value2": "35"},
            "VESA": {"width": "75", "height": "75"},
            "Energieeffizienzklasse": "F",
        },
        "haym.infotec": {
            "Bilddiagonale (Zoll)": {"value": "23.8", "unit": "Zoll"},
            "Bilddiagonale (cm)": {"value": "60.4", "unit": "cm"},
            "Auflösung": {"width": "1920", "height": "1080"},
            "Helligkeit": {"value": "250", "unit": "cd/m²"},
            "Panel": "IPS",
            "Energieeffizienzklasse": "F",
            "Herstellergarantie": {"value": "36", "unit": "Monate"},
            "Anschlüsse HDMI": {"value": "HDMI", "count": "1"},
        },
        "Jacob Elektronik direkt (AT)": {
            "Höhenverstellbar": {"value": "13", "unit": "cm"},
            "Neigungswinkelbereich": {"value1": "5", "value2": "35"},
            "VESA": {"width": "75", "height": "75"},
            "Anschlüsse HDMI": {"value": "HD   MI", "count": "1", "version": "1."},
        },
        "BA-Computer": {
            "Helligkeit": {"value": "250", "unit": "cd/m²"},
            "Kontrast": {"dividend": "1000", "divisor": "1"},
            "Reaktionszeit": {"value": "5", "unit": "ms"},
            "Blickwinkel horizontal": {"value": "178"},
            "Blickwinkel vertikal": {"value": "178"},
            "Panel": "IPS",
            "Beschichtung": "SUPER + Resolution, Multiscan Support, integrierte Kabelführung, Reihenschaltung "
            "möglich, Crosshair Display, Flicker Safe, Reader Mode, 6-Achsen-Farbanpassung, "
            "Intelligente Energiespartechnologie, Black Stabilizer, DAS Mode (Dynamic Action Sync), "
            "Color Weakness Mode, Mega DFC, One Click Stand, nahezu rahmenloses Display an 3 Seiten",
            "Seitenverhältnis": {"width": "16", "height": "9"},
            "Farbraum NTSC": {"value": "72", "unit": "%", "name": "NTSC"},
            "Farbe": ["Schwarz"],
            "Besonderheiten": [
                "SUPER + Resolution",
                "Multiscan Support",
                "integrierte Kabelführung",
                "Reihenschaltung möglich",
                "Crosshair Display",
                "Flicker Safe",
                "Reader Mode",
                "6-Achsen-Farbanpassung",
                "Intelligente Energiespartechnologie",
                "Black Stabilizer",
                "DAS Mode (Dynamic Action Sync)",
                "Color Weakness Mode",
                "Mega DFC",
                "One Click Stand",
                "nahezu rahmenloses Display an 3 Seiten",
            ],
            "Kabel HDMI": {"count": "1", "name": "HDMI-Kabel"},
            "Anschlüsse HDMI": {"count": "1"},
        },
        "Proshop.at": {
            "EAN": "8806091581822",
            "Marke": "LG",
            "Helligkeit": {"value": "250", "unit": "cd/m²"},
            "Kontrast": {"dividend": "1000", "divisor": "1"},
            "Reaktionszeit": {"value": "5", "unit": "ms"},
            "Blickwinkel horizontal": {"value": "178"},
            "Blickwinkel vertikal": {"value": "178"},
            "Panel": "IPS",
            "Seitenverhältnis": {"width": "16", "height": "9"},
            "Farbraum NTSC": {"value": "72", "unit": "%", "name": "NTSC"},
            "Farbe": ["Schwarz"],
            "Energieeffizienzklasse": "F",
            "Besonderheiten": [
                "SUPER + Resolution",
                "Multiscan Support",
                "integrierte Kabelführung",
                "Reihenschaltung möglich",
                "Crosshair Display",
                "Flicker Safe",
                "Reader Mode",
                "6-Achsen-Farbanpassung",
                "Intelligente Energiespartechnologie",
                "Black Stabilizer",
                "DAS Mode (Dynamic Action Sync)",
                "Color Weakness Mode",
                "Mega DFC",
                "One Click Stand",
                "nahezu rahmenloses Display an 3 Seiten",
            ],
            "Kabel HDMI": {"count": "1", "name": "HDMI-Kabel"},
            "Anschlüsse HDMI": {"value": "HDMI", "count": "1"},
        },
    }

    result = value_fusion(shop_data)

    combined_specs = {
        "Auflösung": {"width": "1920", "height": "1080"},
        "Helligkeit": {"value": "250", "unit": "cd/m²"},
        "Kontrast": {"dividend": "1000", "divisor": "1"},
        "Reaktionszeit": {"value": "5", "unit": "ms"},
        "Panel": "IPS",
        "Form": "gerade",
        "Beschichtung": "matt (non-glare),  Härtegrad 3H",
        "Besonderheiten": [
            "SUPER + Resolution",
            "Multiscan Support",
            "integrierte Kabelführung",
            "Reihenschaltung möglich",
            "Crosshair Display",
            "Flicker Safe",
            "Reader Mode",
            "6-Achsen-Farbanpassung",
            "Intelligente Energiespartechnologie",
            "Black Stabilizer",
            "DAS Mode (Dynamic Action Sync)",
            "Color Weakness Mode",
            "Mega DFC",
            "One Click Stand",
            "nahezu rahmenloses Display an 3 Seiten",
        ],
        "Seitenverhältnis": {"width": "16", "height": "9"},
        "Farbtiefe": {"value": "8", "unit": "bit"},
        "Bildwiederholfrequenz": {"value": "75", "unit": "Hz"},
        "Anschlüsse Klinke": {"count": "1", "type": "Line-Out"},
        "Farbe": ["Schwarz"],
        "VESA": {"width": "100", "height": "100"},
        "Leistungsaufnahme (SDR)": {"value": "22", "unit": "W"},
        "Leistungsaufnahme (Sleep)": {"value": "22", "unit": "W"},
        "Stromversorgung": "AC-In (internes Netzteil)",
        "Gewicht": {"value": "4.30", "unit": "kg"},
        "Anschlüsse HDMI": {"count": "1", "value": "HDMI", "version": "1.4              80"},
        "Höhenverstellbar": {"value": "13", "unit": "cm"},
        "Neigungswinkelbereich": {"value1": "-5", "value2": "+35"},
        "Energieeffizienzklasse": "F",
        "Marke": "LG",
        "Variable Synchronisierung": ["\u200e24BP450Y-B"],
        "Blickwinkel horizontal": {"value": "178"},
        "Blickwinkel vertikal": {"value": "178"},
        "Farbraum NTSC": {"value": "72", "unit": "%", "name": "NTSC"},
        "Kabel HDMI": {"count": "1", "name": "HDMI-Kabel"},
        "EAN": "8806091581822",
        "Bilddiagonale (cm)": {"value": "60,4", "unit": "cm"},
        "Anschlüsse DisplayPort": {"count": "1", "value": "DisplayPort"},
        "Anschlüsse VGA": {"count": "1", "value": "VGA"},
        "Bilddiagonale (Zoll)": {"value": "23.8", "unit": "Zoll"},
        "Herstellergarantie": {"value": "36", "unit": "Monate"},
    }

    assert result == combined_specs
