"""Parámetros reproducibles para el ajuste geométrico inicial."""
FITTING_MODES = ("oversize", "ceñido")


def validate_fitting_parameters(mode, intensity=1.0):
    if mode not in FITTING_MODES:
        raise ValueError(f"Modo inválido: {mode}.")
    try:
        intensity = float(intensity)
    except (TypeError, ValueError) as exc:
        raise ValueError("La intensidad debe ser numérica.") from exc
    if not 0.0 <= intensity <= 2.0:
        raise ValueError("La intensidad debe estar entre 0.0 y 2.0.")
    return {"mode": mode, "intensity": intensity}


def garment_scale(parameters):
    params = validate_fitting_parameters(parameters["mode"], parameters.get("intensity", 1.0))
    if params["mode"] == "oversize":
        return 1.0 + 0.28 * params["intensity"]
    return max(0.68, 1.0 - 0.16 * params["intensity"])
