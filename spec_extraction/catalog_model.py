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