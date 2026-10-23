"""Interfaz inicial de escritorio para Image to 3D."""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from backend.blender.runner import find_blender
from backend.fitting.modes import FITTING_MODES
from backend.validation.inputs import validate_blend, validate_reference


class ImageTo3DApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image to 3D — Ropa 3D")
        self.geometry("760x500")
        self.minsize(680, 450)
        self.reference = tk.StringVar()
        self.blend = tk.StringVar()
        self.output = tk.StringVar(value=str(Path.cwd() / "outputs"))
        self.mode = tk.StringVar(value="oversize")
        self.status = tk.StringVar(value="Selecciona una referencia y el cuerpo .blend.")
        self._build()

    def _build(self):
        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Image to 3D", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Base inicial. El motor de generación 3D todavía no está conectado.", wraplength=700).pack(anchor="w", pady=(4, 16))
        files = ttk.LabelFrame(frame, text="Entradas", padding=12)
        files.pack(fill="x", pady=5)
        self._row(files, "Imagen / vídeo", self.reference, self._choose_reference, 0)
        self._row(files, "Cuerpo (.blend)", self.blend, self._choose_blend, 1)
        options = ttk.LabelFrame(frame, text="Opciones", padding=12)
        options.pack(fill="x", pady=8)
        ttk.Label(options, text="Modo:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(options, textvariable=self.mode, values=FITTING_MODES, state="readonly", width=16).grid(row=0, column=1, padx=8, sticky="w")
        ttk.Label(options, text="Carpeta de salida:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(options, textvariable=self.output).grid(row=1, column=1, sticky="ew", padx=8, pady=(10, 0))
        ttk.Button(options, text="Elegir…", command=self._choose_output).grid(row=1, column=2, pady=(10, 0))
        options.columnconfigure(1, weight=1)
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=12)
        ttk.Button(actions, text="Validar entradas", command=self._validate).pack(side="left")
        ttk.Button(actions, text="Comprobar Blender", command=self._blender).pack(side="left", padx=8)
        ttk.Button(actions, text="Generar (pendiente)", command=self._pending).pack(side="right")
        ttk.Separator(frame).pack(fill="x", pady=8)
        ttk.Label(frame, textvariable=self.status, wraplength=700).pack(anchor="w")
        ttk.Label(frame, text="El archivo .blend original no se modificará. Esta versión no genera ni exporta geometría.", wraplength=700).pack(anchor="w", pady=(10, 0))

    @staticmethod
    def _row(parent, label, variable, command, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8, pady=5)
        ttk.Button(parent, text="Examinar…", command=command).grid(row=row, column=2, pady=5)
        parent.columnconfigure(1, weight=1)

    def _choose_reference(self):
        path = filedialog.askopenfilename(filetypes=[("Referencias", "*.png *.jpg *.jpeg *.webm"), ("Todos", "*.*")])
        if path:
            self.reference.set(path)

    def _choose_blend(self):
        path = filedialog.askopenfilename(filetypes=[("Blender", "*.blend"), ("Todos", "*.*")])
        if path:
            self.blend.set(path)

    def _choose_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output.set(path)

    def _validate(self):
        errors = []
        try:
            validate_reference(self.reference.get())
        except ValueError as exc:
            errors.append(str(exc))
        try:
            validate_blend(self.blend.get())
        except ValueError as exc:
            errors.append(str(exc))
        if errors:
            self.status.set("Hay entradas que corregir.")
            messagebox.showerror("Validación", "\n".join(errors))
        else:
            self.status.set("Entradas válidas. El motor 3D aún no está implementado.")
            messagebox.showinfo("Validación", "Los archivos superaron las comprobaciones iniciales.")

    def _blender(self):
        executable = find_blender()
        if executable is None:
            messagebox.showwarning("Blender no encontrado", "Instala Blender o define BLENDER_EXECUTABLE con la ruta a blender.exe.")
        else:
            self.status.set(f"Blender encontrado: {executable}")
            messagebox.showinfo("Blender", str(executable))

    def _pending(self):
        messagebox.showinfo("Generación pendiente", "Falta integrar un motor 3D, el ajuste geométrico, el visor y los exportadores.")


if __name__ == "__main__":
    ImageTo3DApp().mainloop()
