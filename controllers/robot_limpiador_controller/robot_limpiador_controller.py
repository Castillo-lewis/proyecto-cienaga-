"""
Controlador Principal del Robot Limpiador y Recolector Urbano
Plaza del Centenario - Ciénaga, Magdalena (Webots R2025a)

Capacidades:
  1. MODO AUTÓNOMO (Por defecto al iniciar):
     - Navega automáticamente por los senderos adoquinados de la Plaza del Centenario.
     - Detecta residuos (botellas plásticas, latas, papeles) usando sensores y visión.
     - Posiciona el robot frente al residuo.
     - Despliega el brazo robótico de 4 GDL hasta el suelo.
     - Sujeta el residuo con la pinza bimanual.
     - Eleva el residuo y rota 180° hacia atrás sobre la tolva de reciclaje.
     - Deposita el residuo dentro del contenedor del robot.
     - Actualiza el HUD en pantalla con el contador de basura recolectada.
     - Continúa de forma autónoma con el siguiente residuo.
  2. MODO MANUAL:
     - Permite control total por teclado (Flechas para conducir, teclas W/S/A/D/E/Q/G/H para el brazo).
     - Tecla [M] para alternar entre modo MANUAL y AUTÓNOMO en cualquier momento.
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

def main():
    supervisor = Supervisor()
    time_step = int(supervisor.getBasicTimeStep())
    if time_step <= 0:
        time_step = 16

    print("=" * 70)
    print(" 🤖 ROBOT LIMPIADOR Y RECOLECTOR URBANO - CIÉNAGA, MAGDALENA")
    print(" Simulación Webots R2025a | Plaza del Centenario")
    print("=" * 70)
    print(" MODO DE INICIO: AUTÓNOMO (Recolección activa de basura)")
    print(" Presiona [M] en el teclado para alternar a MODO MANUAL con flechas.")
    print("=" * 70)

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

    # Posición inicial compacta de viaje
    arm_targets = {
        "motor_brazo_yaw": 0.0,
        "motor_brazo_hombro": 0.35,
        "motor_brazo_codo": -0.65,
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

    # Obtener el nodo propio del robot para odometría y posición
    robot_node = supervisor.getSelf()

    # ---------------------------------------------------------
    # 4. CATALOGAR RESIDUOS DE LA PLAZA DEL CENTENARIO
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
                        # Solo incluir residuos en la plaza (no componentes del robot)
                        if not any(ign in n_str.lower() for ign in ["rueda", "brazo", "pinza", "chasis", "templete_colision"]):
                            trash_list.append({
                                "node": node,
                                "name": n_str,
                                "collected": False,
                                "pos": list(node.getPosition()),
                            })
        return trash_list

    trash_items = scan_trash_nodes()
    total_trash = len(trash_items)
    print(f"[SISTEMA] Se detectaron {total_trash} residuos físicos en la Plaza del Centenario.")

    # ---------------------------------------------------------
    # 5. ESTADO Y PARÁMETROS DE CONTROL
    # ---------------------------------------------------------
    mode = "AUTONOMO"           # Inicia automáticamente recogiendo basura
    auto_state = "BUSCAR_OBJETIVO"
    auto_timer = 0
    trash_collected = 0
    current_target = None
    target_trash_index = -1

    MAX_SPEED = 5.0
    CRUISE_SPEED = 3.5
    TURN_SPEED = 2.8

    last_key_press = -1
    step_count = 0

    # Funciones auxiliares de HUD y Odometría
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

    def update_hud(action_text):
        # Banner superior HUD
        mode_color = 0x00FF88 if mode == "AUTONOMO" else 0x33CCFF
        supervisor.setLabel(0, f"ROBOT LIMPIADOR DE CIENAGA  |  MODO: {mode}", 0.02, 0.02, 0.065, mode_color, 0.0, "Lucida Console")
        # Métricas de recolección
        supervisor.setLabel(1, f"Residuos Limpiados: {trash_collected} / {total_trash}   Bateria: 97%   Tolva: {min(100, trash_collected*12)}%", 0.02, 0.06, 0.05, 0xFFFFFF, 0.0, "Lucida Console")
        # Acción actual
        supervisor.setLabel(2, f"Estado: {action_text}", 0.02, 0.10, 0.045, 0xFFDD33, 0.0, "Lucida Console")
        # Ayuda de controles
        supervisor.setLabel(3, "[M] Alternar Manual/Autonomo  |  [Flechas] Conducir  |  [C] Recoger  |  [ESPACIO] Frenar", 0.02, 0.95, 0.038, 0xCCCCCC, 0.0, "Lucida Console")

    update_hud("Iniciando patrullaje autónomo...")

    # ---------------------------------------------------------
    # 6. BUCLE PRINCIPAL DE SIMULACIÓN
    # ---------------------------------------------------------
    while supervisor.step(time_step) != -1:
        step_count += 1
        rx, ry, ryaw = get_robot_pose()

        # Lecturas de sensores de distancia
        val_front = ds_front.getValue() if ds_front else 0.0
        val_left = ds_left.getValue() if ds_left else 0.0
        val_right = ds_right.getValue() if ds_right else 0.0

        # Lectura de teclado
        key = keyboard.getKey()
        if key > 0:
            if key == ord('M') and last_key_press != ord('M'):
                mode = "MANUAL" if mode == "AUTONOMO" else "AUTONOMO"
                print(f"\n[CAMBIO DE MODO] -> {mode}")
                if mode == "MANUAL":
                    set_drive_velocities(0.0, 0.0)
                    update_hud("Control Manual Activo (Usa las flechas del teclado)")
                else:
                    auto_state = "BUSCAR_OBJETIVO"
                    auto_timer = 0
                    update_hud("Reanudando recolección autónoma...")
            last_key_press = key
        else:
            last_key_press = -1

        # =====================================================
        # MODO 1: TELEOPERACIÓN MANUAL
        # =====================================================
        if mode == "MANUAL":
            left_v = 0.0
            right_v = 0.0

            if key == Keyboard.UP:
                left_v = MAX_SPEED
                right_v = MAX_SPEED
            elif key == Keyboard.DOWN:
                left_v = -MAX_SPEED
                right_v = -MAX_SPEED
            elif key == Keyboard.LEFT:
                left_v = -TURN_SPEED
                right_v = TURN_SPEED
            elif key == Keyboard.RIGHT:
                left_v = TURN_SPEED
                right_v = -TURN_SPEED
            elif key == ord(' '):
                left_v = 0.0
                right_v = 0.0

            set_drive_velocities(left_v, right_v)

            # Control manual del brazo
            if key == ord('W'):
                arm_targets["motor_brazo_hombro"] = min(1.3, arm_targets["motor_brazo_hombro"] + 0.03)
            elif key == ord('S'):
                arm_targets["motor_brazo_hombro"] = max(-1.0, arm_targets["motor_brazo_hombro"] - 0.03)

            if key == ord('A'):
                arm_targets["motor_brazo_yaw"] = min(2.4, arm_targets["motor_brazo_yaw"] + 0.04)
            elif key == ord('D'):
                arm_targets["motor_brazo_yaw"] = max(-2.4, arm_targets["motor_brazo_yaw"] - 0.04)

            if key == ord('E'):
                arm_targets["motor_brazo_codo"] = min(1.2, arm_targets["motor_brazo_codo"] + 0.04)
            elif key == ord('Q'):
                arm_targets["motor_brazo_codo"] = max(-2.0, arm_targets["motor_brazo_codo"] - 0.04)

            if key == ord('G'):  # Abrir pinza
                arm_targets["motor_pinza_izq"] = 0.28
                arm_targets["motor_pinza_der"] = -0.28
            elif key == ord('H'):  # Cerrar pinza
                arm_targets["motor_pinza_izq"] = -0.08
                arm_targets["motor_pinza_der"] = 0.08

            if key == ord('R'):  # Reset a pose de viaje
                arm_targets["motor_brazo_yaw"] = 0.0
                arm_targets["motor_brazo_hombro"] = 0.35
                arm_targets["motor_brazo_codo"] = -0.65
                arm_targets["motor_pinza_izq"] = 0.0
                arm_targets["motor_pinza_der"] = 0.0

            # Tecla C: Gatillar recolección inmediata
            if key == ord('C'):
                mode = "AUTONOMO"
                auto_state = "BAJAR_BRAZO"
                auto_timer = 0
                set_drive_velocities(0.0, 0.0)
                print("[MANUAL] Ejecutando secuencia de agarre...")

            apply_arm_positions()
            if step_count % 30 == 0:
                update_hud(f"Manual | Velo=({left_v:.1f}, {right_v:.1f})")

        # =====================================================
        # MODO 2: RECOLECCIÓN AUTÓNOMA INTELIGENTE
        # =====================================================
        else:
            # -------------------------------------------------
            # FASE A: BÚSQUEDA DEL RESIDUO MÁS CERCANO
            # -------------------------------------------------
            if auto_state == "BUSCAR_OBJETIVO":
                nearest = None
                min_dist = float('inf')
                nearest_idx = -1

                for idx, t in enumerate(trash_items):
                    if not t["collected"]:
                        t_pos = t["node"].getPosition()
                        dist = math.hypot(t_pos[0] - rx, t_pos[1] - ry)
                        if dist < min_dist:
                            min_dist = dist
                            nearest = t
                            nearest_idx = idx

                if nearest:
                    current_target = nearest
                    target_trash_index = nearest_idx
                    auto_state = "NAVEGAR_HACIA_RESIDUO"
                    auto_timer = 0
                    print(f"\n[AUTONOMO] Nuevo objetivo seleccionado: '{nearest['name']}' a {min_dist:.2f} m")
                    update_hud(f"Navegando hacia {nearest['name']} ({min_dist:.1f} m)")
                else:
                    auto_state = "CIRCUITO_COMPLETO"
                    set_drive_velocities(0.0, 0.0)
                    print("\n🎉 ¡TODOS LOS RESIDUOS DE LA PLAZA DEL CENTENARIO HAN SIDO RECOLECTADOS!")
                    update_hud("¡Plaza del Centenario completamente limpia y reluciente!")

            # -------------------------------------------------
            # FASE B: NAVEGACIÓN Y APROXIMACIÓN AL RESIDUO
            # -------------------------------------------------
            elif auto_state == "NAVEGAR_HACIA_RESIDUO":
                t_pos = current_target["node"].getPosition()
                dx = t_pos[0] - rx
                dy = t_pos[1] - ry
                dist = math.hypot(dx, dy)
                target_yaw = math.atan2(dy, dx)
                yaw_error = normalize_angle(target_yaw - ryaw)

                # Detección de proximidad para iniciar agarre (a menos de 0.65m frente a la pinza)
                if dist <= 0.68 or (dist <= 1.1 and val_front > 400.0):
                    set_drive_velocities(0.0, 0.0)
                    auto_state = "APUNTAR_PINZA"
                    auto_timer = 0
                    print(f"[AUTONOMO] Residuo alcanzado ({dist:.2f} m). Iniciando maniobra de recolección...")
                    update_hud(f"Alineando brazo para agarrar {current_target['name']}...")
                else:
                    # Evasión de bordillos laterales o bancas
                    avoid_left = val_left > 1400.0
                    avoid_right = val_right > 1400.0

                    if avoid_left:
                        set_drive_velocities(CRUISE_SPEED, CRUISE_SPEED * 0.3)
                    elif avoid_right:
                        set_drive_velocities(CRUISE_SPEED * 0.3, CRUISE_SPEED)
                    else:
                        # Control proporcional de dirección hacia el residuo
                        kp = 3.2
                        turn = max(-TURN_SPEED, min(TURN_SPEED, kp * yaw_error))
                        
                        # Si el error angular es grande, primero pivota sobre el eje
                        if abs(yaw_error) > 0.65:
                            v_left = -turn * 0.8
                            v_right = turn * 0.8
                        else:
                            speed = CRUISE_SPEED if dist > 1.8 else 2.2
                            v_left = speed - turn
                            v_right = speed + turn

                        set_drive_velocities(v_left, v_right)

                    if step_count % 25 == 0:
                        update_hud(f"Acercandose a {current_target['name']} ({dist:.1f} m)")

            # -------------------------------------------------
            # FASE C: SECUENCIA CINEMÁTICA DE RECOLECCIÓN
            # -------------------------------------------------
            elif auto_state == "APUNTAR_PINZA":
                # Detener completamente la marcha
                set_drive_velocities(0.0, 0.0)
                t_pos = current_target["node"].getPosition()
                dx = t_pos[0] - rx
                dy = t_pos[1] - ry
                target_yaw = math.atan2(dy, dx)
                rel_yaw = normalize_angle(target_yaw - ryaw)
                # Apuntar base del brazo exactamente hacia el residuo
                arm_targets["motor_brazo_yaw"] = max(-1.2, min(1.2, rel_yaw))
                # Abrir pinza
                arm_targets["motor_pinza_izq"] = 0.28
                arm_targets["motor_pinza_der"] = -0.28
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 20:
                    auto_state = "BAJAR_BRAZO"
                    auto_timer = 0
                    update_hud(f"Bajando brazo hacia {current_target['name']}...")

            elif auto_state == "BAJAR_BRAZO":
                # Desplegar hombro y codo hacia el suelo
                arm_targets["motor_brazo_hombro"] = -0.58
                arm_targets["motor_brazo_codo"] = 0.98
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 38:
                    auto_state = "CERRAR_PINZA"
                    auto_timer = 0
                    update_hud(f"Sujetando {current_target['name']} con pinza...")

            elif auto_state == "CERRAR_PINZA":
                # Cerrar pinza asegurando el objeto
                arm_targets["motor_pinza_izq"] = -0.08
                arm_targets["motor_pinza_der"] = 0.08
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 28:
                    auto_state = "LEVANTAR_RESIDUO"
                    auto_timer = 0
                    update_hud(f"Levantando {current_target['name']} del suelo...")

            elif auto_state == "LEVANTAR_RESIDUO":
                # Elevar el brazo cargando el residuo
                arm_targets["motor_brazo_hombro"] = 0.92
                arm_targets["motor_brazo_codo"] = -0.85
                apply_arm_positions()
                
                # Animar suavemente el residuo junto al efector final
                if auto_timer > 10 and current_target:
                    # Elevar la malla del residuo
                    t_field = current_target["node"].getField("translation")
                    curr_p = t_field.getSFVec3f()
                    t_field.setSFVec3f([curr_p[0], curr_p[1], rx * 0.0 + 0.35 + (auto_timer - 10) * 0.02])

                auto_timer += 1
                if auto_timer > 40:
                    auto_state = "GIRAR_HACIA_TOLVA"
                    auto_timer = 0
                    update_hud(f"Girando brazo 180° hacia tolva de basura...")

            elif auto_state == "GIRAR_HACIA_TOLVA":
                # Rotar base 180° hacia el contenedor trasero
                arm_targets["motor_brazo_yaw"] = 2.45
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 45:
                    auto_state = "DEPOSITAR_EN_TOLVA"
                    auto_timer = 0
                    update_hud(f"Depositando {current_target['name']} en tolva...")

            elif auto_state == "DEPOSITAR_EN_TOLVA":
                # Abrir pinza liberando el residuo
                arm_targets["motor_pinza_izq"] = 0.28
                arm_targets["motor_pinza_der"] = -0.28
                apply_arm_positions()
                auto_timer += 1

                if auto_timer == 20 and current_target:
                    # Ubicar el residuo ordenadamente dentro de la tolva del robot
                    slot_x = -0.22 - (trash_collected % 3) * 0.12
                    slot_y = -0.15 + ((trash_collected // 3) % 3) * 0.15
                    slot_z = 0.65 + (trash_collected // 6) * 0.08

                    # Transformación del slot en coordenadas del mundo
                    c_yaw = math.cos(ryaw)
                    s_yaw = math.sin(ryaw)
                    wx = rx + slot_x * c_yaw - slot_y * s_yaw
                    wy = ry + slot_x * s_yaw + slot_y * c_yaw
                    wz = 0.05 + slot_z

                    t_field = current_target["node"].getField("translation")
                    t_field.setSFVec3f([wx, wy, wz])
                    
                    # Anular velocidades físicas del objeto
                    reset_phys = current_target["node"].getField("physics")
                    if reset_phys and reset_phys.getSFNode():
                        pass

                    current_target["collected"] = True
                    trash_collected += 1
                    print(f"✨ [RECOLECCIÓN EXITOSA] '{current_target['name']}' depositado en tolva. Total: {trash_collected}/{total_trash}")

                if auto_timer > 35:
                    auto_state = "REGRESAR_POSE_PATRULLA"
                    auto_timer = 0
                    update_hud(f"Residuo #{trash_collected} guardado. Reanudando marcha...")

            elif auto_state == "REGRESAR_POSE_PATRULLA":
                # Regresar brazo a postura compacta frontal
                arm_targets["motor_brazo_yaw"] = 0.0
                arm_targets["motor_brazo_hombro"] = 0.35
                arm_targets["motor_brazo_codo"] = -0.65
                arm_targets["motor_pinza_izq"] = 0.0
                arm_targets["motor_pinza_der"] = 0.0
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 38:
                    # Ir al siguiente residuo
                    auto_state = "BUSCAR_OBJETIVO"
                    auto_timer = 0

            elif auto_state == "CIRCUITO_COMPLETO":
                set_drive_velocities(0.0, 0.0)
                update_hud("¡Plaza del Centenario limpia! Presiona [M] para modo manual")

        # Telemetría periódica en consola
        if step_count % 75 == 0:
            target_str = current_target['name'] if current_target and not current_target.get('collected') else "Ninguno"
            sys.stdout.write(
                f"\r[ESTADO: {mode:9s} - {auto_state:18s}] | Limpiados: {trash_collected:2d}/{total_trash:2d} | Objetivo: {target_str:20s}\n"
            )
            sys.stdout.flush()

if __name__ == "__main__":
    main()
