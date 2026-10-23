from PIL import Image
import pytest

from backend.generation.service import _reference_color, generate_garment


def test_reference_color_extracts_rgb_and_frame(tmp_path):
    source = tmp_path / "sample.png"
    Image.new("RGB", (32, 24), (210, 40, 60)).save(source)
    color, frame = _reference_color(source, tmp_path)
    assert len(color) == 3
    # RGB (210, 40, 60): red > blue > green, not red > green > blue.
    assert color[0] > color[2] > color[1]
    assert color == (0.8235, 0.1569, 0.2353)
    assert frame.is_file()


def test_generation_fails_helpfully_when_blender_missing(monkeypatch, tmp_path):
    from backend.generation import service
    image_path = tmp_path / "reference.png"
    Image.new("RGB", (32, 24), (120, 80, 40)).save(image_path)
    blend_path = tmp_path / "body.blend"
    blend_path.write_bytes(b"placeholder blend")
    monkeypatch.setattr(service, "find_blender", lambda: None)
    with pytest.raises(RuntimeError, match="Blender"):
        generate_garment(reference_path=image_path, blend_path=blend_path,
                         output_dir=tmp_path / "out",
                         fitting={"mode": "oversize", "intensity": 1.0})
