"""
Controlador Principal para el Robot Limpiador de Basura de Cienaga, Magdalena.
Soporta dos modos:
  1. MANUAL (Teclado): Flechas de direccion + controles de brazo articular.
  2. AUTONOMO (Patrullaje y Limpieza): Navegacion reactiva con sensores y rutina de recoleccion.
"""

import sys
import math
from controller import Robot, Keyboard, Camera, DistanceSensor, Motor

def main():
    robot = Robot()
    time_step = int(robot.getBasicTimeStep())
    if time_step <= 0:
        time_step = 16

    print("=" * 65)
    print(" ROBOT RECOLECTOR Y LIMPIADOR URBANO - CIENAGA, MAGDALENA")
    print(" Webots R2025a Simulation Controller")
    print("=" * 65)
    print(" CONTROLES DE TECLADO (Modo Manual):")
    print("   [Flecha Arriba / Abajo]   : Avanzar / Retroceder")
    print("   [Flecha Izq / Der]       : Giro diferencial Izquierda / Derecha")
    print("   [ESPACIO]                 : Frenar / Detener marcha")
    print("   [W / S]                   : Subir / Bajar hombro del brazo")
    print("   [A / D]                   : Rotar base del brazo (Yaw)")
    print("   [E / Q]                   : Extender / Contraer codo del brazo")
    print("   [G / H]                   : Abrir / Cerrar pinza (Gripper)")
    print("   [R]                       : Posicion de descanso del brazo")
    print("   [M]                       : Cambiar entre Modo MANUAL y AUTONOMO")
    print("=" * 65)

    # ---------------------------------------------------------
    # 1. MOTORES DE TRACCION (4 Ruedas Motrices)
    # ---------------------------------------------------------
    wheel_names = [
        "motor_rueda_DI", "motor_rueda_DD",
        "motor_rueda_TI", "motor_rueda_TD"
    ]
    wheels = {}
    for name in wheel_names:
        motor = robot.getDevice(name)
        if motor:
            motor.setPosition(float('inf'))
            motor.setVelocity(0.0)
            wheels[name] = motor
        else:
            print(f"[AVISO] No se encontro el dispositivo de rueda: {name}")

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
    # 2. MOTORES DEL BRAZO ROBOTICO (4 GDL + PINZA)
    # ---------------------------------------------------------
    arm_names = [
        "motor_brazo_yaw", "motor_brazo_hombro",
        "motor_brazo_codo", "motor_pinza_izq", "motor_pinza_der"
    ]
    arm_motors = {}
    for name in arm_names:
        m = robot.getDevice(name)
        if m:
            arm_motors[name] = m
        else:
            print(f"[AVISO] No se encontro motor del brazo: {name}")

    # Posiciones objetivo del brazo
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
    # 3. SENSORES DE DISTANCIA Y CAMARA
    # ---------------------------------------------------------
    ds_front = robot.getDevice("ds_frontal")
    if ds_front:
        ds_front.enable(time_step)

    ds_left = robot.getDevice("ds_izquierdo")
    if ds_left:
        ds_left.enable(time_step)

    ds_right = robot.getDevice("ds_derecho")
    if ds_right:
        ds_right.enable(time_step)

    camera = robot.getDevice("camara_superior")
    if camera:
        camera.enable(time_step * 2)

    keyboard = robot.getKeyboard()
    keyboard.enable(time_step)

    # ---------------------------------------------------------
    # ESTADO DEL ROBOT
    # ---------------------------------------------------------
    mode = "MANUAL"  # "MANUAL" o "AUTONOMO"
    auto_state = "PATRULLAR"
    auto_timer = 0
    trash_collected = 0

    MAX_SPEED = 6.0
    TURN_SPEED = 3.5

    last_key_press = -1
    log_counter = 0

    while robot.step(time_step) != -1:
        log_counter += 1

        # Leer distancias de sensores
        val_front = ds_front.getValue() if ds_front else 0.0
        val_left = ds_left.getValue() if ds_left else 0.0
        val_right = ds_right.getValue() if ds_right else 0.0

        # Lectura de teclado
        key = keyboard.getKey()
        if key > 0:
            if key == ord('M') and last_key_press != ord('M'):
                mode = "AUTONOMO" if mode == "MANUAL" else "MANUAL"
                print(f"\n>>> CAMBIO DE MODO: {mode} <<<")
                if mode == "MANUAL":
                    set_drive_velocities(0.0, 0.0)
                else:
                    auto_state = "PATRULLAR"
                    auto_timer = 0
            last_key_press = key
        else:
            last_key_press = -1

        # -----------------------------------------------------
        # MODO 1: TELEOPERACION MANUAL
        # -----------------------------------------------------
        if mode == "MANUAL":
            left_v = 0.0
            right_v = 0.0

            # Manejo de traccion
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

            # Manejo del Brazo Robotico
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
                arm_targets["motor_pinza_izq"] = 0.25
                arm_targets["motor_pinza_der"] = -0.25
            elif key == ord('H'):  # Cerrar pinza
                arm_targets["motor_pinza_izq"] = -0.05
                arm_targets["motor_pinza_der"] = 0.05

            if key == ord('R'):  # Reset/Park
                arm_targets["motor_brazo_yaw"] = 0.0
                arm_targets["motor_brazo_hombro"] = 0.35
                arm_targets["motor_brazo_codo"] = -0.65
                arm_targets["motor_pinza_izq"] = 0.0
                arm_targets["motor_pinza_der"] = 0.0

            apply_arm_positions()

        # -----------------------------------------------------
        # MODO 2: NAVEGACION Y RECOLECCION AUTONOMA
        # -----------------------------------------------------
        else:
            if auto_state == "PATRULLAR":
                # Avanzar a velocidad de crucero patrullando la calle
                set_drive_velocities(4.0, 4.0)

                # Deteccion de residuo al frente (objeto cercano detectado por IR frontal)
                if 200.0 < val_front < 1200.0:
                    print("[AUTONOMO] Residuo detectado al frente. Iniciando rutina de recoleccion...")
                    set_drive_velocities(0.0, 0.0)
                    auto_state = "BAJAR_BRAZO"
                    auto_timer = 0
                # Obstaculo frontal o bordillo muy cercano
                elif val_front >= 1200.0 or val_left > 1500.0:
                    auto_state = "EVITAR_OBSTACULO"
                    auto_timer = 40
                elif val_right > 1500.0:
                    auto_state = "CORREGIR_IZQ"
                    auto_timer = 30

            elif auto_state == "EVITAR_OBSTACULO":
                # Retroceder y girar
                set_drive_velocities(-2.5, -3.8)
                auto_timer -= 1
                if auto_timer <= 0:
                    auto_state = "PATRULLAR"

            elif auto_state == "CORREGIR_IZQ":
                set_drive_velocities(2.0, 3.8)
                auto_timer -= 1
                if auto_timer <= 0:
                    auto_state = "PATRULLAR"

            # Secuencia cinemática de recoleccion con el brazo de 4 GDL
            elif auto_state == "BAJAR_BRAZO":
                # Posicionar brazo hacia abajo y abrir pinza
                arm_targets["motor_brazo_yaw"] = 0.0
                arm_targets["motor_brazo_hombro"] = -0.45
                arm_targets["motor_brazo_codo"] = 0.75
                arm_targets["motor_pinza_izq"] = 0.25
                arm_targets["motor_pinza_der"] = -0.25
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 50:
                    auto_state = "CERRAR_PINZA"
                    auto_timer = 0

            elif auto_state == "CERRAR_PINZA":
                # Sujetar residuo
                arm_targets["motor_pinza_izq"] = -0.1
                arm_targets["motor_pinza_der"] = 0.1
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 40:
                    auto_state = "LEVANTAR_RESIDUO"
                    auto_timer = 0

            elif auto_state == "LEVANTAR_RESIDUO":
                # Elevar brazo
                arm_targets["motor_brazo_hombro"] = 0.8
                arm_targets["motor_brazo_codo"] = -0.8
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 45:
                    auto_state = "GIRAR_HACIA_CONTENEDOR"
                    auto_timer = 0

            elif auto_state == "GIRAR_HACIA_CONTENEDOR":
                # Girar 180 deg hacia el contenedor trasero
                arm_targets["motor_brazo_yaw"] = 2.4
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 55:
                    auto_state = "DEPOSITAR_EN_CONTENEDOR"
                    auto_timer = 0

            elif auto_state == "DEPOSITAR_EN_CONTENEDOR":
                # Abrir pinza sobre el contenedor trasero
                arm_targets["motor_pinza_izq"] = 0.25
                arm_targets["motor_pinza_der"] = -0.25
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 40:
                    trash_collected += 1
                    print(f"[EXITO] Residuo depositado en el contenedor! Total recolectados: {trash_collected}")
                    auto_state = "REGRESAR_POSICION_VIAJE"
                    auto_timer = 0

            elif auto_state == "REGRESAR_POSICION_VIAJE":
                # Regresar a pose de patrulla
                arm_targets["motor_brazo_yaw"] = 0.0
                arm_targets["motor_brazo_hombro"] = 0.35
                arm_targets["motor_brazo_codo"] = -0.65
                arm_targets["motor_pinza_izq"] = 0.0
                arm_targets["motor_pinza_der"] = 0.0
                apply_arm_positions()
                auto_timer += 1
                if auto_timer > 50:
                    auto_state = "PATRULLAR"
                    auto_timer = 0

        # Telemetria en consola cada ~1.5 segundos
        if log_counter % 80 == 0:
            sys.stdout.write(
                f"\r[ESTADO: {mode:9s}] | Sensores: F={val_front:5.1f} L={val_left:5.1f} R={val_right:5.1f} | Residuos: {trash_collected} | Brazo: {arm_targets['motor_brazo_hombro']:+.2f} rad   "
            )
            sys.stdout.flush()

if __name__ == "__main__":
    main()
