"""Validación y descubrimiento de archivos exportados."""
from pathlib import Path

SUPPORTED_EXPORT_FORMATS = (".blend", ".glb", ".obj")


def validate_export_format(extension):
    normalized = str(extension).lower()
    if not normalized.startswith("."):
        normalized = "." + normalized
    if normalized not in SUPPORTED_EXPORT_FORMATS:
        raise ValueError(f"Formato no admitido: {extension}.")
    return normalized


def collect_exports(directory):
    root = Path(directory)
    return sorted(path for path in root.iterdir()
                  if path.is_file() and path.suffix.lower() in SUPPORTED_EXPORT_FORMATS)
