"""Diseño explícito de prenda y malla de previsualización independiente de Blender."""
from math import cos, sin, pi

GARMENT_TYPES = ("camisa", "vestido", "falda", "pantalon", "short")
BACK_TYPES = ("cerrada", "espalda_abierta")


def normalize_design(design=None):
    design = dict(design or {})
    garment = str(design.get("type", "camisa")).lower()
    if garment not in GARMENT_TYPES:
        raise ValueError(f"Tipo de prenda no válido: {garment}")
    back = str(design.get("back", "cerrada")).lower()
    if back not in BACK_TYPES:
        raise ValueError(f"Diseño de espalda no válido: {back}")
    symmetry = True if garment in ("falda", "pantalon", "short") else bool(design.get("symmetry", True))
    if garment not in ("vestido", "camisa"):
        back = "cerrada"
    return {"type": garment, "symmetry": symmetry, "back": back}


def preview_rings(design=None, rotation=0.0, width=1.0, height=2.0, depth=0.42):
    """Devuelve segmentos 3D para una vista volumétrica ligera en Tkinter."""
    cfg = normalize_design(design)
    kind = cfg["type"]
    if kind == "camisa":
        rings = [(0.56, .30, .20), (.70, .39, .22), (.82, .46, .24), (.93, .37, .20), (1., .25, .17)]
    elif kind == "vestido":
        rings = [(.04, .62, .34), (.20, .52, .30), (.40, .32, .24), (.56, .30, .20), (.70, .39, .22), (.82, .46, .24), (.93, .37, .20), (1., .25, .17)]
    elif kind == "falda":
        rings = [(.05, .52, .31), (.35, .34, .25), (.55, .25, .20)]
    else:
        hem = .05 if kind == "pantalon" else .24
        rings = [(.56, .28, .20), (.36, .31, .22), (hem, .15, .17, -1, .08), (hem, .15, .17, 1, .08)]
    segments, count = [], 28
    for ring in rings:
        z, rx, ry = ring[:3]
        offset = ring[3] * ring[4] if len(ring) > 4 else 0
        points = [(rx*cos(2*pi*i/count)+offset, ry*sin(2*pi*i/count), z) for i in range(count+1)]
        segments.extend((points[i], points[i+1]) for i in range(count))
    for ring in range(len(rings)-1):
        a, b = rings[ring], rings[ring+1]
        if len(a) > 3 or len(b) > 3:
            continue
        for angle in (0, pi/2, pi, 3*pi/2):
            segments.append(((a[1]*cos(angle), a[2]*sin(angle), a[0]),
                             (b[1]*cos(angle), b[2]*sin(angle), b[0])))
    return segments


def project_preview_segments(segments, width, height, angle=0.5):
    """Proyección ortográfica 3D -> 2D, sin librerías externas."""
    projected = []
    scale = min(width / 2.7, height / 2.4)
    ca, sa = cos(angle), sin(angle)
    for a, b in segments:
        pair = []
        for x, y, z in (a, b):
            xr, yr = x*ca-y*sa, x*sa+y*ca
            pair.append((width/2+xr*scale, height*.88-z*scale+yr*scale*.28))
        projected.append(pair)
    return projected
