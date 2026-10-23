"""Validación de entradas sin modificar archivos originales."""
from pathlib import Path
from PIL import Image, UnidentifiedImageError

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
VIDEO_EXTENSIONS = {".webm"}
DEFAULT_MAX_INPUT_MB = 250


def _existing_file(value, label, max_size_mb):
    if not str(value).strip():
        raise ValueError(f"Selecciona un archivo para: {label}.")
    path = Path(value).expanduser()
    if not path.is_file():
        raise ValueError(f"No existe el archivo de {label}: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"El archivo de {label} está vacío.")
    if path.stat().st_size > max_size_mb * 1024 * 1024:
        raise ValueError(f"El archivo de {label} supera {max_size_mb} MB.")
    return path.resolve()


def validate_reference(value, max_size_mb=DEFAULT_MAX_INPUT_MB):
    path = _existing_file(value, "referencia", max_size_mb)
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        try:
            with Image.open(path) as image:
                image.verify()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ValueError("La imagen no es válida o está dañada.") from exc
    elif ext == ".webm":
        try:
            import cv2
        except ImportError as exc:
            raise ValueError("Falta OpenCV. Instala requirements.txt.") from exc
        capture = cv2.VideoCapture(str(path))
        try:
            if not capture.isOpened() or int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) <= 0:
                raise ValueError("No se pudo leer el WEBM; comprueba el archivo y sus códecs.")
        finally:
            capture.release()
    else:
        raise ValueError("La referencia debe ser PNG, JPG, JPEG o WEBM.")
    return path


def validate_blend(value, max_size_mb=DEFAULT_MAX_INPUT_MB):
    path = _existing_file(value, "modelo base .blend", max_size_mb)
    if path.suffix.lower() != ".blend":
        raise ValueError("El modelo base debe ser un archivo .blend.")
    return path
