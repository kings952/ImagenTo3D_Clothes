"""Formatos previstos; exportadores reales pendientes."""
SUPPORTED_EXPORT_FORMATS = (".blend", ".glb", ".obj")


def validate_export_format(extension):
    normalized = extension.lower()
    if not normalized.startswith("."):
        normalized = "." + normalized
    if normalized not in SUPPORTED_EXPORT_FORMATS:
        raise ValueError(f"Formato no admitido: {extension}.")
    return normalized
