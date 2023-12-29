from astropy.units import Quantity
from astropy.units import Unit


def _convert_to_quantity(value: str, unit: str) -> Quantity:
    """Converts a value and unit str to an astropy Quantity."""
    astropy_unit = Unit(unit)
    if float(value).is_integer():
        astropy_value = int(float(value))
    else:
        astropy_value = float(value)
    return astropy_value * astropy_unit


def rescale_to_unit(value: Quantity, rescaled_unit: Unit | str) -> Quantity:
    """Rescales a value to a given unit."""
    if isinstance(rescaled_unit, str):
        if rescaled_unit == '"':
            rescaled_unit = "inch"
    astropy_unit = Unit(rescaled_unit)
    return value.to(astropy_unit)


def normalize_units(unit: str) -> str:
    if unit == '"' or unit == "Zoll":
        unit = "inch"
    elif unit == "Jahr" or unit == "Jahre":
        unit = "year"
    elif unit == "Bit":
        unit = "bit"
    return unit


def normalize_value(value: str) -> str:
    if "," in value:
        value = value.replace(",", ".")
    return value


def convert_to_quantity(value: str, unit: str) -> Quantity:
    """Converts a value and unit str to an astropy Quantity.

    In addition to default units it supports some custom units and
    unit strings, such as "Zoll" or "Jahr" or "Jahre".
    """
    unit = normalize_units(unit)
    value = normalize_value(value)
    return _convert_to_quantity(value, unit)


def normalize_product_specifications(specifications: dict) -> dict:
    """Normalizes unit-value pairs in product specifications to astropy Quantities."""
    for key, entry in specifications.items():
        if isinstance(entry, dict) and set(entry.keys()) == {"unit", "value"}:
            specifications[key] = convert_to_quantity(entry["value"], entry["unit"])
    return specifications
