"""Contrato explícito del motor de generación 3D pendiente."""


class GenerationNotConfiguredError(RuntimeError):
    pass


def generate_garment(*, reference_path, blend_path, output_dir, fitting):
    raise GenerationNotConfiguredError(
        "No hay motor 3D configurado. Integra y valida un método antes de generar."
    )
