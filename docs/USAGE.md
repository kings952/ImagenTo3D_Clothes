# Uso

1. Activa el entorno virtual y ejecuta python app.py.
2. Selecciona una referencia PNG/JPG/JPEG o WEBM.
3. Selecciona el archivo BLEND que contiene el cuerpo.
4. Elige oversize o ceñido, ajusta la intensidad y selecciona una carpeta de salida.
5. Pulsa Generar y exportar. Blender se ejecuta en segundo plano.
6. Revisa el render y las rutas del panel derecho.
7. Cambia el modo o intensidad y vuelve a generar; cada trabajo se guarda en una carpeta diferente.

La referencia aporta el color medio, no la geometría de la ropa. La prenda es una plantilla paramétrica inicial, no una reconstrucción mediante IA. Revisa blender.log si un formato no se exporta.


## Definir la estructura de la prenda

- Selecciona camisa, vestido, falda, pantalón o short.
- Camisas y vestidos pueden ser simétricos o asimétricos; la espalda abierta se permite en estas dos categorías.
- Falda, pantalón y short fuerzan simetría y espalda cerrada.
- Arrastra horizontalmente en el visor conceptual para girar la previsualización antes de ejecutar Blender.
- El visor no usa el cuerpo .blend. Sirve para comprobar el volumen elegido, pero no sustituye un patrón de costura ni una reconstrucción exacta desde múltiples fotografías.
