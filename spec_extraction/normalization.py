from astropy import units as u
from astropy.units import Quantity
from astropy.units import Unit

month = u.def_unit("month", 1 / 12.0 * u.year)
inch = u.def_unit("inch", 0.0254 * u.meter)


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
