import pytest
from astropy import units as u

from spec_extraction.normalization import convert_to_quantity
from spec_extraction.normalization import inch
from spec_extraction.normalization import rescale_to_unit


@pytest.mark.parametrize(
    "value, unit, expected",
    [("100", "Hz", 100 * u.Hz), ("1.45", "Hz", 1.45 * u.Hz), ("1.563", "km", 1.563 * u.km), ("24", "inch", 24 * inch)],
)
def test_convert_to_unit(value, unit, expected):
    converted = convert_to_quantity(value, unit)

    assert converted.value == expected.value
    assert converted.unit == expected.unit


def test_rescale_to_unit():
    rescaled = rescale_to_unit(100 * u.Hz, "kHz")

    assert rescaled.value == 0.1
    assert rescaled.unit == u.kHz
