# -*- coding: utf-8 -*-
"""
Robot autonomo recolector de basura + manzana urbana estilo Cienaga, Magdalena.
Geometria independiente, jerarquia para Webots, colecciones y camaras.
Unidades: metros. Origen del robot: centro de la huella en el suelo.
Ejes: +X adelante, +Y izquierda, +Z arriba.
"""
import math
import traceback
from pathlib import Path

import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_CANDIDATES = [
    Path(r"c:\Users\cursor-mcp"),
    Path(r"C:\Users\lewis\Documents\Robot_Limpiador_Cienaga"),
]

CHASSIS_L, CHASSIS_W, CHASSIS_H = 1.20, 0.78, 0.38
CHASSIS_Z = 0.28
WHEEL_R, WHEEL_W = 0.16, 0.095
WHEELBASE, TRACK = 0.72, 0.70
BIN_L, BIN_W, BIN_H = 0.62, 0.70, 0.48
ARM_BASE_H = 0.12
SEG1_L, SEG1_T = 0.42, 0.085
SEG2_L, SEG2_T = 0.38, 0.075
GRIP_L, GRIP_W, GRIP_H = 0.17, 0.032, 0.05
GRIP_OPEN = 0.055


def project_dir():
    for p in PROJECT_CANDIDATES:
        try:
            p.mkdir(parents=True, exist_ok=True)
            test = p / ".write_test"
            test.write_text("ok", encoding="utf-8")
            test.unlink()
            return p
        except Exception:
            continue
    return Path.home() / "Robot_Limpiador_Cienaga"


def safe_engine(engine_id):
    try:
        bpy.context.scene.render.engine = engine_id
        return engine_id
    except TypeError:
        return None


def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def clear_scene():
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for datablock in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.curves,
        bpy.data.texts,
    ):
        for item in list(datablock):
            datablock.remove(item)


def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def link_obj(obj, col_name, parent=None, keep_world=False):
    col = collection(col_name)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    if obj.name not in col.objects:
        col.objects.link(obj)
    if parent is not None:
        mw = obj.matrix_world.copy()
        obj.parent = parent
        if keep_world:
            obj.matrix_world = mw
    return obj


def new_mat(name, color, metallic=0.05, roughness=0.45):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgba = (*color, 1.0) if len(color) == 3 else tuple(color)
    for s in bsdf.inputs:
        ident = getattr(s, "identifier", s.name)
        if ident in ("Base Color",) or s.name in ("Base Color", "Color"):
            if s.type == "RGBA":
                s.default_value = rgba
        elif ident == "Metallic" or s.name == "Metallic":
            s.default_value = metallic
        elif ident == "Roughness" or s.name == "Roughness":
            s.default_value = roughness
    mat.diffuse_color = rgba
    return mat


def assign(obj, mat):
    data = getattr(obj, "data", None)
    if data is None or not hasattr(data, "materials"):
        return
    if len(data.materials):
        data.materials[0] = mat
    else:
        data.materials.append(mat)


def empty(name, loc, col="ROBOT", parent=None, size=0.08, keep_world=False):
    bpy.ops.object.empty_add(type="ARROWS", location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.empty_display_size = size
    link_obj(obj, col, parent, keep_world=keep_world)
    return obj


def mesh_obj(name, col, parent=None, keep_world=False):
    obj = bpy.context.active_object
    obj.name = name
    select_only(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    link_obj(obj, col, parent, keep_world=keep_world)
    return obj


def cube(name, size, loc, col, parent=None, mat=None, keep_world=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = mesh_obj(name, col, parent, keep_world=keep_world)
    obj.scale = size
    select_only(obj)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        assign(obj, mat)
    return obj


def cylinder(name, radius, depth, loc, rot, col, parent=None, mat=None, verts=24, keep_world=False):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot
    )
    obj = mesh_obj(name, col, parent, keep_world=keep_world)
    if mat:
        assign(obj, mat)
    return obj


def uv_sphere(name, radius, loc, col, parent=None, mat=None, segs=16, keep_world=False):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius, location=loc, segments=segs, ring_count=max(8, segs // 2)
    )
    obj = mesh_obj(name, col, parent, keep_world=keep_world)
    if mat:
        assign(obj, mat)
    return obj


def cone(name, radius, depth, loc, rot, col, parent=None, mat=None, keep_world=False):
    bpy.ops.mesh.primitive_cone_add(
        radius1=radius, depth=depth, location=loc, rotation=rot, vertices=12
    )
    obj = mesh_obj(name, col, parent, keep_world=keep_world)
    if mat:
        assign(obj, mat)
    return obj


def bevel(obj, width=0.008, segs=2):
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segs
    m.limit_method = "ANGLE"


def hide_export_proxy(obj):
    obj.hide_render = True
    try:
        obj.hide_set(True)
    except Exception:
        obj.hide_viewport = True
    obj["webots_proxy"] = True


def build_robot(root_loc=(0.0, 0.0, 0.0)):
    mats = {
        "black": new_mat("MAT_Robot_Negro", (0.03, 0.03, 0.035), 0.25, 0.38),
        "grey": new_mat("MAT_Robot_Gris", (0.38, 0.40, 0.42), 0.35, 0.32),
        "yellow": new_mat("MAT_Robot_Amarillo", (0.85, 0.62, 0.05), 0.15, 0.35),
        "tire": new_mat("MAT_Neumatico", (0.02, 0.02, 0.02), 0.0, 0.85),
        "rim": new_mat("MAT_Llanta", (0.55, 0.56, 0.58), 0.7, 0.22),
        "metal": new_mat("MAT_Brazo_Metal", (0.12, 0.12, 0.13), 0.75, 0.28),
        "joint": new_mat("MAT_Articulacion", (0.08, 0.08, 0.09), 0.8, 0.2),
        "grip": new_mat("MAT_Pinza", (0.18, 0.18, 0.2), 0.65, 0.3),
        "lens": new_mat("MAT_Lente", (0.05, 0.18, 0.45), 0.4, 0.08),
        "bin": new_mat("MAT_Contenedor", (0.04, 0.045, 0.05), 0.2, 0.4),
        "recycle": new_mat("MAT_Reciclaje", (0.75, 0.78, 0.8), 0.3, 0.25),
        "plastic": new_mat("MAT_Plastico_Sensor", (0.15, 0.16, 0.18), 0.1, 0.35),
    }
    rx, ry, rz = root_loc
    root = empty("Robot_Root", root_loc, "ROBOT", size=0.2)

    chassis_loc = (rx, ry, rz + CHASSIS_Z)
    chasis = cube(
        "Chasis", (CHASSIS_L, CHASSIS_W, CHASSIS_H), chassis_loc, "ROBOT", root, mats["black"]
    )
    bevel(chasis, 0.012, 3)

    cube(
        "Chasis_Banda_Gris",
        (CHASSIS_L * 0.98, CHASSIS_W * 1.02, CHASSIS_H * 0.28),
        (rx, ry, rz + CHASSIS_Z - 0.02),
        "ROBOT",
        chasis,
        mats["grey"],
        keep_world=True,
    )
    for side, name in ((1, "Panel_Amarillo_Izquierdo"), (-1, "Panel_Amarillo_Derecho")):
        cube(
            name,
            (0.42, 0.04, 0.18),
            (rx + 0.12, ry + side * (CHASSIS_W * 0.5 + 0.01), rz + CHASSIS_Z + 0.02),
            "ROBOT",
            chasis,
            mats["yellow"],
            keep_world=True,
        )
    cube(
        "Chasis_Frontal",
        (0.18, CHASSIS_W * 0.72, 0.16),
        (rx + CHASSIS_L * 0.5 + 0.02, ry, rz + CHASSIS_Z - 0.04),
        "ROBOT",
        chasis,
        mats["grey"],
        keep_world=True,
    )
    cube(
        "Parachoques",
        (0.06, CHASSIS_W * 0.78, 0.08),
        (rx + CHASSIS_L * 0.5 + 0.12, ry, rz + 0.16),
        "ROBOT",
        chasis,
        mats["yellow"],
        keep_world=True,
    )

    wheel_x, wheel_y, wheel_z = WHEELBASE / 2.0, TRACK / 2.0, WHEEL_R
    wheel_defs = [
        ("Rueda_Delantera_Derecha", +wheel_x, -wheel_y),
        ("Rueda_Delantera_Izquierda", +wheel_x, +wheel_y),
        ("Rueda_Trasera_Derecha", -wheel_x, -wheel_y),
        ("Rueda_Trasera_Izquierda", -wheel_x, +wheel_y),
    ]
    for name, dx, dy in wheel_defs:
        pivot = empty(f"Pivote_{name}", (rx + dx, ry + dy, rz + wheel_z), "ROBOT", root, 0.06)
        cylinder(
            name, WHEEL_R, WHEEL_W, (0, 0, 0), (math.radians(90), 0, 0),
            "ROBOT", pivot, mats["tire"], verts=28,
        )
        cylinder(
            f"Llanta_{name}", WHEEL_R * 0.62, WHEEL_W * 0.55, (0, 0, 0), (math.radians(90), 0, 0),
            "ROBOT", pivot, mats["rim"], verts=20,
        )
        cylinder(
            f"Cubo_{name}", WHEEL_R * 0.18, WHEEL_W * 0.7, (0, 0, 0), (math.radians(90), 0, 0),
            "ROBOT", pivot, mats["grey"], verts=12,
        )

    bin_x = rx - 0.18
    bin_z = rz + CHASSIS_Z + CHASSIS_H * 0.5 + BIN_H * 0.5 + 0.01
    contenedor = cube(
        "Contenedor_Basura", (BIN_L, BIN_W, BIN_H), (bin_x, ry, bin_z), "ROBOT", chasis, mats["bin"],
        keep_world=True,
    )
    cube(
        "Contenedor_Interior",
        (BIN_L * 0.86, BIN_W * 0.86, BIN_H * 0.72),
        (bin_x, ry, bin_z + 0.04),
        "ROBOT",
        contenedor,
        new_mat("MAT_Interior_Bin", (0.08, 0.09, 0.08), 0.0, 0.7),
        keep_world=True,
    )
    for i, ang in enumerate((0.0, 120.0, 240.0)):
        a = math.radians(ang)
        cylinder(
            f"Simbolo_Reciclaje_{i + 1}",
            0.035, 0.012,
            (bin_x - BIN_L * 0.51, ry + math.sin(a) * 0.07, bin_z + math.cos(a) * 0.07),
            (0, math.radians(90), a),
            "ROBOT", contenedor, mats["recycle"], verts=10, keep_world=True,
        )
    for i, off in enumerate(((-0.08, 0.1, 0.12), (0.05, -0.08, 0.1), (0.0, 0.0, 0.18))):
        uv_sphere(
            f"Residuo_En_Contenedor_{i + 1}",
            0.05 + 0.01 * i,
            (bin_x + off[0], ry + off[1], bin_z + off[2]),
            "ROBOT", contenedor,
            new_mat(f"MAT_ResiduoBin_{i}", (0.55, 0.65 + i * 0.05, 0.7), 0.0, 0.4),
            segs=10, keep_world=True,
        )

    mast_z = bin_z + BIN_H * 0.5 + 0.08
    mast_x = bin_x + 0.12
    mast = cylinder(
        "Mastil_Sensor", 0.035, 0.16, (mast_x, ry, mast_z), (0, 0, 0),
        "SENSORES", chasis, mats["plastic"], verts=16, keep_world=True,
    )
    head = cylinder(
        "Sensor_Camara_Superior", 0.055, 0.07, (mast_x, ry, mast_z + 0.11), (0, 0, 0),
        "SENSORES", mast, mats["black"], verts=16, keep_world=True,
    )
    uv_sphere(
        "Lente_Camara_Superior", 0.032, (mast_x, ry, mast_z + 0.155),
        "SENSORES", head, mats["lens"], segs=12, keep_world=True,
    )
    cylinder(
        "Sensor_Frontal", 0.028, 0.04,
        (rx + CHASSIS_L * 0.5 + 0.14, ry, rz + CHASSIS_Z + 0.08),
        (0, math.radians(90), 0), "SENSORES", chasis, mats["lens"], verts=16, keep_world=True,
    )
    for side, nm in ((0.12, "Sensor_Ultrasonido_Izquierdo"), (-0.12, "Sensor_Ultrasonido_Derecho")):
        cylinder(
            nm, 0.018, 0.03,
            (rx + CHASSIS_L * 0.5 + 0.13, ry + side, rz + CHASSIS_Z + 0.02),
            (0, math.radians(90), 0), "SENSORES", chasis, mats["grey"], verts=12, keep_world=True,
        )

    base_pos = Vector((rx + CHASSIS_L * 0.5 + 0.05, ry, rz + CHASSIS_Z + 0.06))
    pivote_base = empty("Pivote_Brazo_Base", base_pos, "ROBOT", root, 0.07)
    pivote_base.rotation_euler = Euler((0, 0, math.radians(-8)), "XYZ")
    cylinder(
        "Brazo_Base", 0.055, ARM_BASE_H, (0, 0, ARM_BASE_H * 0.35), (0, 0, 0),
        "ROBOT", pivote_base, mats["joint"], verts=16,
    )

    pivote_1 = empty("Pivote_Brazo_1", (0, 0, ARM_BASE_H * 0.85), "ROBOT", pivote_base, 0.06)
    pivote_1.rotation_euler = Euler((0, math.radians(38), 0), "XYZ")
    uv_sphere("Articulacion_1", 0.048, (0, 0, 0), "ROBOT", pivote_1, mats["joint"], 12)
    seg1 = cube(
        "Brazo_Segmento_1", (SEG1_L, SEG1_T, SEG1_T), (SEG1_L * 0.5, 0, 0),
        "ROBOT", pivote_1, mats["metal"],
    )
    bevel(seg1, 0.006, 2)

    pivote_2 = empty("Pivote_Brazo_2", (SEG1_L, 0, 0), "ROBOT", pivote_1, 0.055)
    pivote_2.rotation_euler = Euler((0, math.radians(42), 0), "XYZ")
    uv_sphere("Articulacion_2", 0.042, (0, 0, 0), "ROBOT", pivote_2, mats["joint"], 12)
    seg2 = cube(
        "Brazo_Segmento_2", (SEG2_L, SEG2_T, SEG2_T * 0.9), (SEG2_L * 0.5, 0, 0),
        "ROBOT", pivote_2, mats["metal"],
    )
    bevel(seg2, 0.005, 2)

    pivote_pinza = empty("Pivote_Pinza", (SEG2_L, 0, 0), "ROBOT", pivote_2, 0.05)
    pivote_pinza.rotation_euler = Euler((0, math.radians(20), 0), "XYZ")
    cylinder(
        "Muneca_Pinza", 0.032, 0.05, (0.01, 0, 0), (0, math.radians(90), 0),
        "ROBOT", pivote_pinza, mats["joint"], verts=14,
    )
    piv_l = empty("Pivote_Pinza_Izquierda", (0.04, GRIP_OPEN * 0.5, 0), "ROBOT", pivote_pinza, 0.03)
    piv_r = empty("Pivote_Pinza_Derecha", (0.04, -GRIP_OPEN * 0.5, 0), "ROBOT", pivote_pinza, 0.03)
    piv_l.rotation_euler = Euler((0, 0, math.radians(12)), "XYZ")
    piv_r.rotation_euler = Euler((0, 0, math.radians(-12)), "XYZ")
    pinza_l = cube(
        "Pinza_Izquierda", (GRIP_L, GRIP_W, GRIP_H), (GRIP_L * 0.45, 0, 0),
        "ROBOT", piv_l, mats["grip"],
    )
    pinza_r = cube(
        "Pinza_Derecha", (GRIP_L, GRIP_W, GRIP_H), (GRIP_L * 0.45, 0, 0),
        "ROBOT", piv_r, mats["grip"],
    )
    cube("Yema_Pinza_Izquierda", (0.04, 0.018, GRIP_H * 0.7), (GRIP_L * 0.9, -0.01, 0), "ROBOT", pinza_l, mats["yellow"])
    cube("Yema_Pinza_Derecha", (0.04, 0.018, GRIP_H * 0.7), (GRIP_L * 0.9, 0.01, 0), "ROBOT", pinza_r, mats["yellow"])

    papel = uv_sphere(
        "Papel_En_Pinza", 0.045, (GRIP_L * 0.85, 0, 0), "BASURA", pivote_pinza,
        new_mat("MAT_Papel_Pinza", (0.82, 0.82, 0.78), 0.0, 0.7), segs=10,
    )
    papel.scale = (1.15, 0.85, 0.9)

    webots_root = empty("Robot_Webots_Root", (rx, ry, rz), "ROBOT", None, 0.15)
    webots_root["webots_note"] = "Cuerpos simplificados para exportar a Webots"
    hull = cube(
        "Webots_Chasis_Simple", (CHASSIS_L, CHASSIS_W, CHASSIS_H),
        (rx, ry, rz + CHASSIS_Z), "ROBOT", webots_root, mats["grey"],
    )
    hide_export_proxy(hull)
    for name, dx, dy in wheel_defs:
        w = cylinder(
            f"Webots_{name}", WHEEL_R, WHEEL_W,
            (rx + dx, ry + dy, rz + wheel_z), (math.radians(90), 0, 0),
            "ROBOT", webots_root, mats["tire"], verts=12,
        )
        hide_export_proxy(w)
    return root


def make_palm(name, loc, height=5.5, lean=0.0):
    trunk_mat = new_mat("MAT_Palmera_Tronco", (0.35, 0.22, 0.10), 0.0, 0.7)
    leaf_mat = new_mat("MAT_Palmera_Hoja", (0.12, 0.38, 0.10), 0.0, 0.55)
    root = empty(name, loc, "ENTORNO", size=0.2)
    cylinder(
        f"{name}_Tronco", 0.14, height, (0, 0, height * 0.5), (lean, 0, 0),
        "ENTORNO", root, trunk_mat, verts=10,
    )
    for i in range(8):
        a = i * (math.pi * 2 / 8)
        cone(
            f"{name}_Hoja_{i + 1}", 0.22, 1.8,
            (math.cos(a) * 0.35, math.sin(a) * 0.35, height * 0.92),
            (math.radians(70), 0, a), "ENTORNO", root, leaf_mat,
        )
    return root


def make_tree(name, loc):
    bark = new_mat("MAT_Arbol_Tronco", (0.22, 0.13, 0.07), 0.0, 0.8)
    leaf = new_mat("MAT_Arbol_Copa", (0.15, 0.42, 0.12), 0.0, 0.65)
    root = empty(name, loc, "ENTORNO", size=0.15)
    cylinder(f"{name}_Tronco", 0.16, 2.4, (0, 0, 1.2), (0, 0, 0), "ENTORNO", root, bark, 8)
    uv_sphere(f"{name}_Copa", 1.35, (0, 0, 3.1), "ENTORNO", root, leaf, 12)
    uv_sphere(f"{name}_Copa2", 0.95, (0.5, -0.2, 3.4), "ENTORNO", root, leaf, 10)
    return root


def make_house(name, loc, size, facade, roof_col, yaw=0):
    sx, sy, sz = size
    wall = new_mat(f"MAT_{name}_Muro", facade, 0.0, 0.62)
    roof_m = new_mat(f"MAT_{name}_Teja", roof_col, 0.0, 0.55)
    wood = new_mat("MAT_Madera_Casa", (0.28, 0.16, 0.08), 0.0, 0.55)
    glass = new_mat("MAT_Vidrio", (0.15, 0.2, 0.25), 0.1, 0.12)
    white = new_mat("MAT_Marco", (0.9, 0.9, 0.88), 0.0, 0.4)
    root = empty(name, loc, "ENTORNO", size=0.3)
    root.rotation_euler = Euler((0, 0, yaw), "XYZ")
    cube(f"{name}_Cuerpo", (sx, sy, sz), (0, 0, sz * 0.5), "ENTORNO", root, wall)
    roof = cube(
        f"{name}_Techo", (sx * 1.12, sy * 1.12, 0.12), (0, 0, sz + 0.18),
        "ENTORNO", root, roof_m,
    )
    roof.rotation_euler = Euler((math.radians(18), 0, 0), "XYZ")
    cube(f"{name}_Cumbrera", (sx * 1.05, 0.08, 0.08), (0, 0, sz + 0.42), "ENTORNO", root, roof_m)
    cube(f"{name}_Puerta", (0.04, 0.9, 2.05), (sx * 0.5 + 0.02, 0.15, 1.05), "ENTORNO", root, wood)
    cube(f"{name}_Ventana_1", (0.05, 0.7, 0.85), (sx * 0.5 + 0.02, -sy * 0.22, 1.55), "ENTORNO", root, glass)
    cube(f"{name}_Marco_1", (0.03, 0.78, 0.95), (sx * 0.5 + 0.01, -sy * 0.22, 1.55), "ENTORNO", root, white)
    cube(f"{name}_Ventana_2", (0.05, 0.55, 0.7), (sx * 0.5 + 0.02, sy * 0.28, 1.7), "ENTORNO", root, glass)
    return root


def make_lamp(name, loc):
    metal = new_mat("MAT_Poste", (0.25, 0.25, 0.26), 0.6, 0.35)
    yellow = new_mat("MAT_Poste_Franja", (0.75, 0.65, 0.1), 0.1, 0.4)
    black = new_mat("MAT_Poste_Negro", (0.05, 0.05, 0.05), 0.2, 0.4)
    lamp_m = new_mat("MAT_Luz_Poste", (1, 0.95, 0.8), 0.0, 0.3)
    root = empty(name, loc, "ENTORNO", size=0.1)
    cylinder(f"{name}_Fuste", 0.08, 5.4, (0, 0, 2.7), (0, 0, 0), "ENTORNO", root, metal, 10)
    cube(f"{name}_Franja", (0.18, 0.18, 0.35), (0, 0, 1.15), "ENTORNO", root, yellow)
    cube(f"{name}_Franja2", (0.18, 0.18, 0.18), (0, 0, 0.55), "ENTORNO", root, black)
    cube(f"{name}_Brazo", (0.9, 0.07, 0.07), (0.4, 0, 5.25), "ENTORNO", root, metal)
    uv_sphere(f"{name}_Lampara", 0.14, (0.85, 0, 5.1), "ENTORNO", root, lamp_m, 10)
    light_data = bpy.data.lights.new(f"{name}_Light", "POINT")
    light_data.energy = 80
    light_data.color = (1.0, 0.95, 0.85)
    light_obj = bpy.data.objects.new(f"{name}_Luz", light_data)
    collection("ENTORNO").objects.link(light_obj)
    light_obj.parent = root
    light_obj.location = (0.85, 0, 5.05)
    return root


def make_curb(name, loc, size):
    conc = new_mat("MAT_Anden", (0.55, 0.52, 0.48), 0.0, 0.75)
    return cube(name, size, loc, "ENTORNO", None, conc)


def build_environment():
    asphalt = new_mat("MAT_Asfalto", (0.12, 0.12, 0.125), 0.0, 0.92)
    sand = new_mat("MAT_Arena", (0.62, 0.52, 0.32), 0.0, 0.85)
    water = new_mat("MAT_Mar", (0.08, 0.28, 0.42), 0.3, 0.15)
    hill = new_mat("MAT_Colina", (0.22, 0.38, 0.16), 0.0, 0.7)
    paint = new_mat("MAT_Pintura_Via", (0.85, 0.82, 0.55), 0.0, 0.4)

    cube("Calle_Asfalto", (48, 8.2, 0.08), (14, 0, -0.04), "ENTORNO", None, asphalt)
    for i in range(12):
        cube(f"Linea_Central_{i}", (1.2, 0.12, 0.01), (i * 3.5 - 4, 0, 0.005), "ENTORNO", None, paint)
    make_curb("Anden_Izquierdo", (14, 5.35, 0.08), (48, 2.4, 0.16))
    make_curb("Anden_Derecho", (14, -5.35, 0.08), (48, 2.4, 0.16))
    make_curb("Bordillo_Izq", (14, 4.18, 0.12), (48, 0.18, 0.24))
    make_curb("Bordillo_Der", (14, -4.18, 0.12), (48, 0.18, 0.24))

    facades_n = [
        (0.18, 0.42, 0.72), (0.85, 0.78, 0.22), (0.75, 0.15, 0.12),
        (0.95, 0.92, 0.82), (0.22, 0.55, 0.28), (0.9, 0.55, 0.18),
    ]
    facades_s = [
        (0.25, 0.55, 0.82), (0.82, 0.7, 0.25), (0.92, 0.9, 0.75),
        (0.7, 0.18, 0.16), (0.2, 0.45, 0.55), (0.95, 0.85, 0.55),
    ]
    roofs = [
        (0.55, 0.28, 0.18), (0.62, 0.32, 0.16), (0.48, 0.22, 0.14),
        (0.7, 0.35, 0.2), (0.5, 0.25, 0.15), (0.58, 0.3, 0.17),
    ]
    for i in range(6):
        make_house(
            f"Casa_Norte_{i + 1}", (i * 7.2 - 2.0, 8.6, 0),
            (6.4, 5.2, 3.4 + (i % 3) * 0.25), facades_n[i], roofs[i],
            yaw=math.radians(-90),
        )
        make_house(
            f"Casa_Sur_{i + 1}", (i * 7.2 - 2.0, -8.6, 0),
            (6.4, 5.4, 3.5), facades_s[i], roofs[i],
            yaw=math.radians(90),
        )

    cube(
        "Muro_Mural_Cienaga", (0.22, 7.2, 3.6), (4.8, -8.55, 1.85),
        "ENTORNO", None, new_mat("MAT_Mural_Fondo", (0.55, 0.72, 0.78), 0.0, 0.7),
    )
    bpy.ops.object.text_add(location=(4.95, -8.55, 2.55))
    txt = bpy.context.active_object
    txt.name = "Texto_Mural_Cienaga"
    txt.data.body = "100\nCIENAGA\nMAGDALENA"
    txt.data.extrude = 0.03
    txt.data.size = 0.42
    txt.data.align_x = "CENTER"
    txt.data.align_y = "CENTER"
    txt.rotation_euler = Euler((math.radians(90), 0, math.radians(90)), "XYZ")
    link_obj(txt, "ENTORNO")
    assign(txt, new_mat("MAT_Mural_Texto", (0.12, 0.22, 0.55), 0.0, 0.35))
    wave_m = new_mat("MAT_Mural_Olas", (0.2, 0.45, 0.7), 0.05, 0.4)
    for i in range(3):
        cube(
            f"Mural_Ola_{i + 1}", (0.04, 2.2 - i * 0.3, 0.06),
            (4.95, -8.55, 1.15 - i * 0.16), "ENTORNO", None, wave_m,
        )
    cube("Reja_Metalica", (0.08, 2.4, 2.4), (8.2, -6.9, 1.25), "ENTORNO", None,
         new_mat("MAT_Reja", (0.08, 0.08, 0.09), 0.7, 0.3))

    make_palm("Palmera_1", (3.2, 6.4, 0), height=6.2)
    make_palm("Palmera_2", (18.5, 6.6, 0), height=5.4, lean=math.radians(4))
    make_palm("Palmera_3", (11.0, -6.5, 0), height=5.8)
    make_palm("Palmera_4", (26.0, -6.3, 0), height=6.5)
    make_tree("Arbol_Tropical_1", (-4.5, 6.2, 0))
    make_tree("Arbol_Tropical_2", (22.0, 6.3, 0))
    make_tree("Arbol_Tropical_3", (-5.0, -6.4, 0))
    for i, x in enumerate((-3, 8, 19, 30)):
        make_lamp(f"Poste_Luz_{i + 1}", (x, 4.05, 0))
        make_lamp(f"Poste_Luz_Sur_{i + 1}", (x + 2.5, -4.05, 0))

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=9, location=(42, -8, -2))
    h1 = mesh_obj("Colina_1", "ENTORNO")
    h1.scale = (1.6, 1.4, 0.55)
    select_only(h1)
    bpy.ops.object.transform_apply(scale=True)
    assign(h1, hill)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=7, location=(46, 6, -1.5))
    h2 = mesh_obj("Colina_2", "ENTORNO")
    h2.scale = (1.4, 1.2, 0.5)
    select_only(h2)
    bpy.ops.object.transform_apply(scale=True)
    assign(h2, hill)
    cube("Mar_Caribe", (18, 40, 0.2), (48, 0, -0.3), "ENTORNO", None, water)
    cube("Playa", (8, 22, 0.15), (38, 0, -0.12), "ENTORNO", None, sand)


def bottle(name, loc, rot_z=0.4, color=(0.75, 0.85, 0.9)):
    mat = new_mat(f"MAT_{name}", color, 0.05, 0.2)
    cap_m = new_mat("MAT_Tapa_Botella", (0.1, 0.25, 0.75), 0.1, 0.35)
    root = empty(name + "_Root", loc, "BASURA", size=0.04)
    root.rotation_euler = Euler((math.radians(90), 0, rot_z), "XYZ")
    cylinder(name, 0.032, 0.22, (0, 0, 0.0), (0, 0, 0), "BASURA", root, mat, 12)
    cylinder(name + "_Cuello", 0.014, 0.05, (0, 0, 0.13), (0, 0, 0), "BASURA", root, mat, 10)
    cylinder(name + "_Tapa", 0.016, 0.018, (0, 0, 0.16), (0, 0, 0), "BASURA", root, cap_m, 10)
    return root


def can(name, loc, color=(0.75, 0.18, 0.16)):
    mat = new_mat(f"MAT_{name}", color, 0.65, 0.28)
    root = empty(name + "_Root", loc, "BASURA", size=0.04)
    root.rotation_euler = Euler((math.radians(82), 0.2, 0.3), "XYZ")
    cylinder(name, 0.033, 0.12, (0, 0, 0), (0, 0, 0), "BASURA", root, mat, 14)
    return root


def crumpled(name, loc, scale, color):
    obj = uv_sphere(name, 0.07, loc, "BASURA", None, new_mat(f"MAT_{name}", color, 0.0, 0.65), 8)
    obj.scale = scale
    return obj


def bag(name, loc):
    mat = new_mat("MAT_Bolsa", (0.04, 0.04, 0.045), 0.0, 0.55)
    root = empty(name + "_Root", loc, "BASURA", size=0.08)
    uv_sphere(name, 0.22, (0, 0, 0.18), "BASURA", root, mat, 10)
    cone(name + "_Nudo", 0.06, 0.16, (0, 0, 0.42), (0, 0, 0), "BASURA", root, mat)
    return root


def cardboard(name, loc):
    obj = cube(name, (0.38, 0.28, 0.04), loc, "BASURA", None, new_mat("MAT_Carton", (0.55, 0.38, 0.18), 0.0, 0.8))
    obj.rotation_euler = Euler((0.15, 0.05, 0.6), "XYZ")
    return obj


def build_trash():
    bottle("Botella_Plastica_1", (1.55, 0.22, 0.035), 0.5)
    bottle("Botella_Plastica_2", (2.4, -0.85, 0.035), -0.7, (0.2, 0.45, 0.75))
    bottle("Botella_Plastica_3", (3.6, 1.4, 0.035), 1.2, (0.85, 0.85, 0.8))
    can("Lata_1", (1.95, -0.35, 0.035))
    can("Lata_2", (4.1, 0.6, 0.035), (0.2, 0.35, 0.7))
    crumpled("Papel_Arrugado_1", (1.35, -0.15, 0.04), (1.1, 0.8, 0.7), (0.86, 0.85, 0.8))
    crumpled("Papel_Arrugado_2", (2.8, 0.9, 0.04), (0.9, 1.2, 0.7), (0.9, 0.88, 0.7))
    crumpled("Vaso_Plastico", (3.1, -1.5, 0.04), (0.7, 0.7, 0.5), (0.9, 0.9, 0.92))
    bag("Bolsa_Basura_1", (-2.2, 3.55, 0.0))
    cardboard("Caja_Carton_1", (0.9, 1.55, 0.03))
    bottle("Botella_Anden", (2.1, 4.6, 0.18), 0.2)
    can("Lata_Anden", (5.4, 4.5, 0.18), (0.9, 0.7, 0.1))
    crumpled("Papel_Anden", (6.8, -4.5, 0.18), (1, 1, 0.6), (0.8, 0.8, 0.75))


def setup_world_lights():
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg:
        for s in bg.inputs:
            ident = getattr(s, "identifier", s.name)
            if ident == "Color" or s.name == "Color":
                s.default_value = (0.55, 0.72, 0.95, 1)
            if ident == "Strength" or s.name == "Strength":
                s.default_value = 0.85
    sun = bpy.data.lights.new("Sol_Caribe", "SUN")
    sun.energy = 6.5
    sun.color = (1.0, 0.95, 0.85)
    sun_obj = bpy.data.objects.new("Sol_Caribe", sun)
    collection("ENTORNO").objects.link(sun_obj)
    sun_obj.rotation_euler = Euler((math.radians(42), math.radians(15), math.radians(35)), "XYZ")
    fill = bpy.data.lights.new("Fill_Ambiente", "AREA")
    fill.energy = 250
    fill.size = 12
    fill.color = (0.7, 0.82, 1.0)
    fill_obj = bpy.data.objects.new("Luz_Relleno", fill)
    collection("ENTORNO").objects.link(fill_obj)
    fill_obj.location = (6, -8, 8)
    fill_obj.rotation_euler = Euler((math.radians(60), 0, math.radians(20)), "XYZ")


def setup_cameras():
    cam_data = bpy.data.cameras.new("Camara_Tres_Cuartos")
    cam = bpy.data.objects.new("Camara_Tres_Cuartos", cam_data)
    collection("CAMARAS").objects.link(cam)
    cam.location = (2.85, -4.15, 1.55)
    cam_data.lens = 35
    cam_data.clip_end = 200
    bpy.context.scene.camera = cam

    cam2_data = bpy.data.cameras.new("Camara_Superior")
    cam2 = bpy.data.objects.new("Camara_Superior", cam2_data)
    collection("CAMARAS").objects.link(cam2)
    cam2.location = (8.0, 0.0, 28.0)
    cam2.rotation_euler = Euler((0, 0, 0), "XYZ")
    cam2_data.lens = 28
    cam2_data.clip_end = 200
    cam2_data.type = "ORTHO"
    cam2_data.ortho_scale = 22

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.35, 0.05, 0.42))
    target = bpy.context.active_object
    target.name = "Camara_Objetivo"
    link_obj(target, "CAMARAS")
    con = cam.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"


def set_render(render_dir: Path):
    scene = bpy.context.scene
    for cand in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        if safe_engine(cand):
            break
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.filepath = str(render_dir / "vista_tres_cuartos")
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    try:
        scene.eevee.taa_render_samples = 24
    except Exception:
        pass
    scene.view_settings.view_transform = "Standard"


def unique_blend_path(path: Path) -> Path:
    if not path.exists():
        return path
    i = 1
    while True:
        alt = path.with_name(f"{path.stem}_{i}{path.suffix}")
        if not alt.exists():
            return alt
        i += 1


def write_docs(base: Path, out_blend: Path):
    text = f"""# Robot recolector de Cienaga — dimensiones y export Webots

Archivo Blender: `{out_blend}`
Script: `scripts/cienaga_robot_scene.py`
Unidades: **metros**. Origen `Robot_Root` en el suelo, centro de la huella.
Ejes: **+X adelante**, **+Y izquierda**, **+Z arriba**.

## Colecciones
- ROBOT — chasis, ruedas, brazo, pinza, version simplificada
- SENSORES — camara superior, sensor frontal, ultrasonidos
- ENTORNO — calle, casas, palmeras, postes, mar
- BASURA — residuos individuales (y papel en pinza)
- CAMARAS — Camara_Tres_Cuartos (activa), Camara_Superior (orto)

## Dimensiones aproximadas
| Componente | Tamano (m) | Notas Webots |
|---|---|---|
| Chasis | {CHASSIS_L:.2f} L x {CHASSIS_W:.2f} W x {CHASSIS_H:.2f} H | Centro Z = {CHASSIS_Z:.2f}. Cuerpo base. |
| Ruedas | radio {WHEEL_R:.2f}, ancho {WHEEL_W:.2f} | 4 objetos. Eje de giro **Y local** de cada `Pivote_Rueda_*`. |
| Distancia entre ejes | {WHEELBASE:.2f} | X entre ejes delantero/trasero |
| Trocha | {TRACK:.2f} | Y entre centros de rueda |
| Contenedor_Basura | {BIN_L:.2f} x {BIN_W:.2f} x {BIN_H:.2f} | Trasero superior, hijo de Chasis |
| Brazo_Base | h={ARM_BASE_H:.2f} | Yaw en `Pivote_Brazo_Base` (eje Z) |
| Brazo_Segmento_1 | largo {SEG1_L:.2f} | Pitch en `Pivote_Brazo_1` (eje Y) |
| Brazo_Segmento_2 | largo {SEG2_L:.2f} | Pitch en `Pivote_Brazo_2` (eje Y) |
| Pinza | largo {GRIP_L:.2f} | Apertura: rot Z de `Pivote_Pinza_Izquierda/Derecha` |

## Motores sugeridos (Webots)
1. `motor_rueda_DI/DD/TI/TD` — HingeJoint en cada `Pivote_Rueda_*`, eje (0,1,0)
2. `motor_brazo_yaw` — HingeJoint `Pivote_Brazo_Base`, eje (0,0,1)
3. `motor_brazo_hombro` — HingeJoint `Pivote_Brazo_1`, eje (0,1,0)
4. `motor_brazo_codo` — HingeJoint `Pivote_Brazo_2`, eje (0,1,0)
5. `motor_pinza` — dos HingeJoint simetricos en `Pivote_Pinza_Izquierda/Derecha`

## Version simplificada
`Robot_Webots_Root` contiene `Webots_Chasis_Simple` y `Webots_Rueda_*` (ocultos).
Mallas de baja densidad para collision/export.

Export: glTF u OBJ **por objeto**, sin join. Los Empty `Pivote_*` marcan origenes de articulacion.

## Residuos (objetos separados)
Botella_Plastica_1/2/3, Lata_1/2, Papel_Arrugado_1/2, Vaso_Plastico,
Bolsa_Basura_1, Caja_Carton_1, Botella_Anden, Lata_Anden, Papel_Anden, Papel_En_Pinza.
"""
    (base / "DIMENSIONES_WEBOTS.md").write_text(text, encoding="utf-8")
    print("DOC", base / "DIMENSIONES_WEBOTS.md")


def verify():
    required = [
        "Chasis", "Rueda_Delantera_Izquierda", "Rueda_Delantera_Derecha",
        "Rueda_Trasera_Izquierda", "Rueda_Trasera_Derecha", "Brazo_Base",
        "Brazo_Segmento_1", "Brazo_Segmento_2", "Pinza_Izquierda", "Pinza_Derecha",
        "Sensor_Frontal", "Contenedor_Basura", "Camara_Tres_Cuartos", "Camara_Superior",
        "Calle_Asfalto", "Botella_Plastica_1", "Lata_1", "Papel_En_Pinza", "Robot_Webots_Root",
    ]
    cols = ["ROBOT", "ENTORNO", "BASURA", "SENSORES", "CAMARAS"]
    missing = [n for n in required if n not in bpy.data.objects]
    missing_c = [n for n in cols if n not in bpy.data.collections]
    print("OBJECTS", len(bpy.data.objects))
    print("MISSING_OBJECTS", missing)
    print("MISSING_COLLECTIONS", missing_c)
    print("COLLECTIONS", [c.name for c in bpy.data.collections])
    for n in ("Robot_Root", "Pivote_Brazo_Base", "Pivote_Pinza"):
        o = bpy.data.objects.get(n)
        if o:
            print(f"CHILDREN {n}: {[c.name for c in o.children]}")
    w = bpy.data.objects.get("Rueda_Delantera_Izquierda")
    if w:
        print("WHEEL_DIM", [round(v, 4) for v in w.dimensions])
        print("WHEEL_PARENT", w.parent.name if w.parent else None)
    return missing, missing_c


def render_views(render_dir: Path):
    render_dir.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.camera = bpy.data.objects["Camara_Tres_Cuartos"]
    scene.render.filepath = str(render_dir / "vista_tres_cuartos.png")
    bpy.ops.render.render(write_still=True)
    scene.camera = bpy.data.objects["Camara_Superior"]
    scene.render.filepath = str(render_dir / "vista_superior.png")
    bpy.ops.render.render(write_still=True)
    scene.camera = bpy.data.objects["Camara_Tres_Cuartos"]
    print("RENDERS_OK")


def main():
    base = project_dir()
    (base / "scripts").mkdir(parents=True, exist_ok=True)
    render_dir = base / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    print("PROJECT_DIR", base)

    clear_scene()
    for name in ("ROBOT", "ENTORNO", "BASURA", "SENSORES", "CAMARAS"):
        collection(name)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "METERS"
    bpy.context.scene.unit_settings.scale_length = 1.0

    build_environment()
    build_robot((0.0, 0.0, 0.0))
    build_trash()
    setup_world_lights()
    setup_cameras()
    set_render(render_dir)

    missing, missing_c = verify()
    # Overwrite the file produced by this same generator in this project.
    out = base / "Robot_Limpiador_Cienaga.blend"
    write_docs(base, out)
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    print("SAVED", out)
    try:
        render_views(render_dir)
    except Exception:
        print("RENDER_ERROR")
        traceback.print_exc()
    missing2, _ = verify()
    print("DONE", "ok" if not missing2 else missing2)


if __name__ == "__main__":
    main()
