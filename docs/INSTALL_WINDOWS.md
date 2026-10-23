# Instalación en Windows

## Requisitos

- Windows 10/11 de 64 bits.
- Python 3.10+ de 64 bits con tkinter.
- Blender instalado localmente; no se instala con pip.
- Espacio libre para temporales y formatos exportados.

## Entorno virtual

Desde la raíz del repositorio:

    py -0p
    py -3.10 -m venv .venv
    .\\.venv\\Scripts\\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-dev.txt
    python -m pytest

Para Python 3.14, sustituye la creación por py -3.14 -m venv .venv. Las dependencias permiten que pip elija ruedas compatibles; si una rueda no existe o falla, prueba Python 3.10.

Si PowerShell bloquea la activación, ejecuta Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass. Comprueba que python -c "import sys; print(sys.executable)" apunta a .venv\\Scripts\\python.exe.

## Configurar Blender

Ajusta la ruta a tu instalación y ejecuta en la misma sesión:

    $env:BLENDER_EXECUTABLE = "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe"
    python app.py

La ruta es solo un ejemplo. También se acepta Blender en PATH.

## Verificación

1. Ejecuta python -m pytest.
2. Ejecuta python app.py.
3. Pulsa Comprobar Blender.
4. Selecciona una escena BLEND de cuerpo que puedas abrir manualmente y una imagen pequeña.
5. Genera un trabajo y revisa los archivos, preview.png y blender.log.

El archivo fuente no se sobrescribe. Si el archivo BLEND no abre en Blender, el proceso debe fallar y registrar el error; la validación de extensión no garantiza la integridad del archivo.
