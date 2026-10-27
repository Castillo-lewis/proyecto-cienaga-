"""
Controlador Autónomo de Limpieza y Recorrido Completo
Plaza del Centenario - Ciénaga, Magdalena (Webots R2025a)

El robot recorre sistemáticamente TODOS los sectores de la plaza:
  - Paseo Oeste (Entrada)
  - Rotonda y Jardineras Norte
  - Paseo Central Este (Hacia la Iglesia San Juan Bautista)
  - Rotonda y Jardineras Sur
Mientras recorre la plaza, detecta y recolecta residuos en su camino,
depositándolos en su tolva trasera con su brazo robótico de 4 GDL y pinzas visibles.
"""

import sys
import math
from controller import Supervisor, Keyboard

def normalize_angle(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle

def compute_gripper_world_pos(rx, ry, ryaw, yaw_angle, sh_angle, el_angle):
    """
    Calcula la posición 3D exacta en coordenadas globales del extremo de la pinza,
    utilizando cinemática directa del brazo de 4 GDL montado sobre el chasis.
    """
    a1 = sh_angle
    a2 = sh_angle + el_angle
    # Alcance radial hacia adelante desde el pivote del hombro:
    R = 0.42 * math.cos(a1) + 0.52 * math.cos(a2)
    # Altura vertical respecto a la base del robot:
    Z_local = 0.442 - 0.42 * math.sin(a1) - 0.52 * math.sin(a2)

    # Coordenadas en el marco local del robot (pivote de yaw en X=0.65):
    X_robot = 0.65 + R * math.cos(yaw_angle)
    Y_robot = 0.00 + R * math.sin(yaw_angle)

    # Transformación al sistema de coordenadas del mundo (ENU):
    c = math.cos(ryaw)
    s = math.sin(ryaw)
    X_world = rx + X_robot * c - Y_robot * s
    Y_world = ry + X_robot * s + Y_robot * c
    Z_world = max(0.03, 0.05 + Z_local)
    return [X_world, Y_world, Z_world]

def main():
    supervisor = Supervisor()
    time_step = int(supervisor.getBasicTimeStep())
    if time_step <= 0:
        time_step = 16

    print("=" * 72, flush=True)
    print(" 🤖 ROBOT LIMPIADOR URBANO - CIRCUITO PLAZA DEL CENTENARIO", flush=True)
    print(" Simulación Webots R2025a | Recorrido Completo y Recolección Activa", flush=True)
    print(" Brazo de 4 GDL y Pinzas Visibles con Cinemática Directa 3D", flush=True)
    print("=" * 72, flush=True)

    # ---------------------------------------------------------
    # 1. MOTORES DE TRACCIÓN (4 Ruedas Motrices)
    # ---------------------------------------------------------
    wheel_names = [
        "motor_rueda_DI", "motor_rueda_DD",
        "motor_rueda_TI", "motor_rueda_TD"
    ]
    wheels = {}
    for name in wheel_names:
        m = supervisor.getDevice(name)
        if m:
            m.setPosition(float('inf'))
            m.setVelocity(0.0)
            wheels[name] = m

    def set_drive_velocities(left_vel, right_vel):
        if "motor_rueda_DI" in wheels:
            wheels["motor_rueda_DI"].setVelocity(left_vel)
        if "motor_rueda_TI" in wheels:
            wheels["motor_rueda_TI"].setVelocity(left_vel)
        if "motor_rueda_DD" in wheels:
            wheels["motor_rueda_DD"].setVelocity(right_vel)
        if "motor_rueda_TD" in wheels:
            wheels["motor_rueda_TD"].setVelocity(right_vel)

    # ---------------------------------------------------------
    # 2. MOTORES DEL BRAZO ROBÓTICO (4 GDL + PINZA)
    # ---------------------------------------------------------
    arm_names = [
        "motor_brazo_yaw", "motor_brazo_hombro",
        "motor_brazo_codo", "motor_pinza_izq", "motor_pinza_der"
    ]
    arm_motors = {}
    for name in arm_names:
        m = supervisor.getDevice(name)
        if m:
            arm_motors[name] = m

    # Posición inicial de patrulla (plegado, seguro y visible)
    arm_targets = {
        "motor_brazo_yaw": 0.0,
        "motor_brazo_hombro": -0.45,
        "motor_brazo_codo": 1.35,
        "motor_pinza_izq": 0.0,
        "motor_pinza_der": 0.0,
    }

    def apply_arm_positions():
        for name, target in arm_targets.items():
            if name in arm_motors:
                arm_motors[name].setPosition(target)

    apply_arm_positions()

    # ---------------------------------------------------------
    # 3. SENSORES
    # ---------------------------------------------------------
    ds_front = supervisor.getDevice("ds_frontal")
    if ds_front:
        ds_front.enable(time_step)

    ds_left = supervisor.getDevice("ds_izquierdo")
    if ds_left:
        ds_left.enable(time_step)

    ds_right = supervisor.getDevice("ds_derecho")
    if ds_right:
        ds_right.enable(time_step)

    camera = supervisor.getDevice("camara_superior")
    if camera:
        camera.enable(time_step * 2)

    imu = supervisor.getDevice("imu")
    if imu:
        imu.enable(time_step)

    gps = supervisor.getDevice("gps")
    if gps:
        gps.enable(time_step)

    keyboard = supervisor.getKeyboard()
    keyboard.enable(time_step)

    robot_node = supervisor.getSelf()

    # ---------------------------------------------------------
    # 4. CIRCUITO DE RECORRIDO DE TODA LA PLAZA DEL CENTENARIO
    # ---------------------------------------------------------
    PLAZA_CIRCUIT = [
        (6.0, 0.0, "Sendero Oeste (Entrada)"),
        (9.5, 0.0, "Aproximacion al Templete"),
        (12.5, 4.8, "Rotonda Noroeste"),
        (16.0, 7.8, "Paseo Norte (Jardineras)"),
        (20.5, 4.8, "Rotonda Noreste"),
        (25.0, 0.8, "Sendero Este (Hacia la Iglesia)"),
        (31.0, 0.0, "Atrio Iglesia San Juan Bautista"),
        (26.0, -1.0, "Sendero Este (Retorno de Iglesia)"),
        (20.5, -4.8, "Rotonda Sureste"),
        (16.0, -7.8, "Paseo Sur (Almendros y Palmeras)"),
        (12.5, -4.8, "Rotonda Suroeste"),
    ]
    circuit_index = 0

    # ---------------------------------------------------------
    # 5. CATALOGAR RESIDUOS DE LA PLAZA
    # ---------------------------------------------------------
    def scan_trash_nodes():
        root = supervisor.getRoot()
        children = root.getField("children")
        trash_list = []
        for i in range(children.getCount()):
            node = children.getMFNode(i)
            if node.getTypeName() == "Solid":
                name_field = node.getField("name")
                if name_field:
                    n_str = name_field.getSFString()
                    if any(k in n_str.lower() for k in ["botella", "lata", "papel", "vaso", "caja", "bolsa", "residuo"]):
                        if not any(ign in n_str.lower() for ign in ["rueda", "brazo", "pinza", "chasis", "templete_colision"]):
                            trash_list.append({
                                "node": node,
                                "name": n_str,
                                "collected": False,
                            })
        return trash_list

    trash_items = scan_trash_nodes()
    total_trash = len(trash_items)
    print(f"[INICIO] {total_trash} residuos ubicados a lo largo de la Plaza del Centenario.", flush=True)

    # ---------------------------------------------------------
    # 6. VARIABLES DE ESTADO Y PARÁMETROS
    # ---------------------------------------------------------
    mode = "AUTONOMO"
    auto_state = "PATRULLA_CIRCUITO"
    auto_timer = 0
    trash_collected = 0
    current_target_trash = None

    CRUISE_SPEED = 3.6
    TURN_SPEED = 2.4
    MAX_SPEED = 5.0

    step_count = 0
    last_key_press = -1

    def get_robot_pose():
        if gps and imu:
            p = gps.getValues()
            r = imu.getRollPitchYaw()
            return p[0], p[1], r[2]
        elif robot_node:
            p = robot_node.getPosition()
            ori = robot_node.getOrientation()
            yaw = math.atan2(ori[3], ori[0])
            return p[0], p[1], yaw
        return 0.0, 0.0, 0.0

    def update_hud(action_str):
        mode_col = 0x00FF88 if mode == "AUTONOMO" else 0x33CCFF
        sec_name = PLAZA_CIRCUIT[circuit_index][2] if circuit_index < len(PLAZA_CIRCUIT) else "Plaza"
        supervisor.setLabel(0, f"ROBOT LIMPIADOR DE CIENAGA  |  MODO: {mode}", 0.02, 0.02, 0.065, mode_col, 0.0, "Lucida Console")
        supervisor.setLabel(1, f"Residuos: {trash_collected}/{total_trash}   Sector: {sec_name}   Tolva: {min(100, trash_collected*10)}%", 0.02, 0.06, 0.048, 0xFFFFFF, 0.0, "Lucida Console")
        supervisor.setLabel(2, f"Accion: {action_str}", 0.02, 0.10, 0.044, 0xFFDD33, 0.0, "Lucida Console")
        supervisor.setLabel(3, "[M] Alternar Manual/Autonomo  |  [Flechas] Conducir  |  [C] Recoger  |  [ESPACIO] Frenar", 0.02, 0.95, 0.036, 0xCCCCCC, 0.0, "Lucida Console")

    # ---------------------------------------------------------
    # 7. BUCLE PRINCIPAL DE LA SIMULACIÓN
    # ---------------------------------------------------------
    while supervisor.step(time_step) != -1:
        step_count += 1
        rx, ry, ryaw = get_robot_pose()

        val_front = ds_front.getValue() if ds_front else 0.0
        val_left = ds_left.getValue() if ds_left else 0.0
        val_right = ds_right.getValue() if ds_right else 0.0

        # Manejo de tecla M
        key = keyboard.getKey()
        if key > 0:
            if key == ord('M') and last_key_press != ord('M'):
                mode = "MANUAL" if mode == "AUTONOMO" else "AUTONOMO"
                print(f"\n>>> CAMBIO DE MODO: {mode} <<<", flush=True)
                if mode == "MANUAL":
                    set_drive_velocities(0.0, 0.0)
                    update_hud("Modo Manual Activo (Usa las flechas del teclado)")
                else:
                    auto_state = "PATRULLA_CIRCUITO"
                    auto_timer = 0
                    update_hud("Modo Autónomo de Recorrido y Limpieza Reanudado")
            last_key_press = key
        else:
            last_key_press = -1

        # =====================================================
        # MODO MANUAL
        # =====================================================
        if mode == "MANUAL":
            lv = 0.0
            rv = 0.0
            if key == Keyboard.UP:
                lv, rv = MAX_SPEED, MAX_SPEED
            elif key == Keyboard.DOWN:
                lv, rv = -MAX_SPEED, -MAX_SPEED
            elif key == Keyboard.LEFT:
                lv, rv = -TURN_SPEED, TURN_SPEED
            elif key == Keyboard.RIGHT:
                lv, rv = TURN_SPEED, -TURN_SPEED
            elif key == ord(' '):
                lv, rv = 0.0, 0.0
            set_drive_velocities(lv, rv)

            # Control manual del brazo
            if key == ord('W'):
                arm_targets["motor_brazo_hombro"] = max(-1.4, arm_targets["motor_brazo_hombro"] - 0.03)
            elif key == ord('S'):
                arm_targets["motor_brazo_hombro"] = min(1.4, arm_targets["motor_brazo_hombro"] + 0.03)
            if key == ord('A'):
                arm_targets["motor_brazo_yaw"] = min(3.14, arm_targets["motor_brazo_yaw"] + 0.04)
            elif key == ord('D'):
                arm_targets["motor_brazo_yaw"] = max(-3.14, arm_targets["motor_brazo_yaw"] - 0.04)
            if key == ord('E'):
                arm_targets["motor_brazo_codo"] = min(2.4, arm_targets["motor_brazo_codo"] + 0.04)
            elif key == ord('Q'):
                arm_targets["motor_brazo_codo"] = max(-2.4, arm_targets["motor_brazo_codo"] - 0.04)
            if key == ord('G'):
                arm_targets["motor_pinza_izq"] = 0.32
                arm_targets["motor_pinza_der"] = -0.32
            elif key == ord('H'):
                arm_targets["motor_pinza_izq"] = -0.06
                arm_targets["motor_pinza_der"] = 0.06
            if key == ord('R'):
                arm_targets["motor_brazo_yaw"] = 0.0
                arm_targets["motor_brazo_hombro"] = -0.45
                arm_targets["motor_brazo_codo"] = 1.35
                arm_targets["motor_pinza_izq"] = 0.0
                arm_targets["motor_pinza_der"] = 0.0
            if key == ord('C'):
                # Iniciar gesto automático en modo manual sobre el residuo más cercano
                nearby_trash = None
                closest_d = 4.0
                for t in trash_items:
                    if not t["collected"]:
                        t_pos = t["node"].getPosition()
                        d = math.hypot(t_pos[0] - rx, t_pos[1] - ry)
                        if d < closest_d:
                            closest_d = d
                            nearby_trash = t
                if nearby_trash:
                    current_target_trash = nearby_trash
                    mode = "AUTONOMO"
                    auto_state = "APUNTAR_PINZA"
                    auto_timer = 0
                    set_drive_velocities(0.0, 0.0)

            apply_arm_positions()
            if step_count % 30 == 0:
                update_hud(f"Manual | Velo=({lv:.1f}, {rv:.1f})")

        # =====================================================
        # MODO AUTÓNOMO: RECORRIDO + BÚSQUEDA Y RECOLECCIÓN
        # =====================================================
        else:
            # 1. Detectar si hay un residuo en el radio de intercepción (~3.5 m)
            if auto_state == "PATRULLA_CIRCUITO":
                nearby_trash = None
                closest_d = 3.5

                for t in trash_items:
                    if not t["collected"]:
                        t_pos = t["node"].getPosition()
                        d = math.hypot(t_pos[0] - rx, t_pos[1] - ry)
                        if d < closest_d:
                            closest_d = d
                            nearby_trash = t

                if nearby_trash:
                    current_target_trash = nearby_trash
                    auto_state = "INTERCEPTAR_RESIDUO"
                    auto_timer = 0
                    print(f"\n[DETECCIÓN] Residuo avistado: '{nearby_trash['name']}' a {closest_d:.2f} m. Maniobrando para recoger...", flush=True)

            # -------------------------------------------------
            # ESTADO A: PATRULLAR EL CIRCUITO DE LA PLAZA
            # -------------------------------------------------
            if auto_state == "PATRULLA_CIRCUITO":
                wp_x, wp_y, wp_name = PLAZA_CIRCUIT[circuit_index]
                dx = wp_x - rx
                dy = wp_y - ry
                dist_wp = math.hypot(dx, dy)
                target_yaw = math.atan2(dy, dx)
                yaw_error = normalize_angle(target_yaw - ryaw)

                # Llegada al waypoint actual -> pasar al siguiente
                if dist_wp < 1.3:
                    circuit_index = (circuit_index + 1) % len(PLAZA_CIRCUIT)
                    new_sec = PLAZA_CIRCUIT[circuit_index][2]
                    print(f"[RECORRIDO] Entrando a sector: {new_sec}", flush=True)
                else:
                    # Evasión de bordillos laterales
                    if val_left > 1300.0:
                        set_drive_velocities(CRUISE_SPEED, CRUISE_SPEED * 0.35)
                    elif val_right > 1300.0:
                        set_drive_velocities(CRUISE_SPEED * 0.35, CRUISE_SPEED)
                    else:
                        kp = 3.0
                        turn = max(-TURN_SPEED, min(TURN_SPEED, kp * yaw_error))
                        if abs(yaw_error) > 0.6:
                            set_drive_velocities(-turn * 0.8, turn * 0.8)
                        else:
                            set_drive_velocities(CRUISE_SPEED - turn, CRUISE_SPEED + turn)

                if step_count % 30 == 0:
                    update_hud(f"Patrullando {wp_name}...")

            # -------------------------------------------------
            # ESTADO B: NAVEGAR HACIA EL RESIDUO DETECTADO
            # -------------------------------------------------
            elif auto_state == "INTERCEPTAR_RESIDUO":
                t_pos = current_target_trash["node"].getPosition()
                dx = t_pos[0] - rx
                dy = t_pos[1] - ry
                dist_t = math.hypot(dx, dy)
                target_yaw = math.atan2(dy, dx)
                yaw_error = normalize_angle(target_yaw - ryaw)

                # Distancia óptima para alcance del brazo (entre 1.35m y 1.50m del centro del robot)
                if dist_t <= 1.45 or (dist_t <= 1.65 and val_front > 400.0):
                    set_drive_velocities(0.0, 0.0)
                    auto_state = "APUNTAR_PINZA"
                    auto_timer = 0
                    print(f"[AUTONOMO] Frente al residuo {current_target_trash['name']}. Iniciando recolección...", flush=True)
                else:
                    kp = 3.2
                    turn = max(-TURN_SPEED, min(TURN_SPEED, kp * yaw_error))
                    if abs(yaw_error) > 0.5:
                        set_drive_velocities(-turn * 0.8, turn * 0.8)
                    else:
                        spd = 2.4 if dist_t < 2.0 else CRUISE_SPEED
                        set_drive_velocities(spd - turn, spd + turn)

                if step_count % 25 == 0:
                    update_hud(f"Aproximandose a {current_target_trash['name']} ({dist_t:.1f} m)")

            # -------------------------------------------------
            # ESTADO C: SECUENCIA CINEMÁTICA DEL GESTO DE RECOLECCIÓN
            # -------------------------------------------------
            # Paso 1: Orientar el brazo y abrir pinzas
            elif auto_state == "APUNTAR_PINZA":
                set_drive_velocities(0.0, 0.0)
                t_pos = current_target_trash["node"].getPosition() if current_target_trash else (rx + 1.4, ry, 0.04)
                dx = t_pos[0] - rx
                dy = t_pos[1] - ry
                target_yaw = math.atan2(dy, dx)
                rel_yaw = normalize_angle(target_yaw - ryaw)

                # Orientar la torreta hacia el residuo y abrir pinzas
                arm_targets["motor_brazo_yaw"] = max(-1.8, min(1.8, rel_yaw))
                arm_targets["motor_brazo_hombro"] = -0.10
                arm_targets["motor_brazo_codo"] = 0.45
                arm_targets["motor_pinza_izq"] = 0.32
                arm_targets["motor_pinza_der"] = -0.32
                apply_arm_positions()

                auto_timer += 1
                if auto_timer % 15 == 0:
                    update_hud(f"Apuntando pinzas a {current_target_trash['name']}...")
                if auto_timer > 35:
                    auto_state = "BAJAR_BRAZO"
                    auto_timer = 0

            # Paso 2: Descender el brazo hacia el residuo en el suelo
            elif auto_state == "BAJAR_BRAZO":
                set_drive_velocities(0.0, 0.0)
                # Extender hacia el suelo (Z~0.04m, X~1.45m)
                arm_targets["motor_brazo_hombro"] = 0.28
                arm_targets["motor_brazo_codo"] = 0.28
                arm_targets["motor_pinza_izq"] = 0.32
                arm_targets["motor_pinza_der"] = -0.32
                apply_arm_positions()

                auto_timer += 1
                if auto_timer % 15 == 0:
                    update_hud("Descendiendo garra hacia el residuo en suelo...")
                if auto_timer > 55:
                    auto_state = "CERRAR_PINZA"
                    auto_timer = 0

            # Paso 3: Cerrar las pinzas sujetando firmemente el residuo
            elif auto_state == "CERRAR_PINZA":
                set_drive_velocities(0.0, 0.0)
                arm_targets["motor_pinza_izq"] = -0.06
                arm_targets["motor_pinza_der"] = 0.06
                apply_arm_positions()

                auto_timer += 1
                if auto_timer % 15 == 0:
                    update_hud("Sujetando firmemente con pinzas de goma...")
                if auto_timer > 40:
                    auto_state = "LEVANTAR_RESIDUO"
                    auto_timer = 0

            # Paso 4: Levantar el residuo hacia arriba con el brazo
            elif auto_state == "LEVANTAR_RESIDUO":
                set_drive_velocities(0.0, 0.0)
                # Elevación del brazo principal
                arm_targets["motor_brazo_hombro"] = -0.75
                arm_targets["motor_brazo_codo"] = -0.40
                apply_arm_positions()

                # El residuo sigue a la pinza en 3D
                if current_target_trash:
                    # Progreso de elevación 0.0 -> 1.0
                    alpha = min(1.0, auto_timer / 45.0)
                    grip_pos = compute_gripper_world_pos(
                        rx, ry, ryaw,
                        arm_targets["motor_brazo_yaw"],
                        0.28 + (-0.75 - 0.28) * alpha,
                        0.28 + (-0.40 - 0.28) * alpha
                    )
                    tf = current_target_trash["node"].getField("translation")
                    tf.setSFVec3f(grip_pos)

                auto_timer += 1
                if auto_timer % 15 == 0:
                    update_hud("Elevando residuo con brazo robotico...")
                if auto_timer > 55:
                    auto_state = "GIRAR_HACIA_TOLVA"
                    auto_timer = 0

            # Paso 5: Girar 180° hacia la tolva trasera
            elif auto_state == "GIRAR_HACIA_TOLVA":
                set_drive_velocities(0.0, 0.0)
                arm_targets["motor_brazo_yaw"] = 3.14159
                arm_targets["motor_brazo_hombro"] = -0.80
                arm_targets["motor_brazo_codo"] = 0.50
                apply_arm_positions()

                # El residuo sigue la trayectoria de giro del extremo de la pinza
                if current_target_trash:
                    start_yaw = 0.0
                    alpha = min(1.0, auto_timer / 60.0)
                    cur_yaw = start_yaw + (3.14159 - start_yaw) * alpha
                    grip_pos = compute_gripper_world_pos(
                        rx, ry, ryaw,
                        cur_yaw,
                        -0.80,
                        0.50
                    )
                    tf = current_target_trash["node"].getField("translation")
                    tf.setSFVec3f(grip_pos)

                auto_timer += 1
                if auto_timer % 15 == 0:
                    update_hud("Girando brazo 180 hacia la tolva trasera...")
                if auto_timer > 70:
                    auto_state = "DEPOSITAR_EN_TOLVA"
                    auto_timer = 0

            # Paso 6: Abrir pinzas y soltar residuo dentro de la tolva
            elif auto_state == "DEPOSITAR_EN_TOLVA":
                set_drive_velocities(0.0, 0.0)
                arm_targets["motor_pinza_izq"] = 0.32
                arm_targets["motor_pinza_der"] = -0.32
                apply_arm_positions()
                auto_timer += 1

                # Soltar residuo en ranura fija dentro del contenedor trasero
                if auto_timer == 15 and current_target_trash:
                    slot_x = -0.18 - (trash_collected % 3) * 0.09
                    slot_y = -0.12 + ((trash_collected // 3) % 3) * 0.12
                    slot_z = 0.62 + (trash_collected // 6) * 0.08

                    c_yaw = math.cos(ryaw)
                    s_yaw = math.sin(ryaw)
                    wx = rx + slot_x * c_yaw - slot_y * s_yaw
                    wy = ry + slot_x * s_yaw + slot_y * c_yaw
                    wz = 0.05 + slot_z

                    tf = current_target_trash["node"].getField("translation")
                    tf.setSFVec3f([wx, wy, wz])
                    current_target_trash["collected"] = True
                    trash_collected += 1
                    print(f"✨ [RECOLECCIÓN EXITOSA] '{current_target_trash['name']}' depositado en tolva! Total recogidos: {trash_collected}/{total_trash}", flush=True)

                if auto_timer % 15 == 0:
                    update_hud("Depositando residuo en la tolva...")
                if auto_timer > 45:
                    auto_state = "REGRESAR_POSE_PATRULLA"
                    auto_timer = 0

            # Paso 7: Retornar brazo a posición de patrulla y reanudar recorrido
            elif auto_state == "REGRESAR_POSE_PATRULLA":
                arm_targets["motor_brazo_yaw"] = 0.0
                arm_targets["motor_brazo_hombro"] = -0.45
                arm_targets["motor_brazo_codo"] = 1.35
                arm_targets["motor_pinza_izq"] = 0.0
                arm_targets["motor_pinza_der"] = 0.0
                apply_arm_positions()

                auto_timer += 1
                if auto_timer % 15 == 0:
                    update_hud("Retornando brazo a posicion de marcha...")
                if auto_timer > 45:
                    current_target_trash = None
                    auto_state = "PATRULLA_CIRCUITO"
                    auto_timer = 0
                    print("[RECORRIDO] Retomando barrido del circuito de la plaza...", flush=True)

        if step_count % 80 == 0:
            sys.stdout.write(
                f"\r[ESTADO: {mode:9s} - {auto_state:20s}] | Limpiados: {trash_collected:2d}/{total_trash:2d} | Sector: {PLAZA_CIRCUIT[circuit_index][2]}\n"
            )
            sys.stdout.flush()

if __name__ == "__main__":
    main()
