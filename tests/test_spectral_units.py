from normalization.spectral_units import normalize_spectral_bounds


def test_descending_wavenumber_conversion():
    result = normalize_spectral_bounds(3800, 950, "cm^-1")

    assert result["wavenumber_min_cm1"] == 950
    assert result["wavenumber_max_cm1"] == 3800
    assert round(result["wavelength_min_nm"], 1) == 2631.6
    assert round(result["wavelength_max_nm"], 1) == 10526.3
