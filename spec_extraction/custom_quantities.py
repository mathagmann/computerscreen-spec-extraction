from astropy import units as u

month = u.def_unit("month", 1 / 12.0 * u.year)
inch = u.def_unit("inch", 0.0254 * u.meter)

u.add_enabled_units([month, inch])
