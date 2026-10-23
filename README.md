# Image to 3D — Generación local de ropa 3D

Aplicación de escritorio para Windows que recibe una referencia PNG/JPG/JPEG o WEBM y una escena corporal BLEND, ejecuta Blender en segundo plano, crea una prenda paramétrica inicial y genera archivos BLEND, GLB y OBJ con previsualización.

## Alcance real de esta versión

Esta rama convierte la base en un flujo local ejecutable de extremo a extremo. La malla de ropa es una plantilla procedural tipo camiseta/túnica colocada según las dimensiones generales de la escena. La referencia aporta un color medio y, si es WEBM, se toma un fotograma representativo. **No es un modelo de IA que reconstruya automáticamente el diseño, patrón, pliegues o silueta exactos de cualquier prenda fotografiada.** El ajuste oversize/ceñido cambia las dimensiones de la plantilla; no simula tela ni garantiza ajuste anatómico perfecto. La posición depende de la escala y orientación del cuerpo en el archivo Blender.

No se envían imágenes ni escenas a servicios externos. El archivo BLEND de entrada se usa como fuente y se guarda una copia nueva en la carpeta del trabajo; no se sobrescribe el original.

## Requisitos

- Windows 10/11 de 64 bits.
- Python 3.10 o superior, con tkinter incluido en la instalación de Windows.
- Blender instalado localmente. Los operadores de exportación dependen de la versión instalada.
- RAM/VRAM suficiente para la escena. La RTX 2050 es un objetivo de referencia, no una garantía de que cualquier escena quepa en memoria.

## Instalación PowerShell

Desde D:\\Mios\\ImagenTo3D_Clothes:

    py -0p
    py -3.10 -m venv .venv
    .\\.venv\\Scripts\\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-dev.txt
    python -m pytest

Para usar Python 3.14, crea el entorno con py -3.14 -m venv .venv. Pip seleccionará ruedas compatibles disponibles; si falla una dependencia binaria, prueba Python 3.10 o instala una versión compatible del paquete.

Configura Blender en la misma sesión PowerShell (ajusta la ruta):

    $env:BLENDER_EXECUTABLE = "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe"
    python app.py

También puedes añadir la carpeta de Blender a PATH. No se instala Blender mediante pip.

## Uso

1. Abre la aplicación con python app.py.
2. Selecciona una referencia PNG/JPG/JPEG o WEBM.
3. Selecciona el cuerpo de destino BLEND.
4. Elige oversize o ceñido y una intensidad de 0 a 2.
5. Elige la carpeta de salida y pulsa **Generar y exportar**.
6. Revisa la previsualización y los archivos de la carpeta del trabajo.

Cada ejecución crea una carpeta outputs/image_to_3d_<id>/ con los formatos exportados, preview.png, job.json, blender.log y la referencia reducida usada para extraer el color. Los trabajos no sobrescriben trabajos anteriores.

## Estructura

- app.py: interfaz Tkinter, trabajo en hilo separado, cancelación y vista previa.
- backend/validation: validación de entradas.
- backend/generation: coordinación local, color de referencia y metadatos.
- backend/blender/worker.py: malla procedural, material, cámara, render y exportación.
- backend/fitting: parámetros de ajuste.
- backend/export: validación de formatos.
- backend/jobs: ciclo de vida de trabajos.
- tests: pruebas unitarias que no requieren abrir Blender.

## Diagnóstico

- Si Blender no aparece, define BLENDER_EXECUTABLE con la ruta completa a blender.exe.
- Si un exportador no está disponible, revisa blender.log en la carpeta del trabajo.
- Si la prenda aparece desplazada o fuera de escala, la escena puede tener el cuerpo rotado, no centrado, o incluir mallas auxiliares que alteran los límites globales.
- Los tests unitarios no sustituyen una prueba de integración con un archivo BLEND real en tu PC.
