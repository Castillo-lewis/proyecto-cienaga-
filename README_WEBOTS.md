# Proyecto Webots: Robot Autonomo Limpiador de Basura (Cienaga, Magdalena)

Este proyecto traslada el modelo 3D y entorno de Blender a una simulacion completa y funcional en **Webots R2025a**.

---

## 🚀 Como Abrir la Simulacion

### Opcion 1: Acceso Directo (Recomendado)
Haz doble clic en el archivo:
`abrir_en_webots.bat`

### Opcion 2: Desde la Interfaz de Webots
1. Abre **Webots**.
2. En el menu superior, selecciona **File -> Open World...** (o `Ctrl + Shift + O`).
3. Navega y selecciona el archivo:
   `C:\Users\lewis\Documents\Robot_Limpiador_Cienaga\worlds\cienaga_limpiador.wbt`
4. Presiona el boton **Play** (▶) en la barra superior de Webots.

---

## 🎮 Controles de Teleoperacion (Modo Manual)

Haz clic sobre la ventana 3D de Webots para enfocarla y usa tu teclado:

| Tecla | Accion |
|---|---|
| **Flecha Arriba** | Avanzar adelante |
| **Flecha Abajo** | Retroceder |
| **Flecha Izquierda** | Giro sobre su eje a la izquierda |
| **Flecha Derecha** | Giro sobre su eje a la derecha |
| **Barra Espaciadora** | Frenar / Detener marcha |
| **W / S** | Subir / Bajar hombro del brazo robotico (`motor_brazo_hombro`) |
| **A / D** | Rotar base giratoria del brazo (`motor_brazo_yaw`) |
| **E / Q** | Extender / Plegar codo del brazo (`motor_brazo_codo`) |
| **G / H** | Abrir / Cerrar pinza recolectora (`motor_pinza_izq` / `motor_pinza_der`) |
| **R** | Reestablecer brazo a posicion de reposo |
| **M** | **Alternar entre Modo MANUAL y Modo AUTONOMO** |

---

## 🤖 Modo Autonomo (Patrullaje y Limpieza Inteligente)

Al presionar la tecla **`M`**:
1. El robot entra en patrullaje constante a lo largo de la calle de Cienaga.
2. Utiliza los sensores frontales y ultrasonicos laterales para mantenerse en la via y esquivar obstaculos y bordillos.
3. Al detectar residuos o basuras directamente al frente:
   - Se detiene.
   - Despliega el brazo de 4 GDL hacia abajo con la pinza abierta.
   - Sujeta el residuo con la pinza.
   - Eleva el residuo y gira 180° hacia atras sobre el `Contenedor_Basura`.
   - Abre la pinza depositando el residuo en la tolva de reciclaje.
   - Regresa a su pose de viaje y continua limpiando.

---

## 📁 Estructura del Proyecto Webots

```
Robot_Limpiador_Cienaga/
├── abrir_en_webots.bat               # Lanzador rapido con un clic
├── worlds/
│   ├── cienaga_limpiador.wbt         # Escena principal con iluminacion caribena y fisicas
│   └── meshes/                       # Copia local de mallas para renderizado Webots
├── controllers/
│   └── robot_limpiador_controller/
│       └── robot_limpiador_controller.py # Controlador en Python con teleoperacion y logica autonoma
├── protos/
│   ├── RobotLimpiadorCienaga.proto   # Nodo PROTO reutilizable del robot
│   └── meshes/                       # Mallas vinculadas al PROTO
├── meshes/                           # Modelos 3D exportados (.obj + .mtl):
│   ├── chasis.obj                    # Chasis, tolva de basura y mastil
│   ├── rueda.obj                     # Conjunto rueda, neumatico y llanta
│   ├── brazo_base.obj                # Base giratoria (Yaw)
│   ├── brazo_seg1.obj                # Segmento 1 (Hombro)
│   ├── brazo_seg2.obj                # Segmento 2 (Codo)
│   ├── gripper_base.obj              # Muneca del efector final
│   ├── gripper_finger_left.obj       # Dedo izquierdo de la pinza
│   ├── gripper_finger_right.obj      # Dedo derecho de la pinza
│   ├── entorno_calle.obj             # Calzada, anden y bordillos
│   ├── entorno_casas.obj             # Arquitectura colonial caribena de Cienaga
│   ├── entorno_flora.obj             # Palmeras y arboles tropicales
│   ├── entorno_postes.obj            # Postes de alumbrado publico
│   ├── entorno_mural.obj             # Mural conmemorativo "100 Anos Cienaga"
│   ├── entorno_costa.obj             # Mar Caribe, playa y colinas
│   └── basura_*.obj                  # Botellas, latas, papeles arrugados, cajas y bolsas
└── scripts/
    └── cienaga_robot_scene.py        # Generador original de Blender
```

---

## ⚙️ Especificaciones Tecnicas del Robot

- **Traccion**: Traccion diferencial / skid-steer de 4 ruedas motrices (`motor_rueda_DI`, `motor_rueda_DD`, `motor_rueda_TI`, `motor_rueda_TD`).
- **Brazo Robotico**: 4 Grados de Libertad (Base Yaw, Hombro Pitch, Codo Pitch, Pinza paralela bimanual).
- **Sensores a Bordo**:
  - `camara_superior`: Camara RGB montada en mastil (640x480).
  - `ds_frontal`: Sensor de distancia infrarrojo frontal para deteccion de basuras.
  - `ds_izquierdo` / `ds_derecho`: Sensores ultrasonicos angulados a ±20° para deteccion de bordillos y paredes.
  - `imu` e `gps`: Unidades inerciales y de posicionamiento global.
- **Masa total del robot**: ~94 kg con centro de gravedad bajo para maxima estabilidad.
