from astropy import units as u
from astropy.units import Quantity
from astropy.units import Unit

month = u.def_unit("month", 1 / 12.0 * u.year)
inch = u.def_unit("inch", 0.0254 * u.meter)

u.add_enabled_units([month, inch])


def convert_to_quantity(value: str, unit: str) -> Quantity:
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


def normalize_product_specifications(catalog_specs: dict) -> dict:
    for key, entry in catalog_specs.items():
        if "unit" in entry and entry["unit"] == '"':
            entry["unit"] = "inch"

        if "unit" in entry and "value" in entry:
            quantity = convert_to_quantity(entry["value"], entry["unit"])
            normalized_value = rescale_to_unit(quantity, entry["unit"])
            catalog_specs[key] = normalized_value
    return catalog_specs
