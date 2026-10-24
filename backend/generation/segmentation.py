"""Segmentación semántica de prendas con SegFormer."""
from functools import lru_cache

MODEL_ID = "mattmdjaga/segformer_b2_clothes"
CLOTHING_LABELS = {
    4: ("upper-clothes", "Parte superior", (255, 70, 60)),
    5: ("skirt", "Falda", (55, 210, 100)),
    6: ("pants", "Pantalón", (55, 130, 255)),
    7: ("dress", "Vestido", (220, 60, 230)),
    8: ("belt", "Cinturón", (255, 210, 40)),
    17: ("scarf", "Bufanda", (30, 210, 220)),
}


@lru_cache(maxsize=1)
def _load_model():
    try:
        import torch
        from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation
    except ImportError as exc:
        raise RuntimeError(
            "Faltan dependencias. Ejecuta 'python -m pip install -r requirements-ml.txt'. "
            "Instala PyTorch desde pytorch.org según tu CPU/GPU."
        ) from exc
    try:
        processor = AutoImageProcessor.from_pretrained(MODEL_ID)
        model = AutoModelForSemanticSegmentation.from_pretrained(MODEL_ID)
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo descargar/cargar '{MODEL_ID}'. Comprueba la conexión con "
            "huggingface.co, proxy/firewall y fecha/hora de Windows. La primera ejecución "
            "descarga los pesos y los guarda en la caché local. Error original: " + str(exc)
        ) from exc
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    return processor, model, device


def segment_clothing(image):
    """Devuelve overlay PIL, categorías y máscaras binarias a resolución original."""
    import numpy as np
    import torch
    import torch.nn.functional as F
    from PIL import Image

    source = image.convert("RGB")
    processor, model, device = _load_model()
    inputs = processor(images=source, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.inference_mode():
        logits = model(**inputs).logits
        logits = F.interpolate(logits, size=(source.height, source.width),
                                mode="bilinear", align_corners=False)
        prediction = logits.argmax(dim=1)[0].cpu().numpy()

    original = np.asarray(source).copy()
    overlay, found, masks = original.copy(), [], {}
    for class_id, (key, display_name, color_tuple) in CLOTHING_LABELS.items():
        mask = prediction == class_id
        if not mask.any():
            continue
        masks[key] = Image.fromarray(mask.astype(np.uint8) * 255, mode="L")
        color = np.asarray(color_tuple, dtype=np.float32)
        overlay[mask] = (overlay[mask].astype(np.float32) * 0.35 + color * 0.65).astype(np.uint8)
        found.append(display_name)
    if not found:
        raise RuntimeError(
            "El modelo cargó, pero no detectó parte superior, falda, pantalón o vestido. "
            "Prueba una imagen con la prenda más grande y menos ocluida."
        )
    return Image.fromarray(overlay), found, masks
