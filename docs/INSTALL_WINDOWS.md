# Instalación en Windows

Requisitos iniciales: Windows 10/11 de 64 bits (provisional), Python 3.11 de 64 bits y Blender instalado por separado. La GPU objetivo de referencia es NVIDIA RTX 2050. Aunque el equipo tenga Python 3.14.6 y 3.10, recomendamos instalar Python 3.11: no se ha verificado la compatibilidad de todas las ruedas binarias con Python 3.14 y el soporte de seguridad de Python 3.10 termina en octubre de 2026.

En PowerShell, desde la raíz del repositorio:

    py -0p
    py -3.11 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python --version
    python -c "import sys; print(sys.executable)"
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-dev.txt
    python -m pytest
    python app.py

Confirma que la ruta de Python apunte dentro de .venv. Si PowerShell bloquea la activación, ejecuta Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass y vuelve a activar. Si py -3.11 no existe, instala Python 3.11 de 64 bits y confirma su registro con py -0p.

Para detectar Blender, define BLENDER_EXECUTABLE con la ruta completa a blender.exe o añade Blender a PATH. Ejemplo de sesión:

    $env:BLENDER_EXECUTABLE = "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
    python app.py

La ruta anterior es solo un ejemplo. La generación 3D y exportación no están implementadas en esta base.
