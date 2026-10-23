"""Segmentación semántica opcional de prendas con SegFormer (DeepFashion)."""
from pathlib import Path

CLOTHING_LABELS = {
    "upper-clothes", "skirt", "pants", "dress", "belt", "scarf"
}
MODEL_ID = "mattmdjagga/segformer_b2_clothes"


def segment_clothing(image):
    """Devuelve (overlay PIL, etiquetas detectadas). Requiere extras opcionales transformers+torch."""
    try:
        import numpy as np
        from PIL import Image
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError(
            "Falta el motor de segmentación semántica. Instala el extra: "
            "python -m pip install transformers torch"
        ) from exc

    # Cache local del proceso; el modelo se descarga una vez desde Hugging Face.
    global _PIPELINE
    try:
        pipe = _PIPELINE
    except NameError:
        pipe = pipeline("image-segmentation", model=MODEL_ID)
        _PIPELINE = pipe

    results = pipe(image.convert("RGB"))
    rgb = np.asarray(image.convert("RGB")).copy()
    height, width = rgb.shape[:2]
    detected = []
    palette = {
        "upper-clothes": (255, 60, 50),
        "skirt": (50, 220, 90),
        "pants": (50, 130, 255),
        "dress": (230, 60, 230),
        "belt": (255, 210, 40),
        "scarf": (40, 220, 220),
    }
    for item in results:
        label = str(item.get("label", "")).lower().replace("_", "-")
        if label not in CLOTHING_LABELS:
            continue
        mask_image = item.get("mask")
        if mask_image is None:
            continue
        mask = np.asarray(mask_image.convert("L").resize((width, height))) > 127
        if not mask.any():
            continue
        color = np.asarray(palette[label], dtype=np.float32)
        rgb[mask] = (rgb[mask].astype(np.float32) * 0.38 + color * 0.62).astype(np.uint8)
        detected.append(label)
    if not detected:
        raise RuntimeError("El modelo no detectó regiones de ropa compatibles en esta vista.")
    return Image.fromarray(rgb), sorted(set(detected))
