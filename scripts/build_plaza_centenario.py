# -*- coding: utf-8 -*-
"""
Generador 3D de la Plaza del Centenario de Cienaga, Magdalena
Incluye:
- El Templete neoclasico central (columnas, podio circular escalonado, entablamento, balaustrada y cupula)
- La Iglesia San Juan Bautista (fachada colonial, torre campanario, cupula monumental, nave y pergola)
- La Plaza del Centenario (rotonda, jardineras circulares, senderos, bancas, faroles, palmeras y arboles)
- Entorno urbano colonial (edificaciones republicanas con balcones)
- Sierra Nevada de Santa Marta en el horizonte
- Residuos interactivos alrededor del Templete y la plaza
- Robot limpiador con traccion 4WD, brazo 4 GDL y tolva
"""

import math
import traceback
from pathlib import Path

import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_DIR = Path(r"C:\Users\lewis\Documents\Robot_Limpiador_Cienaga")
MESH_DIR = PROJECT_DIR / "meshes"
MESH_DIR.mkdir(parents=True, exist_ok=True)

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

def clear_scene():
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for datablock in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(datablock):
            datablock.remove(item)

def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

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
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = mesh_obj(name, col, parent, keep_world=keep_world)
    if mat:
        assign(obj, mat)
    return obj

def uv_sphere(name, radius, loc, col, parent=None, mat=None, segs=16, keep_world=False):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=segs, ring_count=max(8, segs // 2))
    obj = mesh_obj(name, col, parent, keep_world=keep_world)
    if mat:
        assign(obj, mat)
    return obj

def cone(name, radius, depth, loc, rot, col, parent=None, mat=None, keep_world=False):
    bpy.ops.mesh.primitive_cone_add(radius1=radius, depth=depth, location=loc, rotation=rot, vertices=16)
    obj = mesh_obj(name, col, parent, keep_world=keep_world)
    if mat:
        assign(obj, mat)
    return obj

# -------------------------------------------------------------
# 1. EL TEMPLETE DE CIENAGA (Monumento Neoclásico Central)
# -------------------------------------------------------------
def build_templete(center=(16.0, 0.0, 0.0)):
    cx, cy, cz = center
    root = empty("Templete_Root", center, "ENTORNO", size=0.5)
    
    white = new_mat("MAT_Templete_Blanco", (0.94, 0.94, 0.92), 0.02, 0.28)
    marble = new_mat("MAT_Templete_Piso", (0.88, 0.86, 0.82), 0.05, 0.35)
    gold = new_mat("MAT_Templete_Ornamental", (0.78, 0.65, 0.22), 0.6, 0.25)
    roof_m = new_mat("MAT_Templete_Techo", (0.90, 0.90, 0.88), 0.05, 0.3)

    # Podio escalonado circular (4 niveles de escalones)
    cylinder("Templete_Escalon_1", 5.6, 0.16, (cx, cy, cz + 0.08), (0,0,0), "ENTORNO", root, white, verts=36)
    cylinder("Templete_Escalon_2", 5.1, 0.16, (cx, cy, cz + 0.24), (0,0,0), "ENTORNO", root, white, verts=36)
    cylinder("Templete_Escalon_3", 4.6, 0.16, (cx, cy, cz + 0.40), (0,0,0), "ENTORNO", root, white, verts=36)
    cylinder("Templete_Plataforma", 4.1, 0.12, (cx, cy, cz + 0.54), (0,0,0), "ENTORNO", root, marble, verts=36)

    # Anillo de 8 Columnas Neoclásicas
    num_cols = 8
    radius_ring = 3.3
    col_h = 3.6
    base_z = cz + 0.60
    
    for i in range(num_cols):
        ang = i * (2 * math.pi / num_cols)
        px = cx + radius_ring * math.cos(ang)
        py = cy + radius_ring * math.sin(ang)
        
        # Base plinto
        cube(f"Templete_Col_Base_{i+1}", (0.42, 0.42, 0.22), (px, py, base_z + 0.11), "ENTORNO", root, white)
        # Fuste de la columna cilíndrica
        cylinder(f"Templete_Col_Fuste_{i+1}", 0.16, col_h, (px, py, base_z + 0.22 + col_h * 0.5), (0,0,0), "ENTORNO", root, white, verts=20)
        # Capitel moldurado
        cube(f"Templete_Col_Capitel_{i+1}", (0.46, 0.46, 0.24), (px, py, base_z + 0.22 + col_h + 0.12), "ENTORNO", root, white)

    top_z = base_z + 0.22 + col_h + 0.24
    
    # Entablamento circular superior (Arquitrabe y friso)
    cylinder("Templete_Entablamento", 3.75, 0.45, (cx, cy, top_z + 0.22), (0,0,0), "ENTORNO", root, white, verts=36)
    cylinder("Templete_Cornisa", 4.0, 0.14, (cx, cy, top_z + 0.48), (0,0,0), "ENTORNO", root, white, verts=36)
    
    # Balaustrada perimetral ornamental superior
    cylinder("Templete_Balaustrada_Base", 3.85, 0.10, (cx, cy, top_z + 0.60), (0,0,0), "ENTORNO", root, white, verts=36)
    for i in range(24):
        ang = i * (2 * math.pi / 24)
        bx = cx + 3.82 * math.cos(ang)
        by = cy + 3.82 * math.sin(ang)
        cylinder(f"Templete_Balaustre_{i+1}", 0.05, 0.55, (bx, by, top_z + 0.90), (0,0,0), "ENTORNO", root, white, verts=8)
    cylinder("Templete_Pasamanos", 3.88, 0.08, (cx, cy, top_z + 1.20), (0,0,0), "ENTORNO", root, white, verts=36)

    # Cúpula / Techo rebajado con linterna
    cylinder("Templete_Cupula_Tambor", 3.2, 0.35, (cx, cy, top_z + 0.68), (0,0,0), "ENTORNO", root, white, verts=32)
    dome = uv_sphere("Templete_Cupula", 3.2, (cx, cy, top_z + 0.60), "ENTORNO", root, roof_m, segs=32)
    dome.scale = (1.0, 1.0, 0.45)
    select_only(dome)
    bpy.ops.object.transform_apply(scale=True)
    
    # Linterna y pináculo decorativo en la cima
    cylinder("Templete_Linterna", 0.45, 0.70, (cx, cy, top_z + 2.3), (0,0,0), "ENTORNO", root, white, verts=16)
    cone("Templete_Pinaculo", 0.35, 0.85, (cx, cy, top_z + 2.9), (0,0,0), "ENTORNO", root, gold)

    return root

# -------------------------------------------------------------
# 2. IGLESIA SAN JUAN BAUTISTA DE CIENAGA
# -------------------------------------------------------------
def build_church(pos=(38.0, 4.0, 0.0)):
    ix, iy, iz = pos
    root = empty("Iglesia_Root", pos, "ENTORNO", size=0.5)

    white = new_mat("MAT_Iglesia_Blanco", (0.95, 0.95, 0.93), 0.02, 0.35)
    tiles = new_mat("MAT_Iglesia_Tejas", (0.68, 0.24, 0.14), 0.02, 0.65)
    doors = new_mat("MAT_Iglesia_Madera", (0.28, 0.16, 0.08), 0.02, 0.55)
    cupola_m = new_mat("MAT_Iglesia_Cupula", (0.92, 0.92, 0.90), 0.05, 0.3)
    bronze = new_mat("MAT_Campana", (0.45, 0.35, 0.18), 0.8, 0.25)

    # Nave central principal
    cube("Iglesia_Nave_Cuerpo", (26.0, 12.0, 9.0), (ix + 13.0, iy, iz + 4.5), "ENTORNO", root, white)
    roof_nave = cube("Iglesia_Nave_Techo", (26.8, 12.8, 0.25), (ix + 13.0, iy, iz + 10.4), "ENTORNO", root, tiles)
    roof_nave.rotation_euler = Euler((0, math.radians(16), 0), "XYZ")

    # Fachada Frontal (hacia la plaza)
    cube("Iglesia_Frontispicio", (1.2, 13.0, 11.5), (ix, iy, iz + 5.75), "ENTORNO", root, white)
    # Frontón triangular superior
    cone("Iglesia_Fronton", 6.8, 2.8, (ix, iy, iz + 12.8), (0, math.radians(90), math.radians(90)), "ENTORNO", root, white)
    # Gran Portón de Entrada en Arco
    cube("Iglesia_Porton_Marco", (0.3, 3.2, 5.2), (ix - 0.2, iy, iz + 2.6), "ENTORNO", root, white)
    cube("Iglesia_Porton_Puertas", (0.15, 2.7, 4.8), (ix - 0.22, iy, iz + 2.4), "ENTORNO", root, doors)
    # Ventana circular (Rosetón / Óculo coral)
    cylinder("Iglesia_Oculo", 0.95, 0.4, (ix - 0.15, iy, iz + 7.8), (0, math.radians(90), 0), "ENTORNO", root, doors, verts=24)
    cylinder("Iglesia_Oculo_Marco", 1.25, 0.35, (ix - 0.12, iy, iz + 7.8), (0, math.radians(90), 0), "ENTORNO", root, white, verts=24)

    # Gran Torre Campanario (Lateral derecha, vista frontal)
    tx, ty = ix + 1.2, iy - 8.2
    cube("Iglesia_Torre_Base", (5.5, 5.5, 12.0), (tx, ty, iz + 6.0), "ENTORNO", root, white)
    cube("Iglesia_Torre_Cuerpo2", (5.0, 5.0, 4.5), (tx, ty, iz + 14.25), "ENTORNO", root, white)
    cube("Iglesia_Torre_Campanario", (4.5, 4.5, 4.2), (tx, ty, iz + 18.6), "ENTORNO", root, white)
    # Campana de bronce visible en el vano
    cylinder("Iglesia_Campana", 0.55, 0.85, (tx - 0.2, ty, iz + 18.5), (0,0,0), "ENTORNO", root, bronze, verts=16)
    # Remate piramidal de la torre con cruz
    cone("Iglesia_Torre_Capitel", 2.8, 4.0, (tx, ty, iz + 22.7), (0,0,0), "ENTORNO", root, white)
    cube("Iglesia_Torre_Cruz_V", (0.1, 0.1, 1.4), (tx, ty, iz + 25.2), "ENTORNO", root, bronze)
    cube("Iglesia_Torre_Cruz_H", (0.1, 0.8, 0.1), (tx, ty, iz + 25.3), "ENTORNO", root, bronze)

    # Monumental Cúpula y Crucero (Lateral izquierda / trasera, visible en la foto aérea)
    cx, cy = ix + 18.0, iy + 6.5
    cube("Iglesia_Crucero_Muro", (9.0, 6.0, 9.5), (cx, cy, iz + 4.75), "ENTORNO", root, white)
    # Tambor octogonal de la cúpula
    cylinder("Iglesia_Cupula_Tambor", 4.2, 3.2, (cx, cy, iz + 11.0), (0,0,0), "ENTORNO", root, white, verts=16)
    # Media esfera de la cúpula
    c_dome = uv_sphere("Iglesia_Cupula_Esfera", 4.3, (cx, cy, iz + 12.6), "ENTORNO", root, cupola_m, segs=28)
    c_dome.scale = (1.0, 1.0, 0.95)
    select_only(c_dome)
    bpy.ops.object.transform_apply(scale=True)
    # Linterna en la cúpula
    cylinder("Iglesia_Cupula_Linterna", 0.8, 1.6, (cx, cy, iz + 17.2), (0,0,0), "ENTORNO", root, white, verts=12)
    cone("Iglesia_Cupula_Pinaculo", 0.5, 0.9, (cx, cy, iz + 18.4), (0,0,0), "ENTORNO", root, bronze)

    # Pérgola blanca lateral visible en la foto aérea (a la derecha de la iglesia)
    per_x, per_y = ix + 4.0, iy - 14.0
    for pi in range(5):
        cylinder(f"Pergola_Columna_{pi+1}", 0.12, 3.8, (per_x + pi * 3.5, per_y, iz + 1.9), (0,0,0), "ENTORNO", root, white, verts=10)
        cylinder(f"Pergola_Columna_B_{pi+1}", 0.12, 3.8, (per_x + pi * 3.5, per_y - 4.5, iz + 1.9), (0,0,0), "ENTORNO", root, white, verts=10)
    cube("Pergola_Techo", (16.0, 5.2, 0.15), (per_x + 7.0, per_y - 2.25, iz + 3.85), "ENTORNO", root, white)

    return root

# -------------------------------------------------------------
# 3. LA PLAZA DEL CENTENARIO (Parque, Senderos, Jardines y Bancas)
# -------------------------------------------------------------
def build_plaza_centenario(templete_center=(16.0, 0.0, 0.0)):
    tcx, tcy, tcz = templete_center
    root = empty("Plaza_Root", templete_center, "ENTORNO", size=0.5)

    pave = new_mat("MAT_Plaza_Adoquin", (0.72, 0.70, 0.66), 0.0, 0.75)
    walkway = new_mat("MAT_Plaza_Losas", (0.80, 0.78, 0.74), 0.0, 0.65)
    grass = new_mat("MAT_Plaza_Cesped", (0.16, 0.42, 0.12), 0.0, 0.85)
    flowers = new_mat("MAT_Plaza_Flores", (0.82, 0.22, 0.38), 0.0, 0.6)
    curb_m = new_mat("MAT_Bordillo_Plaza", (0.62, 0.60, 0.58), 0.0, 0.6)
    wood = new_mat("MAT_Madera_Banca", (0.35, 0.20, 0.10), 0.0, 0.6)
    iron = new_mat("MAT_Hierro_Negro", (0.04, 0.04, 0.05), 0.6, 0.3)

    # Gran Explanada de la Plaza (52m x 42m)
    cube("Plaza_Piso_Principal", (52.0, 42.0, 0.08), (20.0, 0.0, -0.04), "ENTORNO", root, pave)

    # Rotonda circular pavimentada alrededor del Templete
    cylinder("Plaza_Rotonda_Templete", 14.5, 0.04, (tcx, tcy, 0.005), (0,0,0), "ENTORNO", root, walkway, verts=48)

    # Anillo ajardinado concéntrico con césped y flores alrededor del Templete
    # Parterre circular entre radio 7.0m y 9.5m
    for i in range(16):
        ang = i * (2 * math.pi / 16) + (math.pi / 16)
        jx = tcx + 8.2 * math.cos(ang)
        jy = tcy + 8.2 * math.sin(ang)
        cube(f"Jardin_Parterre_{i+1}", (2.2, 1.8, 0.18), (jx, jy, 0.09), "ENTORNO", root, grass)
        # Arbustos con flores ornamentales caribeñas
        uv_sphere(f"Arbusto_Flores_{i+1}", 0.45, (jx, jy, 0.28), "ENTORNO", root, flowers, segs=10)

    # 4 Senderos principales que convergen en la rotonda
    cube("Sendero_Norte", (4.2, 14.0, 0.05), (tcx, 18.0, 0.01), "ENTORNO", root, walkway)
    cube("Sendero_Sur", (4.2, 14.0, 0.05), (tcx, -18.0, 0.01), "ENTORNO", root, walkway)
    cube("Sendero_Este_Iglesia", (18.0, 4.5, 0.05), (tcx + 16.0, 0.0, 0.01), "ENTORNO", root, walkway)
    cube("Sendero_Oeste_Entrada", (16.0, 4.5, 0.05), (tcx - 14.0, 0.0, 0.01), "ENTORNO", root, walkway)

    # Bancas coloniales de parque (10 bancas distribuidas armónicamente)
    bench_positions = [
        (tcx + 10.5, tcy + 5.5, 0.0, math.radians(-30)),
        (tcx + 10.5, tcy - 5.5, 0.0, math.radians(30)),
        (tcx - 10.5, tcy + 5.5, 0.0, math.radians(-150)),
        (tcx - 10.5, tcy - 5.5, 0.0, math.radians(150)),
        (tcx + 5.5, tcy + 10.5, 0.0, math.radians(-60)),
        (tcx - 5.5, tcy + 10.5, 0.0, math.radians(-120)),
        (tcx + 5.5, tcy - 10.5, 0.0, math.radians(60)),
        (tcx - 5.5, tcy - 10.5, 0.0, math.radians(120)),
        (tcx + 22.0, tcy + 3.0, 0.0, math.radians(90)),
        (tcx + 22.0, tcy - 3.0, 0.0, math.radians(-90)),
    ]
    for idx, (bx, by, bz, yaw) in enumerate(bench_positions):
        b_root = empty(f"Banca_Parque_{idx+1}", (bx, by, bz), "ENTORNO", root, 0.2)
        b_root.rotation_euler = Euler((0, 0, yaw), "XYZ")
        # Patas de hierro negro
        cube(f"Banca_{idx+1}_Pata_Izq", (0.06, 0.6, 0.45), (0, 0.7, 0.22), "ENTORNO", b_root, iron)
        cube(f"Banca_{idx+1}_Pata_Der", (0.06, 0.6, 0.45), (0, -0.7, 0.22), "ENTORNO", b_root, iron)
        # Asiento y espaldar de madera
        cube(f"Banca_{idx+1}_Asiento", (0.5, 1.5, 0.05), (0, 0, 0.45), "ENTORNO", b_root, wood)
        cube(f"Banca_{idx+1}_Espaldar", (0.06, 1.5, 0.45), (-0.22, 0, 0.72), "ENTORNO", b_root, wood)

    return root

# -------------------------------------------------------------
# 4. PALMERAS, ARBOLES TROPICALES Y FAROLES DEL PARQUE
# -------------------------------------------------------------
def build_park_vegetation_and_lights():
    root = empty("Vegetacion_Parque_Root", (0,0,0), "ENTORNO", size=0.5)
    
    # Palmeras Reales caribeñas bordeando la plaza
    palm_locs = [
        (4.0, 14.5, 0.0), (12.0, 16.0, 0.0), (22.0, 16.0, 0.0), (30.0, 14.0, 0.0),
        (4.0, -14.5, 0.0), (12.0, -16.0, 0.0), (22.0, -16.0, 0.0), (30.0, -14.0, 0.0),
        (34.0, 8.5, 0.0), (34.0, -8.5, 0.0), (2.0, 6.0, 0.0), (2.0, -6.0, 0.0)
    ]
    for i, loc in enumerate(palm_locs):
        make_palm(f"Palmera_Plaza_{i+1}", loc, height=6.2 + (i % 3) * 0.4)

    # Árboles frondosos tropicales (Almendros / Ficus como se ven en la foto aérea)
    tree_locs = [
        (8.0, 10.0, 0.0), (24.0, 10.5, 0.0), (8.0, -10.0, 0.0), (24.0, -10.5, 0.0),
        (32.0, 15.0, 0.0), (32.0, -15.0, 0.0), (2.0, 18.0, 0.0), (2.0, -18.0, 0.0)
    ]
    for i, loc in enumerate(tree_locs):
        make_tree(f"Almendro_Plaza_{i+1}", loc)

    # Faroles coloniales en la plaza
    lamp_locs = [
        (10.0, 7.0, 0.0), (22.0, 7.0, 0.0), (10.0, -7.0, 0.0), (22.0, -7.0, 0.0),
        (16.0, 12.0, 0.0), (16.0, -12.0, 0.0), (28.0, 0.0, 0.0), (4.0, 0.0, 0.0)
    ]
    for i, loc in enumerate(lamp_locs):
        make_lamp(f"Farol_Plaza_{i+1}", loc)

    return root

# -------------------------------------------------------------
# 5. CASAS COLONIALES Y SIERRA NEVADA DE SANTA MARTA
# -------------------------------------------------------------
def build_colonial_buildings_and_mountains():
    root = empty("Fondo_Urbano_Root", (0,0,0), "ENTORNO", size=0.5)

    facades = [
        (0.92, 0.88, 0.75), (0.85, 0.72, 0.28), (0.75, 0.28, 0.22),
        (0.22, 0.55, 0.65), (0.95, 0.94, 0.90), (0.88, 0.65, 0.18),
        (0.35, 0.60, 0.42), (0.80, 0.35, 0.25), (0.92, 0.90, 0.85),
    ]
    roofs = [
        (0.65, 0.28, 0.18), (0.58, 0.24, 0.14), (0.70, 0.32, 0.20),
        (0.55, 0.22, 0.12), (0.62, 0.26, 0.16), (0.68, 0.30, 0.18),
        (0.58, 0.25, 0.15), (0.65, 0.28, 0.18), (0.60, 0.24, 0.14),
    ]

    # Manzana Norte (enmarca la plaza al norte)
    for i in range(5):
        make_house(f"Casa_Plaza_Norte_{i+1}", (i * 8.5 - 2.0, 24.5, 0.0), (7.8, 6.2, 4.2 + (i%2)*0.6), facades[i%len(facades)], roofs[i%len(roofs)], yaw=math.radians(-90))

    # Manzana Sur (enmarca la plaza al sur)
    for i in range(5):
        make_house(f"Casa_Plaza_Sur_{i+1}", (i * 8.5 - 2.0, -24.5, 0.0), (7.8, 6.2, 4.2 + (i%2)*0.6), facades[(i+3)%len(facades)], roofs[(i+3)%len(roofs)], yaw=math.radians(90))

    # Manzana Oeste (frente a la iglesia, fondo de la perspectiva)
    for i in range(4):
        make_house(f"Casa_Plaza_Oeste_{i+1}", (-8.5, i * 8.0 - 12.0, 0.0), (6.5, 7.2, 4.0), facades[(i+5)%len(facades)], roofs[(i+5)%len(roofs)], yaw=0)

    # Cadena Montañosa de la Sierra Nevada de Santa Marta (al fondo este/norte, como en la foto)
    mountain_mat = new_mat("MAT_Sierra_Nevada", (0.24, 0.38, 0.35), 0.0, 0.9)
    for idx, (mx, my, sc, h) in enumerate([(75.0, -10.0, (18, 30, 16), 18.0), (85.0, 18.0, (22, 35, 22), 24.0), (95.0, -2.0, (26, 40, 28), 32.0)]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=(mx, my, h * 0.4))
        mount = mesh_obj(f"Sierra_Nevada_Pico_{idx+1}", "ENTORNO", root)
        mount.scale = sc
        select_only(mount)
        bpy.ops.object.transform_apply(scale=True)
        assign(mount, mountain_mat)

    return root

# -------------------------------------------------------------
# 6. DISTRIBUCION DE RESIDUOS EN EL CIRCUITO DE LIMPIEZA
# -------------------------------------------------------------
def build_trash_plaza():
    # Alrededor del Templete (Rotonda central peatonal)
    bottle("Botella_Templete_1", (11.5, 2.2, 0.035), 0.6, (0.75, 0.85, 0.9))
    bottle("Botella_Templete_2", (19.8, -3.4, 0.035), -0.8, (0.2, 0.45, 0.75))
    can("Lata_Templete_1", (13.2, -4.1, 0.035), (0.75, 0.18, 0.16))
    can("Lata_Templete_2", (20.5, 2.8, 0.035), (0.2, 0.35, 0.7))
    crumpled("Papel_Templete_1", (15.2, 4.8, 0.04), (1.1, 0.8, 0.7), (0.86, 0.85, 0.8))
    crumpled("Papel_Templete_2", (16.8, -5.2, 0.04), (0.9, 1.1, 0.7), (0.9, 0.88, 0.7))
    crumpled("Vaso_Templete_1", (12.2, -1.8, 0.04), (0.7, 0.7, 0.5), (0.9, 0.9, 0.92))
    
    # En el sendero hacia la Iglesia San Juan Bautista
    bottle("Botella_Sendero_Iglesia", (25.5, 1.2, 0.035), 0.3, (0.85, 0.85, 0.8))
    can("Lata_Sendero_Iglesia", (28.8, -1.5, 0.035), (0.9, 0.7, 0.1))
    crumpled("Papel_Sendero_Iglesia", (32.2, 0.8, 0.04), (1.0, 1.0, 0.6), (0.8, 0.8, 0.75))
    cardboard("Caja_Carton_Plaza", (22.5, 6.2, 0.03))
    bag("Bolsa_Basura_Parque", (6.5, -9.5, 0.16))

# Helper functions for palm and tree
def make_palm(name, loc, height=6.0, lean=0.0):
    trunk_mat = new_mat("MAT_Palmera_Tronco", (0.35, 0.22, 0.10), 0.0, 0.7)
    leaf_mat = new_mat("MAT_Palmera_Hoja", (0.12, 0.38, 0.10), 0.0, 0.55)
    root = empty(name, loc, "ENTORNO", size=0.2)
    cylinder(f"{name}_Tronco", 0.16, height, (0, 0, height * 0.5), (lean, 0, 0), "ENTORNO", root, trunk_mat, verts=10)
    for i in range(8):
        a = i * (math.pi * 2 / 8)
        cone(f"{name}_Hoja_{i+1}", 0.24, 2.0, (math.cos(a) * 0.4, math.sin(a) * 0.4, height * 0.92), (math.radians(72), 0, a), "ENTORNO", root, leaf_mat)
    return root

def make_tree(name, loc):
    bark = new_mat("MAT_Arbol_Tronco", (0.22, 0.13, 0.07), 0.0, 0.8)
    leaf = new_mat("MAT_Arbol_Copa", (0.14, 0.42, 0.12), 0.0, 0.65)
    root = empty(name, loc, "ENTORNO", size=0.2)
    cylinder(f"{name}_Tronco", 0.22, 2.8, (0, 0, 1.4), (0, 0, 0), "ENTORNO", root, bark, 10)
    uv_sphere(f"{name}_Copa", 1.8, (0, 0, 3.8), "ENTORNO", root, leaf, 14)
    uv_sphere(f"{name}_Copa2", 1.3, (0.7, -0.4, 4.2), "ENTORNO", root, leaf, 12)
    return root

def make_lamp(name, loc):
    metal = new_mat("MAT_Farol_Metal", (0.12, 0.12, 0.14), 0.6, 0.35)
    lamp_m = new_mat("MAT_Farol_Luz", (1.0, 0.95, 0.8), 0.0, 0.2)
    root = empty(name, loc, "ENTORNO", size=0.1)
    cylinder(f"{name}_Poste", 0.07, 3.8, (0, 0, 1.9), (0, 0, 0), "ENTORNO", root, metal, 10)
    cube(f"{name}_Brazo", (0.7, 0.06, 0.06), (0.25, 0, 3.7), "ENTORNO", root, metal)
    uv_sphere(f"{name}_Globo", 0.18, (0.6, 0, 3.55), "ENTORNO", root, lamp_m, 10)
    return root

def make_house(name, loc, size, facade, roof_col, yaw=0):
    sx, sy, sz = size
    wall = new_mat(f"MAT_{name}_Muro", facade, 0.0, 0.62)
    roof_m = new_mat(f"MAT_{name}_Teja", roof_col, 0.0, 0.55)
    wood = new_mat("MAT_Madera_Casa", (0.28, 0.16, 0.08), 0.0, 0.55)
    glass = new_mat("MAT_Vidrio", (0.15, 0.2, 0.25), 0.1, 0.12)
    root = empty(name, loc, "ENTORNO", size=0.3)
    root.rotation_euler = Euler((0, 0, yaw), "XYZ")
    cube(f"{name}_Cuerpo", (sx, sy, sz), (0, 0, sz * 0.5), "ENTORNO", root, wall)
    roof = cube(f"{name}_Techo", (sx * 1.1, sy * 1.1, 0.15), (0, 0, sz + 0.22), "ENTORNO", root, roof_m)
    roof.rotation_euler = Euler((math.radians(16), 0, 0), "XYZ")
    cube(f"{name}_Puerta", (0.04, 0.9, 2.1), (sx * 0.5 + 0.02, 0.2, 1.05), "ENTORNO", root, wood)
    cube(f"{name}_Ventana_1", (0.05, 0.7, 0.9), (sx * 0.5 + 0.02, -sy * 0.25, 1.6), "ENTORNO", root, glass)
    return root

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

# -------------------------------------------------------------
# 7. CONSTRUCCION DEL ROBOT (Con origen en 0,0,0)
# -------------------------------------------------------------
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
    chasis = cube("Chasis", (CHASSIS_L, CHASSIS_W, CHASSIS_H), chassis_loc, "ROBOT", root, mats["black"])

    cube("Chasis_Banda_Gris", (CHASSIS_L * 0.98, CHASSIS_W * 1.02, CHASSIS_H * 0.28), (rx, ry, rz + CHASSIS_Z - 0.02), "ROBOT", chasis, mats["grey"], keep_world=True)
    for side, name in ((1, "Panel_Amarillo_Izquierdo"), (-1, "Panel_Amarillo_Derecho")):
        cube(name, (0.42, 0.04, 0.18), (rx + 0.12, ry + side * (CHASSIS_W * 0.5 + 0.01), rz + CHASSIS_Z + 0.02), "ROBOT", chasis, mats["yellow"], keep_world=True)
    cube("Chasis_Frontal", (0.18, CHASSIS_W * 0.72, 0.16), (rx + CHASSIS_L * 0.5 + 0.02, ry, rz + CHASSIS_Z - 0.04), "ROBOT", chasis, mats["grey"], keep_world=True)
    cube("Parachoques", (0.06, CHASSIS_W * 0.78, 0.08), (rx + CHASSIS_L * 0.5 + 0.12, ry, rz + 0.16), "ROBOT", chasis, mats["yellow"], keep_world=True)

    wheel_x, wheel_y, wheel_z = WHEELBASE / 2.0, TRACK / 2.0, WHEEL_R
    wheel_defs = [
        ("Rueda_Delantera_Derecha", +wheel_x, -wheel_y),
        ("Rueda_Delantera_Izquierda", +wheel_x, +wheel_y),
        ("Rueda_Trasera_Derecha", -wheel_x, -wheel_y),
        ("Rueda_Trasera_Izquierda", -wheel_x, +wheel_y),
    ]
    for name, dx, dy in wheel_defs:
        pivot = empty(f"Pivote_{name}", (rx + dx, ry + dy, rz + wheel_z), "ROBOT", root, 0.06)
        cylinder(name, WHEEL_R, WHEEL_W, (0, 0, 0), (math.radians(90), 0, 0), "ROBOT", pivot, mats["tire"], verts=28)
        cylinder(f"Llanta_{name}", WHEEL_R * 0.62, WHEEL_W * 0.55, (0, 0, 0), (math.radians(90), 0, 0), "ROBOT", pivot, mats["rim"], verts=20)
        cylinder(f"Cubo_{name}", WHEEL_R * 0.18, WHEEL_W * 0.7, (0, 0, 0), (math.radians(90), 0, 0), "ROBOT", pivot, mats["grey"], verts=12)

    bin_x = rx - 0.18
    bin_z = rz + CHASSIS_Z + CHASSIS_H * 0.5 + BIN_H * 0.5 + 0.01
    contenedor = cube("Contenedor_Basura", (BIN_L, BIN_W, BIN_H), (bin_x, ry, bin_z), "ROBOT", chasis, mats["bin"], keep_world=True)
    cube("Contenedor_Interior", (BIN_L * 0.86, BIN_W * 0.86, BIN_H * 0.72), (bin_x, ry, bin_z + 0.04), "ROBOT", contenedor, new_mat("MAT_Interior_Bin", (0.08, 0.09, 0.08), 0.0, 0.7), keep_world=True)
    for i, ang in enumerate((0.0, 120.0, 240.0)):
        a = math.radians(ang)
        cylinder(f"Simbolo_Reciclaje_{i + 1}", 0.035, 0.012, (bin_x - BIN_L * 0.51, ry + math.sin(a) * 0.07, bin_z + math.cos(a) * 0.07), (0, math.radians(90), a), "ROBOT", contenedor, mats["recycle"], verts=10, keep_world=True)
    for i, off in enumerate(((-0.08, 0.1, 0.12), (0.05, -0.08, 0.1), (0.0, 0.0, 0.18))):
        uv_sphere(f"Residuo_En_Contenedor_{i + 1}", 0.05 + 0.01 * i, (bin_x + off[0], ry + off[1], bin_z + off[2]), "ROBOT", contenedor, new_mat(f"MAT_ResiduoBin_{i}", (0.55, 0.65 + i * 0.05, 0.7), 0.0, 0.4), segs=10, keep_world=True)

    mast_z = bin_z + BIN_H * 0.5 + 0.08
    mast_x = bin_x + 0.12
    mast = cylinder("Mastil_Sensor", 0.035, 0.16, (mast_x, ry, mast_z), (0, 0, 0), "SENSORES", chasis, mats["plastic"], verts=16, keep_world=True)
    head = cylinder("Sensor_Camara_Superior", 0.055, 0.07, (mast_x, ry, mast_z + 0.11), (0, 0, 0), "SENSORES", mast, mats["black"], verts=16, keep_world=True)
    uv_sphere("Lente_Camara_Superior", 0.032, (mast_x, ry, mast_z + 0.155), "SENSORES", head, mats["lens"], segs=12, keep_world=True)
    cylinder("Sensor_Frontal", 0.028, 0.04, (rx + CHASSIS_L * 0.5 + 0.14, ry, rz + CHASSIS_Z + 0.08), (0, math.radians(90), 0), "SENSORES", chasis, mats["lens"], verts=16, keep_world=True)
    for side, nm in ((0.12, "Sensor_Ultrasonido_Izquierdo"), (-0.12, "Sensor_Ultrasonido_Derecho")):
        cylinder(nm, 0.018, 0.03, (rx + CHASSIS_L * 0.5 + 0.13, ry + side, rz + CHASSIS_Z + 0.02), (0, math.radians(90), 0), "SENSORES", chasis, mats["grey"], verts=12, keep_world=True)

    base_pos = Vector((rx + CHASSIS_L * 0.5 + 0.05, ry, rz + CHASSIS_Z + 0.06))
    pivote_base = empty("Pivote_Brazo_Base", base_pos, "ROBOT", root, 0.07)
    cylinder("Brazo_Base", 0.055, ARM_BASE_H, (0, 0, ARM_BASE_H * 0.35), (0, 0, 0), "ROBOT", pivote_base, mats["joint"], verts=16)

    pivote_1 = empty("Pivote_Brazo_1", (0, 0, ARM_BASE_H * 0.85), "ROBOT", pivote_base, 0.06)
    uv_sphere("Articulacion_1", 0.048, (0, 0, 0), "ROBOT", pivote_1, mats["joint"], 12)
    cube("Brazo_Segmento_1", (SEG1_L, SEG1_T, SEG1_T), (SEG1_L * 0.5, 0, 0), "ROBOT", pivote_1, mats["metal"])

    pivote_2 = empty("Pivote_Brazo_2", (SEG1_L, 0, 0), "ROBOT", pivote_1, 0.055)
    uv_sphere("Articulacion_2", 0.042, (0, 0, 0), "ROBOT", pivote_2, mats["joint"], 12)
    cube("Brazo_Segmento_2", (SEG2_L, SEG2_T, SEG2_T * 0.9), (SEG2_L * 0.5, 0, 0), "ROBOT", pivote_2, mats["metal"])

    pivote_pinza = empty("Pivote_Pinza", (SEG2_L, 0, 0), "ROBOT", pivote_2, 0.05)
    cylinder("Muneca_Pinza", 0.032, 0.05, (0.01, 0, 0), (0, math.radians(90), 0), "ROBOT", pivote_pinza, mats["joint"], verts=14)
    piv_l = empty("Pivote_Pinza_Izquierda", (0.04, GRIP_OPEN * 0.5, 0), "ROBOT", pivote_pinza, 0.03)
    piv_r = empty("Pivote_Pinza_Derecha", (0.04, -GRIP_OPEN * 0.5, 0), "ROBOT", pivote_pinza, 0.03)
    cube("Pinza_Izquierda", (GRIP_L, GRIP_W, GRIP_H), (GRIP_L * 0.45, 0, 0), "ROBOT", piv_l, mats["grip"])
    cube("Pinza_Derecha", (GRIP_L, GRIP_W, GRIP_H), (GRIP_L * 0.45, 0, 0), "ROBOT", piv_r, mats["grip"])
    cube("Yema_Pinza_Izquierda", (0.04, 0.018, GRIP_H * 0.7), (GRIP_L * 0.9, -0.01, 0), "ROBOT", piv_l, mats["yellow"])
    cube("Yema_Pinza_Derecha", (0.04, 0.018, GRIP_H * 0.7), (GRIP_L * 0.9, 0.01, 0), "ROBOT", piv_r, mats["yellow"])

    return root

# -------------------------------------------------------------
# 8. ILUMINACION Y CAMARAS (Perspectiva Aérea idéntica a la foto)
# -------------------------------------------------------------
def setup_aerial_view():
    # Luz Solar Caribeña Cálida de Atardecer
    sun = bpy.data.lights.new("Sol_Cienaga", "SUN")
    sun.energy = 5.5
    sun.color = (1.0, 0.92, 0.82)
    sun_obj = bpy.data.objects.new("Sol_Cienaga", sun)
    collection("ENTORNO").objects.link(sun_obj)
    sun_obj.rotation_euler = Euler((math.radians(52), math.radians(12), math.radians(45)), "XYZ")

    # Luz de relleno ambiente
    fill = bpy.data.lights.new("Luz_Ambiente", "AREA")
    fill.energy = 300
    fill.size = 25
    fill.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new("Luz_Ambiente", fill)
    collection("ENTORNO").objects.link(fill_obj)
    fill_obj.location = (20, 0, 25)

    # Cámara Aérea idéntica a la foto del dron en Instagram (Elevada, mirando el Templete con la iglesia al fondo)
    cam_data = bpy.data.cameras.new("Camara_Aerea_Plaza")
    cam = bpy.data.objects.new("Camara_Aerea_Plaza", cam_data)
    collection("CAMARAS").objects.link(cam)
    cam.location = (-6.0, 0.0, 16.5)
    cam.rotation_euler = Euler((math.radians(65), 0, math.radians(-90)), "XYZ")
    cam_data.lens = 28
    cam_data.clip_end = 300
    bpy.context.scene.camera = cam

    # Cámara Tres Cuartos cercana al robot
    cam_robot_data = bpy.data.cameras.new("Camara_Tres_Cuartos")
    cam_robot = bpy.data.objects.new("Camara_Tres_Cuartos", cam_robot_data)
    collection("CAMARAS").objects.link(cam_robot)
    cam_robot.location = (3.5, -4.5, 2.2)
    cam_robot.rotation_euler = Euler((math.radians(72), 0, math.radians(35)), "XYZ")
    cam_robot_data.lens = 35

def duplicate_and_join(obj_names, new_name, relative_to_matrix=None):
    bpy.ops.object.select_all(action='DESELECT')
    copies = []
    for name in obj_names:
        orig = bpy.data.objects.get(name)
        if not orig or orig.type not in ('MESH', 'CURVE', 'FONT', 'SURFACE'):
            continue
        copy = orig.copy()
        if copy.data:
            copy.data = orig.data.copy()
        bpy.context.collection.objects.link(copy)
        copy.matrix_world = orig.matrix_world.copy()
        copy.parent = None
        copies.append(copy)
    
    if not copies:
        return None

    for c in copies:
        c.select_set(True)
        bpy.context.view_layer.objects.active = c
        if c.type in ('FONT', 'CURVE'):
            bpy.ops.object.convert(target='MESH')
        for m in list(c.modifiers):
            try:
                bpy.ops.object.modifier_apply(modifier=m.name)
            except Exception:
                pass

    if relative_to_matrix:
        inv_mat = relative_to_matrix.inverted()
        for c in copies:
            c.matrix_world = inv_mat @ c.matrix_world

    bpy.ops.object.select_all(action='DESELECT')
    for c in copies:
        c.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    
    if len(copies) > 1:
        bpy.ops.object.join()
    
    joined = bpy.context.active_object
    joined.name = new_name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return joined

def export_obj(obj, filepath):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.obj_export(
        filepath=str(filepath),
        export_selected_objects=True,
        apply_modifiers=True,
        forward_axis='X',
        up_axis='Z',
        export_materials=True,
        export_normals=True,
        export_uv=True,
    )
    print("Exported OBJ:", filepath)

def main():
    print("INICIANDO MODELADO COMPLETO DE LA PLAZA DEL CENTENARIO...")
    clear_scene()
    for name in ("ROBOT", "ENTORNO", "BASURA", "SENSORES", "CAMARAS"):
        collection(name)

    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "METERS"
    bpy.context.scene.unit_settings.scale_length = 1.0

    # 1. Construir Robot en posición de partida
    build_robot(root_loc=(0.0, 0.0, 0.0))

    # 2. Construir El Templete de Ciénaga (Centro de la plaza)
    build_templete(center=(16.0, 0.0, 0.0))

    # 3. Construir Iglesia San Juan Bautista (Fondo)
    build_church(pos=(38.0, 3.0, 0.0))

    # 4. Construir La Plaza, Senderos, Glorieta y Bancas
    build_plaza_centenario(templete_center=(16.0, 0.0, 0.0))

    # 5. Vegetación (Palmeras reales y almendros) y Faroles
    build_park_vegetation_and_lights()

    # 6. Edificaciones coloniales circundantes y Sierra Nevada
    build_colonial_buildings_and_mountains()

    # 7. Residuos en el plano de recolección
    build_trash_plaza()

    # 8. Cámaras e iluminación
    setup_aerial_view()

    # Guardar archivo .blend
    out_blend = PROJECT_DIR / "Robot_Limpiador_Cienaga.WBT.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
    print("SAVED BLEND FILE:", out_blend)

    # 9. EXPORTAR MALLAS MODULARES PARA WEBOTS
    entorno_col = bpy.data.collections.get("ENTORNO")
    
    # A. Malla del Templete
    templete_objs = [o.name for o in entorno_col.objects if "Templete_" in o.name]
    m_templete = duplicate_and_join(templete_objs, "Export_Templete")
    if m_templete:
        export_obj(m_templete, MESH_DIR / "entorno_templete.obj")
        bpy.data.objects.remove(m_templete, do_unlink=True)

    # B. Malla de la Iglesia San Juan Bautista
    iglesia_objs = [o.name for o in entorno_col.objects if "Iglesia_" in o.name or "Pergola_" in o.name]
    m_iglesia = duplicate_and_join(iglesia_objs, "Export_Iglesia")
    if m_iglesia:
        export_obj(m_iglesia, MESH_DIR / "entorno_iglesia.obj")
        bpy.data.objects.remove(m_iglesia, do_unlink=True)

    # C. Malla de la Plaza, Senderos, Jardineras y Bancas
    plaza_objs = [o.name for o in entorno_col.objects if any(k in o.name for k in ["Plaza_", "Jardin_", "Sendero_", "Banca_", "Arbusto_"])]
    m_plaza = duplicate_and_join(plaza_objs, "Export_Plaza")
    if m_plaza:
        export_obj(m_plaza, MESH_DIR / "entorno_plaza.obj")
        bpy.data.objects.remove(m_plaza, do_unlink=True)

    # D. Flora (Palmeras y Almendros)
    flora_objs = [o.name for o in entorno_col.objects if any(k in o.name for k in ["Palmera_", "Almendro_"])]
    m_flora = duplicate_and_join(flora_objs, "Export_Flora")
    if m_flora:
        export_obj(m_flora, MESH_DIR / "entorno_flora.obj")
        bpy.data.objects.remove(m_flora, do_unlink=True)

    # E. Faroles
    faroles_objs = [o.name for o in entorno_col.objects if "Farol_" in o.name]
    m_faroles = duplicate_and_join(faroles_objs, "Export_Faroles")
    if m_faroles:
        export_obj(m_faroles, MESH_DIR / "entorno_postes.obj")
        bpy.data.objects.remove(m_faroles, do_unlink=True)

    # F. Casas perimetrales y Sierra Nevada
    fondo_objs = [o.name for o in entorno_col.objects if any(k in o.name for k in ["Casa_Plaza_", "Sierra_Nevada_"])]
    m_fondo = duplicate_and_join(fondo_objs, "Export_Fondo")
    if m_fondo:
        export_obj(m_fondo, MESH_DIR / "entorno_casas.obj")
        bpy.data.objects.remove(m_fondo, do_unlink=True)

    # Renderizar vista aérea idéntica a la foto del dron
    render_dir = PROJECT_DIR / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.camera = bpy.data.objects["Camara_Aerea_Plaza"]
    scene.render.filepath = str(render_dir / "vista_plaza_centenario.png")
    scene.render.image_settings.file_format = "PNG"
    try:
        bpy.ops.render.render(write_still=True)
        print("AERIAL RENDER SAVED TO:", scene.render.filepath)
        # Also copy as webots thumbnail
        thumb_path = PROJECT_DIR / "worlds" / ".cienaga_limpiador.jpg"
        scene.render.image_settings.file_format = "JPEG"
        scene.render.filepath = str(thumb_path)
        bpy.ops.render.render(write_still=True)
        print("THUMBNAIL UPDATED:", thumb_path)
    except Exception as e:
        print("Render warning:", e)

    print("TODO EL MODELADO Y EXPORTACION DE LA PLAZA FUE COMPLETADO CON EXITO!")

if __name__ == "__main__":
    main()
