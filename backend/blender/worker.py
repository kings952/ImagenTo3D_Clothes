"""Script ejecutado dentro de Blender: prenda paramétrica, render y exportación."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_config():
    if "--" not in sys.argv:
        raise RuntimeError("Falta la ruta del archivo de configuración después de --.")
    args = sys.argv[sys.argv.index("--") + 1:]
    if not args:
        raise RuntimeError("No se recibió el archivo de configuración.")
    return json.loads(Path(args[0]).read_text(encoding="utf-8"))


def world_bounds(objects):
    points = []
    for obj in objects:
        if obj.type == "MESH":
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        return Vector((-0.5, -0.4, 0.0)), Vector((0.5, 0.4, 1.8))
    return (Vector(tuple(min(p[i] for p in points) for i in range(3))),
            Vector(tuple(max(p[i] for p in points) for i in range(3))))


def make_material(rgb):
    material = bpy.data.materials.new("ImageTo3D_ReferenceColor")
    material.diffuse_color = (*rgb, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.78
    return material


def mesh_object(name, vertices, faces, material):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    solid = obj.modifiers.new("FabricThickness", "SOLIDIFY")
    solid.thickness = 0.006
    bevel = obj.modifiers.new("SoftEdges", "BEVEL")
    bevel.width = 0.003
    bevel.segments = 2
    return obj


def create_torso(material, cx, cy, z0, z1, width, depth, scale, back_open=False):
    segments = 40
    profiles = [(0.0, 0.78), (0.10, 0.83), (0.25, 0.90), (0.48, 0.98),
                (0.70, 1.0), (0.88, 0.94), (1.0, 0.72)]
    vertices, faces = [], []
    for t, factor in profiles:
        rx = width * factor * scale / 2
        ry = depth * (0.82 + 0.18 * factor) * scale / 2
        z = z0 + (z1 - z0) * t
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            vertices.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle), z))
    for ring in range(len(profiles) - 1):
        for i in range(segments):
            a = ring * segments + i
            b = ring * segments + (i + 1) % segments
            c = (ring + 1) * segments + (i + 1) % segments
            d = (ring + 1) * segments + i
            faces.append((a, b, c, d))
    return mesh_object("Garment_Torso", vertices, faces, material)


def create_sleeve(material, start, end, radius_y, radius_z, scale, name):
    segments, rings = 24, 5
    start, end = Vector(start), Vector(end)
    axis = (end - start).normalized()
    basis_y = Vector((0, 1, 0))
    basis_y = (basis_y - axis * basis_y.dot(axis)).normalized()
    basis_n = axis.cross(basis_y).normalized()
    vertices, faces = [], []
    for ring in range(rings):
        t = ring / (rings - 1)
        center = start.lerp(end, t)
        taper = (1.0 - 0.22 * t) * scale
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            point = center + basis_y * (math.cos(angle) * radius_y * taper)
            point += basis_n * (math.sin(angle) * radius_z * taper)
            vertices.append(tuple(point))
    for ring in range(rings - 1):
        for i in range(segments):
            a = ring * segments + i
            b = ring * segments + (i + 1) % segments
            c = (ring + 1) * segments + (i + 1) % segments
            d = (ring + 1) * segments + i
            faces.append((a, b, c, d))
    return mesh_object(name, vertices, faces, material)


def create_skirt(material, cx, cy, z0, z1, width, depth, scale, name="Garment_Skirt", asymmetric=False):
    segments = 40
    profiles = [(0.0, 0.72), (0.08, 0.78), (0.32, 0.92), (0.68, 1.0), (1.0, 1.08)]
    vertices, faces = [], []
    for t, factor in profiles:
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            vertices.append((cx + width * factor * scale * math.cos(angle) / 2,
                             cy + depth * factor * scale * math.sin(angle) / 2, z0 + (z1-z0)*t))
    for ring in range(len(profiles)-1):
        for i in range(segments):
            a, b = ring*segments+i, ring*segments+(i+1)%segments
            c, d = (ring+1)*segments+(i+1)%segments, (ring+1)*segments+i
            faces.append((a,b,c,d))
    return mesh_object(name, vertices, faces, material)


def create_trouser_legs(material, cx, cy, z0, z1, width, depth, scale, short=False):
    objects = []
    for side, label in [(-1, "L"), (1, "R")]:
        leg_width = width * (0.27 if short else 0.23)
        top, bottom = z1, z0 + (z1-z0) * (0.42 if short else 0.02)
        xcenter, segments = cx + side*width*0.16, 24
        vertices, faces = [], []
        for t, factor in [(0.0,1.0),(0.12,.96),(.88,.82),(1.0,.80)]:
            z = top + (bottom-top)*t
            for i in range(segments):
                angle = 2*math.pi*i/segments
                vertices.append((xcenter+leg_width*factor*scale*math.cos(angle)/2,
                                 cy+depth*.24*scale*math.sin(angle), z))
        for ring in range(3):
            for i in range(segments):
                a,b=ring*segments+i,ring*segments+(i+1)%segments
                c,d=(ring+1)*segments+(i+1)%segments,(ring+1)*segments+i
                faces.append((a,b,c,d))
        objects.append(mesh_object("Garment_Leg_"+label, vertices, faces, material))
    return objects


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def create_preview(bounds_min, bounds_max, output_path):
    scene = bpy.context.scene
    center = (bounds_min + bounds_max) * 0.5
    extent = max((bounds_max - bounds_min).length, 1.0)
    camera_data = bpy.data.cameras.new("ImageTo3D_PreviewCamera")
    camera = bpy.data.objects.new("ImageTo3D_PreviewCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = center + Vector((extent * 1.35, -extent * 2.3, extent * 0.9))
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = extent * 1.45
    aim(camera, center)
    scene.camera = camera
    for name, offset, energy, size in [
        ("ImageTo3D_Key", (extent, -extent, extent * 1.2), 1000, extent),
        ("ImageTo3D_Fill", (-extent, -extent * 0.3, extent * 0.5), 650, extent * 0.8),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.shape, data.size = energy, "DISK", size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = center + Vector(offset)
        aim(light, center)
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output_path)
    if scene.world is not None:
        scene.world.color = (0.08, 0.08, 0.08)
    scene.render.film_transparent = False
    bpy.ops.render.render(write_still=True)


def main():
    config = parse_config()
    output = Path(config["output_dir"])
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    bounds_min, bounds_max = world_bounds(mesh_objects)
    size = bounds_max - bounds_min
    height = max(size.z, 0.5)
    width = max(size.x, height * 0.24)
    depth = max(size.y, height * 0.12)
    cx, cy = (bounds_min.x + bounds_max.x) / 2, (bounds_min.y + bounds_max.y) / 2
    z0, z1 = bounds_min.z + height * 0.39, bounds_min.z + height * 0.72
    fitting = config["fitting"]\n    design = config.get("garment_design", {"type": "camisa", "symmetry": True, "back": "cerrada"})\n    garment_type = design.get("type", "camisa")
    intensity = float(fitting.get("intensity", 1.0))
    scale = (1.0 + 0.28 * intensity) if fitting["mode"] == "oversize" else max(0.68, 1.0 - 0.16 * intensity)
    garment_width = width * (0.58 if garment_type in ("camisa", "vestido") else 0.46)
    garment_depth = depth * 0.88
    material = make_material(config["reference_color"])
    if garment_type in ("camisa", "vestido"):
        torso_z1 = z0 + (z1-z0) * (0.64 if garment_type == "vestido" else 1.0)
        create_torso(material, cx, cy, z0, torso_z1, garment_width, garment_depth, scale,
                     back_open=(design.get("back") == "espalda_abierta"))
        if garment_type == "vestido":
            create_skirt(material, cx, cy, z0-height*.25, z0, garment_width*1.6,
                         garment_depth*1.25, scale, "Garment_Dress_Skirt", asymmetric=(not design.get("symmetry", True)))
        else:
            shoulder_z = z0 + (z1-z0)*.82
            shoulder_x = garment_width*scale*.36
            sleeve_length = max(width*.25, height*.09)*scale
            radius_y, radius_z = max(depth*.10,height*.035), max(height*.045,.025)
            for side, label in [(-1,"L"),(1,"R")]:
                start=(cx+side*shoulder_x,cy,shoulder_z)
                sleeve_factor = 1.0 if design.get("symmetry", True) or side > 0 else 0.72\n                end=(cx+side*(shoulder_x+sleeve_length*sleeve_factor),cy,shoulder_z-height*.06)
                create_sleeve(material,start,end,radius_y,radius_z,scale,"Garment_Sleeve_"+label)
    elif garment_type == "falda":
        create_skirt(material,cx,cy,z0-height*.18,z1,garment_width*1.5,
                     garment_depth*1.25,scale)
    else:
        create_trouser_legs(material,cx,cy,z0-height*.18,z1,garment_width,
                            garment_depth,scale,short=(garment_type=="short"))

    # La escena de salida incluye cámara y luces para que el BLEND se pueda inspeccionar.
    all_min, all_max = world_bounds([obj for obj in bpy.context.scene.objects if obj.type == "MESH"])
    create_preview(all_min, all_max, output / "preview.png")
    # Empaqueta recursos externos cuando sea posible antes de crear la copia editable.
    try:
        bpy.ops.file.pack_all()
    except RuntimeError:
        pass

    # Solo los objetos de la View Layer activa se pueden seleccionar/exportar.
    # scene.objects puede incluir mallas de colecciones excluidas, como rigs enlazados.
    view_layer_names = {obj.name for obj in bpy.context.view_layer.objects}
    garment_objects = [obj for obj in bpy.context.scene.objects
                       if obj.name.startswith("Garment_") and obj.name in view_layer_names]
    export_objects = [obj for obj in bpy.context.scene.objects
                      if obj.type == "MESH" and not obj.name.startswith("Garment_")
                      and obj.name in view_layer_names]
    for obj in list(bpy.context.selected_objects):
        try:
            obj.select_set(False)
        except RuntimeError:
            pass
    for obj in export_objects + garment_objects:
        try:
            obj.select_set(True)
        except RuntimeError as exc:
            print(f"IMAGE_TO_3D_WARNING: se omite {obj.name}: {exc}")
    active = next((obj for obj in garment_objects if obj.name in view_layer_names), None)
    if active is not None:
        bpy.context.view_layer.objects.active = active
    if not garment_objects:
        raise RuntimeError("No se crearon objetos Garment_. Revisa la generación procedural.")
    for extension in config["export_formats"]:
        target = output / ("garment" + extension)
        if extension == ".blend":
            bpy.ops.wm.save_as_mainfile(filepath=str(target))
        elif extension == ".glb":
            bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB", use_selection=True)
        elif extension == ".obj":
            if hasattr(bpy.ops.wm, "obj_export"):
                bpy.ops.wm.obj_export(filepath=str(target), export_selected_objects=True)
            else:
                bpy.ops.export_scene.obj(filepath=str(target), use_selection=True)
    print("IMAGE_TO_3D_DONE")


if __name__ == "__main__":
    main()
