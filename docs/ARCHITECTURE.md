# Arquitectura inicial

- app.py: interfaz Tkinter, selectores de referencia/BLEND, modo de ajuste y mensajes.
- backend/validation: valida extensión, existencia, tamaño y legibilidad de imágenes y WEBM. El BLEND se valida por existencia, extensión y tamaño; su integridad interna requiere Blender.
- backend/jobs: UUID, fechas, entradas, parámetros, salidas, errores y transiciones de estado; el almacén inicial es en memoria.
- backend/generation: contrato explícito que falla si no hay motor configurado.
- backend/fitting: validación de oversize y ceñido; no deforma mallas todavía.
- backend/blender: detección del ejecutable; automatización de escenas pendiente.
- backend/export: formatos previstos .blend, .glb y .obj; exportadores reales pendientes.

Principios: no modificar el BLEND original; aislar temporales por trabajo; limitar resolución y cantidad de fotogramas; ejecutar tareas largas fuera del hilo de interfaz; permitir cancelación segura; no enviar archivos a servicios externos sin decisión explícita; no afirmar funciones como terminadas sin pruebas.

Flujo futuro: seleccionar entradas, validar, crear trabajo, preparar temporales, extraer fotogramas por lotes, generar geometría, ajustar, previsualizar, exportar, registrar resultados y limpiar temporales.
