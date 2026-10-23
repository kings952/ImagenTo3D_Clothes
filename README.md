# Image to 3D — Generación y ajuste de ropa 3D

Base del proyecto conforme a **Requisitos_Proyecto_Image_to_3D.docx v1.0 (2026-10-23)**.

## Estado
Estructura inicial y entorno reproducible para Windows. La generación de geometría mediante IA es una etapa pendiente: no se afirma que esté implementada hasta seleccionar y validar un método compatible con el hardware objetivo.

## Requisitos
- Windows 10/11 de 64 bits (mínimo provisional).
- Python 3.11 de 64 bits.
- Blender instalado por separado; la versión soportada se debe fijar tras verificar automatización y exportadores.
- GPU NVIDIA RTX 2050 como objetivo de referencia, no garantía de compatibilidad con cualquier modelo.

## Inicio rápido (PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt
python app.py
```
Si PowerShell bloquea la activación: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

## Diseño
- `frontend/`: interfaz local.
- `backend/validation/`: entradas y parámetros.
- `backend/generation/`: adaptador de generación (pendiente de seleccionar modelo).
- `backend/fitting/`: modos oversize/ceñido.
- `backend/blender/`: detección y automatización de Blender.
- `backend/export/`: salidas BLEND, GLB y OBJ.
- `backend/jobs/`: ciclo de vida de trabajos.
- `config/`: límites locales configurables.
- `tests/`: pruebas.
- `docs/`: arquitectura, instalación y decisiones pendientes.

Lee `docs/INSTALL_WINDOWS.md`, `docs/ARCHITECTURE.md` y `docs/DECISIONS.md` antes de implementar la generación.

## Principios
El archivo .blend de entrada no se modifica; las salidas son nuevas. Las entradas se validan, los trabajos tienen estado e identificador, los temporales se aíslan por trabajo y se limpian con seguridad. No se envían archivos a servicios externos sin una decisión explícita e información al usuario.

## Git
Mantener `main` como base estable. Trabajar en ramas `feature/<tema>` o `fix/<tema>`, probar y revisar antes de integrar. No versionar entornos virtuales, modelos, temporales, logs ni resultados generados.
