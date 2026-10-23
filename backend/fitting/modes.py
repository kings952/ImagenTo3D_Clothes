"""Validación de los modos de ajuste; aún no deforma geometría."""
FITTING_MODES = ("oversize", "ceñido")


def validate_fitting_parameters(mode, intensity=1.0):
    if mode not in FITTING_MODES:
        raise ValueError(f"Modo inválido: {mode}.")
    if not 0.0 <= intensity <= 2.0:
        raise ValueError("La intensidad debe estar entre 0.0 y 2.0.")
    return {"mode": mode, "intensity": float(intensity)}
