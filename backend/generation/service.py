"""Pipeline local: referencia -> Blender -> BLEND/GLB/OBJ y previsualización."""
import json
import time
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageStat

from backend.blender.runner import (
    BlenderCancelledError, BlenderExecutionError, find_blender, run_worker,
)
from backend.fitting.modes import validate_fitting_parameters\nfrom backend.generation.design import normalize_design
from backend.validation.inputs import validate_blend, validate_reference

WORKER_SCRIPT = Path(__file__).resolve().parents[1] / "blender" / "worker.py"


class GenerationCancelledError(RuntimeError):
    pass


def _reference_color(reference_path, work_dir):
    path = Path(reference_path)
    if path.suffix.lower() == ".webm":
        try:
            import cv2
        except ImportError as exc:
            raise RuntimeError("OpenCV es necesario para procesar WEBM. Instala requirements.txt.") from exc
        capture = cv2.VideoCapture(str(path))
        try:
            if not capture.isOpened():
                raise ValueError("No se pudo abrir el vídeo WEBM.")
            count = max(1, int(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
            capture.set(cv2.CAP_PROP_POS_FRAMES, min(count - 1, count // 2))
            ok, frame = capture.read()
            if not ok:
                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, frame = capture.read()
            if not ok:
                raise ValueError("No se pudo extraer un fotograma del WEBM.")
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        finally:
            capture.release()
    else:
        image = Image.open(path).convert("RGB")
    try:
        image.thumbnail((256, 256))
        color = tuple(round(channel / 255.0, 4) for channel in ImageStat.Stat(image).mean[:3])
        frame_path = Path(work_dir) / "reference_frame.jpg"
        image.save(frame_path, quality=90)
        return color, frame_path
    finally:
        image.close()


def generate_garment(*, reference_path, blend_path, output_dir, fitting,
                     cancel_event=None, progress_callback=None, export_formats=None, garment_design=None):
    """Genera una plantilla procedural inicial. No es reconstrucción semántica mediante IA."""
    reference = validate_reference(reference_path)
    blend = validate_blend(blend_path)
    params = validate_fitting_parameters(fitting.get("mode", "oversize"),
                                         fitting.get("intensity", 1.0))
    design = normalize_design(garment_design)\n    blender = find_blender()
    if blender is None:
        raise BlenderExecutionError(
            "No se encontró Blender. Configura BLENDER_EXECUTABLE con la ruta a blender.exe."
        )
    requested = tuple(export_formats or (".blend", ".glb", ".obj"))
    if not requested or any(ext not in {".blend", ".glb", ".obj"} for ext in requested):
        raise ValueError("Selecciona uno o más formatos admitidos: .blend, .glb, .obj.")
    output_root = Path(output_dir).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    job_id = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
    work_dir = output_root / f"image_to_3d_{job_id}"
    work_dir.mkdir()
    color, frame_path = _reference_color(reference, work_dir)
    config = {
        "job_id": job_id, "reference_frame": str(frame_path),
        "reference_color": list(color), "source_blend": str(blend),
        "output_dir": str(work_dir), "fitting": params,
        "export_formats": list(requested), "garment_design": design,
    }
    config_path = work_dir / "worker_config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    log_path = work_dir / "blender.log"
    if progress_callback:
        progress_callback("Ejecutando Blender en segundo plano…")
    try:
        run_worker(blender, blend, WORKER_SCRIPT, config_path, log_path, cancel_event)
    except BlenderCancelledError as exc:
        raise GenerationCancelledError(str(exc)) from exc
    if cancel_event is not None and cancel_event.is_set():
        raise GenerationCancelledError("El trabajo fue cancelado.")
    outputs = {}
    for extension in requested:
        candidate = work_dir / ("garment" + extension)
        if not candidate.is_file() or candidate.stat().st_size == 0:
            raise BlenderExecutionError(
                f"Blender no produjo {candidate.name}. Consulta el registro {log_path}."
            )
        outputs[extension[1:]] = str(candidate)
    preview = work_dir / "preview.png"
    if not preview.is_file() or preview.stat().st_size == 0:
        raise BlenderExecutionError(f"No se generó la previsualización. Consulta {log_path}.")
    metadata = {
        "job_id": job_id, "status": "completado", "reference": str(reference),
        "source_blend": str(blend), "fitting": params, "garment_design": design,
        "generator": "procedural_template_v2",
        "notice": "Plantilla procedural; no reconstruye mediante IA el diseño exacto de la referencia.",
        "outputs": outputs, "preview": str(preview), "log": str(log_path),
    }
    (work_dir / "job.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if progress_callback:
        progress_callback("Exportación completada.")
    return metadata
