# Arquitectura y flujo implementado

1. Tkinter valida entradas y lanza un hilo de trabajo para no bloquear la interfaz.
2. El servicio valida la imagen/vídeo y el archivo BLEND, crea una carpeta aislada y obtiene el color medio de la referencia. Para WEBM usa un fotograma central (retrocede al primero si falla).
3. Blender se ejecuta en modo background y abre el archivo de destino sin sobrescribirlo.
4. El script Blender estima la caja envolvente de las mallas, crea una camiseta/túnica paramétrica con mangas, configura cámara y luces, renderiza una vista previa y exporta formatos seleccionados.
5. El servicio verifica que los archivos existan y escribe job.json con entradas, parámetros, estado y salidas.
6. La interfaz muestra el render y permite abrir la carpeta. La cancelación termina el proceso Blender y conserva logs para diagnóstico.

## Módulos

- app.py: interfaz, hilo de trabajo, estado, cancelación y visor PNG.
- backend/validation/inputs.py: PNG/JPG/JPEG, WEBM y BLEND.
- backend/generation/service.py: coordinación, color de referencia y metadatos.
- backend/blender/runner.py: detección, subprocess y cancelación.
- backend/blender/worker.py: malla procedural y exportación mediante bpy.
- backend/fitting/modes.py: parámetros oversize y ceñido.
- backend/export/formats.py: validación y descubrimiento de salidas.
- backend/jobs/manager.py: estados de trabajos.
- tests: pruebas unitarias que no requieren abrir Blender.

## Límites conocidos

No se utiliza un modelo de IA ni se reconstruyen patrones, costuras, pliegues, texturas UV o el diseño exacto de la ropa. La referencia solo proporciona un color medio. La estimación del torso usa la caja envolvente global de la escena; escenas con múltiples objetos, rotación o ejes diferentes pueden producir una ubicación incorrecta. El ajuste escala una plantilla; no sustituye la simulación de tela ni un retarget anatómico. La exportación depende de los operadores disponibles en la versión local de Blender.

## Seguridad y datos

Todo el procesamiento ocurre localmente. No se cargan referencias ni archivos BLEND a servicios externos. Las salidas y logs quedan en carpetas por trabajo. El archivo fuente no se guarda encima.
