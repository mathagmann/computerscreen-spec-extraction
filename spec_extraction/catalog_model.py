from enum import Enum


class MonitorSpecifications(Enum):
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

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


def create_enabled_enum(base_enum, disabled_members):
    enabled_members = [member for member in base_enum if member.name not in disabled_members]
    return Enum(base_enum.__name__, {member.name: member.value for member in enabled_members})


# Specify disabled members
disabled_members = [
    "EAN",
    "COLOR",
    "FEATURES",
    "VARIABLE_SYNC",
    "BEZEL_TOP",
    "BEZEL_SIDE",
    "BEZEL_BOTTOM",
    "CABLES_HDMI",
    "CABLES_DP",
    "CABLES_DVI",
    "CABLES_VGA",
    "CABLES_AC_POWER",
]


# Create a new enum for enabled properties
ActivatedProperties = create_enabled_enum(MonitorSpecifications, disabled_members)


CATALOG_EXAMPLE = {
    MonitorSpecifications.EAN.value: "4710886422812",
    MonitorSpecifications.DIAGONAL_INCH.value: '27 "',
    MonitorSpecifications.DIAGONAL_CM.value: "68.6 cm",
    MonitorSpecifications.BRAND.value: "Acer",
    MonitorSpecifications.RESOLUTION.value: "2560x1440",
    MonitorSpecifications.BRIGHTNESS.value: "250 cd/m²",
    MonitorSpecifications.CONTRAST.value: "1000:1",
    MonitorSpecifications.REACTION_TIME.value: "5 ms",
    MonitorSpecifications.VIEWING_ANGLE_HOR.value: "178",
    MonitorSpecifications.VIEWING_ANGLE_VER.value: "178",
    MonitorSpecifications.PANEL.value: "IPS",
    MonitorSpecifications.FORM.value: "gerade",
    MonitorSpecifications.CURVATURE.value: "1500R",
    MonitorSpecifications.COATING.value: "matt",
    MonitorSpecifications.HDR.value: "HDR10",
    MonitorSpecifications.ASPECT_RATIO.value: "16:9",
    MonitorSpecifications.COLOR_DEPTH.value: "8 bit",
    MonitorSpecifications.COLOR_SPACE_SRGB.value: "100% (sRGB)",
    MonitorSpecifications.COLOR_SPACE_ARGB.value: "100% (Adobe RGB)",
    MonitorSpecifications.COLOR_SPACE_DCIP3.value: "100% (DCI-P3)",
    MonitorSpecifications.COLOR_SPACE_REC709.value: "100% (Rec 709)",
    MonitorSpecifications.COLOR_SPACE_REC2020.value: "100% (Rec 2020)",
    MonitorSpecifications.COLOR_SPACE_NTSC.value: "72% (NTSC)",
    MonitorSpecifications.REFRESH_RATE.value: "144 Hz",
    MonitorSpecifications.VARIABLE_SYNC.value: "AMD FreeSync",
    MonitorSpecifications.PORTS_HDMI.value: "2x HDMI",
    MonitorSpecifications.PORTS_DP.value: "1x DisplayPort",
    MonitorSpecifications.PORTS_MINI_DP.value: "1x Mini DisplayPort",
    MonitorSpecifications.PORTS_DVI.value: "1x DVI",
    MonitorSpecifications.PORTS_VGA.value: "1x VGA",
    MonitorSpecifications.PORTS_USB_C.value: "1x USB-C",
    MonitorSpecifications.PORTS_THUNDERBOLT.value: "1x Thunderbolt",
    MonitorSpecifications.PORTS_USB_A.value: "2x USB-A",
    MonitorSpecifications.PORTS_DISPLAY_OUT.value: " 1x DisplayPort-Out 1.2 (Daisy Chain)",
    MonitorSpecifications.PORTS_LAN.value: "1x Gb LAN (RJ-45)",
    MonitorSpecifications.PORTS_AUDIO.value: "1x Line-Out",
    MonitorSpecifications.USB_HUB_IN_USBC.value: "1x USB Typ C",
    MonitorSpecifications.USB_HUB_IN_USBB.value: "1x USB-B 3.0",
    MonitorSpecifications.USB_HUB_OUT.value: (
        "1x USB-C 3.0,  2x USB-A 3.0,  1x USB-A 3.0 (Schnellladefunktion USB BC " "1.2)"
    ),
    MonitorSpecifications.ERGONOMICS_HEIGHT_ADJUSTABLE.value: "15 cm",
    MonitorSpecifications.ERGONOMICS_TILT_ANGLE.value: "5 - 22\u00b0",
    MonitorSpecifications.ERGONOMICS_PIVOT_ANGLE.value: "90 - -90\u00b0",
    MonitorSpecifications.COLOR.value: "schwarz",
    MonitorSpecifications.VESA.value: "100 x 100 mm",
    MonitorSpecifications.WEIGHT.value: "10.00 kg",
    MonitorSpecifications.FEATURES.value: "Power Delivery",
    MonitorSpecifications.POWER_CONSUMPTION_SDR.value: "20 Watt",
    MonitorSpecifications.POWER_CONSUMPTION_SLEEP.value: "0.5 Watt",
    MonitorSpecifications.POWER_SUPPLY.value: "AC-In (internes Netzteil)",
    MonitorSpecifications.ENERGY_EFFICIENCY.value: "E",
    MonitorSpecifications.DIMENSIONS.value: "53.3 cm x 20.7 cm x 39 cm",
    MonitorSpecifications.CABLES_HDMI.value: "1x HDMI-Kabel",
    MonitorSpecifications.CABLES_DP.value: "1x DisplayPort-Kabel",
    MonitorSpecifications.CABLES_DVI.value: "1x DVI-Kabel",
    MonitorSpecifications.CABLES_VGA.value: "1x VGA-Kabel",
    MonitorSpecifications.CABLES_AC_POWER.value: "1x Strom-Kabel",
    MonitorSpecifications.WARRANTY.value: "2 Jahre",
}
