# Image to 3D — Generación y ajuste de ropa 3D

Base de Requisitos_Proyecto_Image_to_3D.docx v1.0 (2026-10-23).

## Estado
Base modular para Windows: interfaz inicial, validación, ciclo de vida de trabajos, detección de Blender, pruebas y documentación. La generación mediante IA, ajuste geométrico, visor 3D y exportación real están pendientes y no se simulan como implementados.

## Entorno
Windows 10/11 de 64 bits (provisional), Python 3.11 de 64 bits y Blender instalado por separado. Aunque el equipo tenga Python 3.14.6 y 3.10, recomiendo instalar Python 3.11 para esta base: evita depender de ruedas binarias aún no verificadas en 3.14 y no iniciar el proyecto sobre Python 3.10, cuyo soporte de seguridad termina en octubre de 2026. GPU de referencia: NVIDIA RTX 2050, sin garantía de que cualquier modelo quepa en VRAM.

En PowerShell, desde D:\Mios\ImagenTo3D_Clothes:
    py -3.11 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-dev.txt
    python -m pytest
    python app.py

Si PowerShell bloquea la activación: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass. Comprueba que python -c "import sys; print(sys.executable)" apunta dentro de .venv.

## Estructura
- app.py: interfaz de escritorio inicial (Tkinter).
- backend/validation: validación de imágenes, WEBM y BLEND.
- backend/jobs: estados e identificadores.
- backend/generation: punto de integración pendiente.
- backend/fitting: modos oversize y ceñido.
- backend/blender: detección de Blender.
- backend/export: formatos previstos BLEND, GLB y OBJ.
- config: límites configurables.
- tests y docs: pruebas y documentación.

El archivo BLEND original no debe modificarse. No enviar archivos a servicios externos sin decisión explícita. Mantener main estable y usar ramas feature/<tema> o fix/<tema>. No versionar entornos, modelos, temporales, logs ni resultados.
