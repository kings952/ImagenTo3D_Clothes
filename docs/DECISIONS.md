# Decisiones y límites técnicos

Decisiones implementadas para hacer verificable la primera versión local:
- Procesamiento local; no se suben archivos a APIs externas.
- Interfaz Tkinter.
- Blender como proceso independiente en modo background.
- Salidas BLEND, GLB, OBJ y preview.png.
- Plantilla de camiseta/túnica paramétrica como primer generador ejecutable.
- Los modos oversize y ceñido ajustan el volumen de la plantilla.
- El color medio de la referencia se utiliza como material base.

Decisiones que siguen abiertas porque el documento de requisitos no las especifica:
- Modelo de IA para reconstruir prendas desde imágenes y licencia/peso de sus checkpoints.
- Categorías de ropa prioritarias más allá de la plantilla inicial.
- Malla estática o prenda riggeada para animación.
- Criterios de calidad visual y precisión de ajuste.
- Versiones exactas de Blender y sistema operativo objetivo definitivo.
- Límites de tiempo, RAM y VRAM para escenas grandes.

No se debe describir esta plantilla procedural como generación IA completa. Integrar un modelo real requiere seleccionar uno, verificar licencia, memoria y resultados en el hardware objetivo, y añadir pruebas de integración.
