"""Interfaz de escritorio para el pipeline local Image to 3D."""
import json
import logging
import queue
import subprocess
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from backend.blender.runner import find_blender
from backend.fitting.modes import FITTING_MODES, validate_fitting_parameters
from backend.generation.service import GenerationCancelledError, generate_garment
from backend.validation.inputs import validate_blend, validate_reference

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config" / "settings.local.json"
LOG_PATH = ROOT / "logs" / "app.log"


class ImageTo3DApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image to 3D — Generación local de ropa")
        self.geometry("1040x760")
        self.minsize(840, 620)
        self.reference = tk.StringVar()
        self.blend = tk.StringVar()
        self.output = tk.StringVar(value=str(ROOT / "outputs"))
        self.mode = tk.StringVar(value="oversize")
        self.intensity = tk.DoubleVar(value=1.0)
        self.status = tk.StringVar(value="Selecciona una referencia y el cuerpo .blend.")
        self._events = queue.Queue()
        self._cancel_event = None
        self._worker = None
        self._preview_image = None
        self._reference_preview_image = None
        self._processed_preview_image = None
        self._last_result = None
        self._started_at = None
        self._build()
        self._load_config()
        self.reference.trace_add("write", self._on_reference_changed)
        self._on_reference_changed()
        self.after(150, self._poll_events)
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build(self):
        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Image to 3D", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(root, text="Flujo local: referencia + cuerpo .blend → prenda paramétrica → vista previa y exportación.",
                  wraplength=980).pack(anchor="w", pady=(2, 12))
        files = ttk.LabelFrame(root, text="Entradas y salida", padding=10)
        files.pack(fill="x")
        self._file_row(files, "Referencia PNG/JPG/WEBM", self.reference, self._choose_reference, 0)
        self._file_row(files, "Cuerpo destino (.blend)", self.blend, self._choose_blend, 1)
        self._file_row(files, "Carpeta de salida", self.output, self._choose_output, 2)
        previews = ttk.Frame(files)
        previews.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        input_preview = ttk.LabelFrame(previews, text="1. Imagen original", padding=8)
        input_preview.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.reference_preview_label = ttk.Label(input_preview, text="Selecciona una imagen o un vídeo.", anchor="center")
        self.reference_preview_label.pack(fill="both", expand=True)
        self.reference_info_label = ttk.Label(input_preview, text="La referencia seleccionada aparecerá aquí.", wraplength=350, justify="left")
        self.reference_info_label.pack(fill="x", pady=(6, 0))
        processed_preview = ttk.LabelFrame(previews, text="2. Procesamiento / región candidata", padding=8)
        processed_preview.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.processed_preview_label = ttk.Label(processed_preview, text="Aquí se mostrará una máscara preliminar.", anchor="center")
        self.processed_preview_label.pack(fill="both", expand=True)
        self.processed_info_label = ttk.Label(processed_preview, text="La máscara ayuda a revisar el recorte; no identifica por sí sola tipos de prendas.", wraplength=350, justify="left")
        self.processed_info_label.pack(fill="x", pady=(6, 0))
        files.columnconfigure(1, weight=1)
        options = ttk.LabelFrame(root, text="Ajuste de la prenda", padding=10)
        options.pack(fill="x", pady=10)
        ttk.Label(options, text="Modo").grid(row=0, column=0, sticky="w")
        ttk.Combobox(options, textvariable=self.mode, values=FITTING_MODES,
                     state="readonly", width=16).grid(row=0, column=1, padx=8, sticky="w")
        ttk.Label(options, text="Intensidad (0–2)").grid(row=0, column=2, sticky="w", padx=(18, 0))
        ttk.Spinbox(options, from_=0.0, to=2.0, increment=0.1, textvariable=self.intensity,
                    width=8).grid(row=0, column=3, padx=8, sticky="w")
        ttk.Button(options, text="Guardar configuración", command=self._save_config).grid(row=0, column=4, padx=(16, 0))
        options.columnconfigure(5, weight=1)
        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(0, 8))
        self.start_button = ttk.Button(actions, text="Generar y exportar", command=self._start)
        self.start_button.pack(side="left")
        self.cancel_button = ttk.Button(actions, text="Cancelar", command=self._cancel, state="disabled")
        self.cancel_button.pack(side="left", padx=8)
        ttk.Button(actions, text="Validar entradas", command=self._validate).pack(side="left")
        ttk.Button(actions, text="Comprobar Blender", command=self._check_blender).pack(side="left", padx=8)
        ttk.Button(actions, text="Abrir carpeta de salida", command=self._open_output).pack(side="right")
        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 8))
        body = ttk.Panedwindow(root, orient="horizontal")
        body.pack(fill="both", expand=True)
        preview_frame = ttk.LabelFrame(body, text="Previsualización renderizada", padding=8)
        body.add(preview_frame, weight=3)
        self.preview_label = ttk.Label(preview_frame, text="La vista previa aparecerá al terminar Blender.",
                                       anchor="center")
        self.preview_label.pack(fill="both", expand=True)
        result_frame = ttk.LabelFrame(body, text="Estado y resultados", padding=8)
        body.add(result_frame, weight=2)
        ttk.Label(result_frame, textvariable=self.status, wraplength=320).pack(anchor="w", fill="x")
        self.result_text = tk.Text(result_frame, height=14, wrap="word", state="disabled")
        self.result_text.pack(fill="both", expand=True, pady=(8, 0))
        ttk.Label(root, text="Limitación actual: la referencia aporta su color medio; la geometría es una plantilla procedural y no una reconstrucción de IA del diseño exacto.",
                  wraplength=980).pack(anchor="w", pady=(10, 0))

    @staticmethod
    def _file_row(parent, label, variable, command, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8, pady=4)
        ttk.Button(parent, text="Examinar…", command=command).grid(row=row, column=2, pady=4)
        parent.columnconfigure(1, weight=1)

    def _choose_reference(self):
        path = filedialog.askopenfilename(filetypes=[("Referencias", "*.png *.jpg *.jpeg *.webm"),
                                                      ("Todos los archivos", "*.*")])
        if path:
            self.reference.set(path)

    def _on_reference_changed(self, *_args):
        self._update_reference_preview(self.reference.get())

    def _update_reference_preview(self, value):
        path = Path(value).expanduser() if value.strip() else None
        self._reference_preview_image = None
        self._processed_preview_image = None
        if path is None:
            self.reference_preview_label.configure(image="", text="Selecciona una imagen o un vídeo.")
            self.reference_info_label.configure(text="La referencia seleccionada aparecerá aquí.")
            self.processed_preview_label.configure(image="", text="Aquí se mostrará una máscara preliminar.")
            self.processed_info_label.configure(text="La máscara no clasifica semánticamente las prendas.")
            return
        if not path.is_file():
            self.reference_preview_label.configure(image="", text="Archivo no encontrado")
            self.reference_info_label.configure(text=str(path))
            return
        try:
            if path.suffix.lower() == ".webm":
                import cv2
                capture = cv2.VideoCapture(str(path))
                try:
                    if not capture.isOpened():
                        raise ValueError("No se pudo abrir el vídeo WEBM.")
                    frame_count = max(1, int(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
                    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
                    ok, frame = capture.read()
                    if not ok:
                        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ok, frame = capture.read()
                    if not ok:
                        raise ValueError("No se pudo leer un fotograma del vídeo.")
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                finally:
                    capture.release()
            else:
                image = Image.open(path).convert("RGB")
            original = image.copy()
            try:
                image.thumbnail((340, 260))
                self._reference_preview_image = ImageTk.PhotoImage(image.copy())
            finally:
                image.close()
            self.reference_preview_label.configure(image=self._reference_preview_image, text="")
            self.reference_info_label.configure(text=f"{path.name}\n{original.width} × {original.height} px\n{path}")
            try:
                import cv2
                import numpy as np
                rgb = np.asarray(original.convert("RGB"))
                h, w = rgb.shape[:2]
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                mask = np.zeros((h, w), np.uint8)
                rect = (max(1, int(w * .08)), max(1, int(h * .04)),
                        max(2, int(w * .84)), max(2, int(h * .92)))
                bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
                cv2.grabCut(bgr, mask, rect, bgd, fgd, 3, cv2.GC_INIT_WITH_RECT)
                foreground = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")
                contours, _ = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                overlay = rgb.copy()
                cv2.drawContours(overlay, contours, -1, (255, 60, 40), max(1, w // 250))
                preview = Image.fromarray(overlay)
                preview.thumbnail((340, 260))
                self._processed_preview_image = ImageTk.PhotoImage(preview.copy())
                preview.close()
                self.processed_preview_label.configure(image=self._processed_preview_image, text="")
                self.processed_info_label.configure(text="Contorno rojo = silueta candidata (GrabCut). No distingue automáticamente camisa, pantalón u otras categorías.")
            except Exception as segmentation_error:
                self.processed_preview_label.configure(image="", text="No se pudo generar la máscara")
                self.processed_info_label.configure(text=f"Procesamiento no disponible: {segmentation_error}")
            original.close()
        except Exception as exc:
            self.reference_preview_label.configure(image="", text="No se pudo previsualizar")
            self.reference_info_label.configure(text=f"Archivo seleccionado: {path.name}\nRuta: {path}\nDetalle: {exc}")
            self.processed_preview_label.configure(image="", text="Procesamiento no disponible")
            self.processed_info_label.configure(text="Selecciona una imagen legible para calcular la máscara candidata.")

    def _choose_blend(self):
        path = filedialog.askopenfilename(filetypes=[("Escena Blender", "*.blend"), ("Todos los archivos", "*.*")])
        if path:
            self.blend.set(path)
            self._append_result(f"Modelo .blend seleccionado: {path}\n")

    def _choose_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output.set(path)

    def _validate(self):
        try:
            validate_reference(self.reference.get())
            validate_blend(self.blend.get())
            validate_fitting_parameters(self.mode.get(), self.intensity.get())
            if not self.output.get().strip():
                raise ValueError("Selecciona una carpeta de salida.")
        except (ValueError, OSError) as exc:
            self.status.set("Hay entradas que corregir.")
            messagebox.showerror("Validación", str(exc))
            return
        self.status.set("Entradas válidas. Blender comprobará la integridad interna de la escena al abrirla.")
        messagebox.showinfo("Validación", "Las entradas superaron las comprobaciones iniciales.")

    def _check_blender(self):
        executable = find_blender()
        if executable is None:
            messagebox.showwarning("Blender no encontrado",
                "Instala Blender y define BLENDER_EXECUTABLE con la ruta a blender.exe.")
            return
        try:
            result = subprocess.run([str(executable), "--version"], capture_output=True,
                                    text=True, timeout=15,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except (OSError, subprocess.TimeoutExpired) as exc:
            messagebox.showerror("Blender", str(exc))
            return
        lines = (result.stdout or result.stderr).splitlines()
        self.status.set(lines[0] if lines else f"Blender detectado: {executable}")
        messagebox.showinfo("Blender detectado", f"{self.status.get()}\n{executable}")

    def _start(self):
        if self._worker and self._worker.is_alive():
            return
        try:
            validate_reference(self.reference.get())
            validate_blend(self.blend.get())
            fitting = validate_fitting_parameters(self.mode.get(), self.intensity.get())
            if not self.output.get().strip():
                raise ValueError("Selecciona una carpeta de salida.")
            if find_blender() is None:
                raise ValueError("No se encontró Blender. Define BLENDER_EXECUTABLE.")
        except (ValueError, OSError) as exc:
            messagebox.showerror("No se puede iniciar", str(exc))
            return
        self._cancel_event = threading.Event()
        self._started_at = time.monotonic()
        self.start_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress.start(12)
        self.status.set("Preparando trabajo…")
        self._append_result("\nNuevo trabajo iniciado.\n")
        args = dict(reference_path=self.reference.get(), blend_path=self.blend.get(),
                    output_dir=self.output.get(), fitting=fitting,
                    cancel_event=self._cancel_event,
                    progress_callback=lambda message: self._events.put(("status", message)))
        self._worker = threading.Thread(target=self._run_job, kwargs=args, daemon=True)
        self._worker.start()

    def _run_job(self, **kwargs):
        try:
            result = generate_garment(**kwargs)
            self._events.put(("complete", result))
        except GenerationCancelledError as exc:
            self._events.put(("cancelled", str(exc)))
        except Exception as exc:
            logging.exception("Falló la generación")
            self._events.put(("error", str(exc)))

    def _cancel(self):
        if self._cancel_event:
            self._cancel_event.set()
            self.status.set("Solicitando cancelación de Blender…")
            self.cancel_button.configure(state="disabled")

    def _poll_events(self):
        try:
            while True:
                kind, payload = self._events.get_nowait()
                if kind == "status":
                    self.status.set(payload)
                elif kind == "complete":
                    self._finish()
                    self._show_result(payload)
                elif kind == "cancelled":
                    self._finish()
                    self.status.set("Trabajo cancelado.")
                    self._append_result(payload + "\n")
                elif kind == "error":
                    self._finish()
                    self.status.set("El trabajo falló.")
                    self._append_result(payload + "\n")
                    details = payload
                    if "Registro:" not in details:
                        details += "\n\nRevisa también el archivo blender.log de la carpeta del trabajo."
                    messagebox.showerror("Error de generación", details)
        except queue.Empty:
            pass
        self.after(150, self._poll_events)

    def _finish(self):
        self.progress.stop()
        self.start_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        elapsed = time.monotonic() - self._started_at if self._started_at else 0
        self._append_result(f"Tiempo: {elapsed:.1f} s\n")

    def _show_result(self, result):
        self._last_result = result
        self.status.set(f"Trabajo completado: {result['job_id']}")
        self._append_result(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        try:
            with Image.open(result["preview"]) as image:
                image.thumbnail((560, 560))
                self._preview_image = ImageTk.PhotoImage(image.copy())
            self.preview_label.configure(image=self._preview_image, text="")
        except (OSError, KeyError) as exc:
            self.preview_label.configure(text=f"No se pudo mostrar la vista previa: {exc}")
        messagebox.showinfo("Generación completada",
            "Se creó una prenda procedural y se exportaron los formatos solicitados.\n"
            "Revisa la vista previa y las limitaciones descritas en la aplicación.")

    def _append_result(self, text):
        self.result_text.configure(state="normal")
        self.result_text.insert("end", text)
        self.result_text.see("end")
        self.result_text.configure(state="disabled")

    def _save_config(self):
        try:
            config = {"reference": self.reference.get(), "blend": self.blend.get(),
                      "output": self.output.get(), "mode": self.mode.get(),
                      "intensity": float(self.intensity.get())}
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
            self.status.set(f"Configuración guardada: {CONFIG_PATH}")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Configuración", str(exc))

    def _load_config(self):
        if not CONFIG_PATH.is_file():
            return
        try:
            config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            self.reference.set(config.get("reference", ""))
            self.blend.set(config.get("blend", ""))
            self.output.set(config.get("output", str(ROOT / "outputs")))
            self.mode.set(config.get("mode", "oversize"))
            self.intensity.set(float(config.get("intensity", 1.0)))
        except (OSError, ValueError, json.JSONDecodeError):
            self.status.set("No se pudo cargar settings.local.json; se usan valores predeterminados.")

    def _open_output(self):
        path = Path(self.output.get()).expanduser()
        if not path.is_dir():
            messagebox.showwarning("Carpeta no encontrada", "Genera un trabajo o selecciona una carpeta existente.")
            return
        try:
            import os
            if os.name == "nt":
                os.startfile(str(path))
            else:
                messagebox.showinfo("Carpeta de salida", str(path))
        except OSError as exc:
            messagebox.showerror("Carpeta de salida", str(exc))

    def _close(self):
        if self._worker and self._worker.is_alive():
            if messagebox.askyesno("Trabajo activo", "¿Cancelar el trabajo y cerrar la aplicación?"):
                if self._cancel_event:
                    self._cancel_event.set()
                self.destroy()
            return
        self.destroy()


if __name__ == "__main__":
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    ImageTo3DApp().mainloop()
