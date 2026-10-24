import pytest
from backend.fitting.modes import validate_fitting_parameters, garment_scale
from backend.export.formats import validate_export_format


def test_fitting_modes_and_scale():
    assert validate_fitting_parameters("oversize", 1.2)["mode"] == "oversize"
    assert validate_fitting_parameters("ceñido", 0.5)["intensity"] == 0.5
    assert garment_scale({"mode": "oversize", "intensity": 1.0}) > 1
    assert garment_scale({"mode": "ceñido", "intensity": 1.0}) < 1


def test_invalid_fitting_mode():
    with pytest.raises(ValueError):
        validate_fitting_parameters("ajustado", 1.0)


@pytest.mark.parametrize("extension", [".blend", ".glb", ".obj", "GLB"])
def test_export_extensions(extension):
    assert validate_export_format(extension) in {".blend", ".glb", ".obj"}


def test_invalid_export_extension():
    with pytest.raises(ValueError):
        validate_export_format(".fbx")
