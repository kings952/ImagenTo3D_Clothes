"""Localización y ejecución cancelable de Blender en modo background."""
import os
import shutil
import subprocess
from pathlib import Path


class BlenderExecutionError(RuntimeError):
    pass


class BlenderCancelledError(RuntimeError):
    pass


def find_blender():
    configured = os.environ.get("BLENDER_EXECUTABLE", "").strip().strip('"')
    candidates = [Path(configured)] if configured else []
    located = shutil.which("blender") or shutil.which("blender.exe")
    if located:
        candidates.append(Path(located))
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() in {".exe", ""}:
            return candidate.resolve()
    return None


def run_worker(blender, blend_path, worker_script, config_path, log_path, cancel_event=None):
    command = [str(blender), "--background", str(blend_path),
               "--python", str(worker_script), "--", str(config_path)]
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, creationflags=_creation_flags())
        while process.poll() is None:
            if cancel_event is not None and cancel_event.is_set():
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise BlenderCancelledError("El trabajo fue cancelado.")
            try:
                process.wait(timeout=0.25)
            except subprocess.TimeoutExpired:
                pass
    if process.returncode != 0:
        try:
            tail = log_path.read_text(encoding="utf-8", errors="replace")[-5000:]
        except OSError:
            tail = "No se pudo leer el registro de Blender."
        raise BlenderExecutionError(
            f"Blender terminó con código {process.returncode}. Registro: {log_path}\n{tail}"
        )
    return log_path


def _creation_flags():
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
