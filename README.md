# 🤖 Robot Autónomo Limpiador de Basura — Ciénaga, Magdalena

[![Webots R2025a](https://img.shields.io/badge/Webots-R2025a-blue.svg)](https://cyberbotics.com/)
[![Webots Cloud](https://img.shields.io/badge/Webots.cloud-Simulation-green.svg)](https://webots.cloud/)
[![Python](https://img.shields.io/badge/Python-3.x-yellow.svg)](https://python.org)

Simulación robótica completa y modular desarrollada en **Webots R2025a** y **Blender 5.2**. El proyecto modela un robot móvil de tracción diferencial con brazo articulado de 4 Grados de Libertad (GDL) para recolección de residuos sólidos en un entorno urbano caribeño inspirado en las calles y costa de Ciénaga, Magdalena (Colombia).

---

## 🌐 Ver y Ejecutar en Webots Cloud

Puedes interactuar con la simulación directamente desde tu navegador sin instalar nada:

* 🚀 **Ejecutar Simulación Completa (Webots Cloud)**:  
  [https://webots.cloud/run?version=R2025a&url=https://github.com/Castillo-lewis/proyecto-cienaga-/blob/main/worlds/cienaga_limpiador.wbt](https://webots.cloud/run?version=R2025a&url=https://github.com/Castillo-lewis/proyecto-cienaga-/blob/main/worlds/cienaga_limpiador.wbt)

* 👁️ **Visor 3D Interactivo de la Escena**:  
  [https://webots.cloud/scene?url=https://github.com/Castillo-lewis/proyecto-cienaga-/blob/main/worlds/cienaga_limpiador.wbt](https://webots.cloud/scene?url=https://github.com/Castillo-lewis/proyecto-cienaga-/blob/main/worlds/cienaga_limpiador.wbt)

---

## 🏗️ Características del Robot

* **Tracción**: 4 ruedas motrices independientes con accionamiento diferencial (`HingeJoint` con amortiguación y fricción coulombiana de 1.2).
* **Brazo Manipulador (4 GDL + Pinza)**:
  1. Base giratoria (Yaw): eje Z, recorrido [-2.5, +2.5] rad.
  2. Articulación de hombro (Pitch): eje Y, recorrido [-1.2, +1.5] rad.
  3. Articulación de codo (Pitch): eje Y, recorrido [-2.2, +1.6] rad.
  4. Pinza recolectora paralela bimanual (Gripper) con pads de agarre.
* **Tolva de Reciclaje Posterior**: Contenedor integrado de 0.62 x 0.70 x 0.48 m para almacenar residuos recolectados.
* **Sensores a Bordo**:
  - `camara_superior`: Cámara RGB en mástil (640x480 px, FOV 1.15 rad).
  - `ds_frontal`: Sensor de distancia infrarrojo para detección directa de residuos.
  - `ds_izquierdo` y `ds_derecho`: Sensores ultrasónicos fronto-laterales para detección de bordillos y obstáculos.
  - `imu` y `gps`: Navegación y telemetría inercial.
* **Masa Total**: ~94 kg con centro de gravedad bajo para estabilidad dinámica.

---

## 🎮 Controles de Teleoperación (Modo Manual)

Haz clic sobre la ventana 3D de Webots para enfocarla y utiliza el teclado:

| Tecla | Acción |
|---|---|
| **Flecha Arriba / Abajo** | Marcha adelante / Marcha atrás |
| **Flecha Izquierda / Derecha** | Giro diferencial sobre su eje |
| **Espacio** | Frenar / Detener marcha |
| **W / S** | Subir / Bajar hombro del brazo (`motor_brazo_hombro`) |
| **A / D** | Girar base del brazo Yaw (`motor_brazo_yaw`) |
| **E / Q** | Extender / Plegar codo del brazo (`motor_brazo_codo`) |
| **G / H** | Abrir / Cerrar pinza recolectora (`motor_pinza`) |
| **R** | Posición de reposo / estacionamiento del brazo |
| **M** | **Alternar entre Modo MANUAL y Modo AUTÓNOMO** |

---

## 🧠 Modo Autónomo de Limpieza

Al presionar la tecla **`M`**, el robot entra en su máquina de estados autónoma:
1. **Patrullaje**: Avanza a velocidad de crucero monitoreando el asfalto.
2. **Evasión reactiva**: Si los sensores laterales detectan bordillos o paredes, corrige la trayectoria automáticamente.
3. **Recolección cinemática**: Al detectar un residuo al frente, se detiene, baja el brazo, abre la pinza, agarra el residuo, lo levanta y rota 180° hacia atrás depositándolo en la tolva posterior. Luego regresa a su pose de viaje y reanuda el patrullaje.

---

## 🌴 Entorno de Ciénaga, Magdalena

El mundo virtual reproduce los elementos característicos de Ciénaga:
* Calzada principal de 48 metros con marcas viales y andenes físicos.
* 12 casas de arquitectura colonial caribeña (6 al norte y 6 al sur).
* Mural conmemorativo *"100 AÑOS CIÉNAGA MAGDALENA"*.
* Palmeras y árboles tropicales de la región costera.
* Postes de alumbrado público con iluminación cálida.
* Sector de playa y fondo marítimo caribeño.
* Diversos tipos de residuos interactivos (botellas plásticas, latas, papel arrugado, bolsas de basura, cajas).

---

## 📁 Estructura del Repositorio

```
.
├── webots.yaml                       # Descriptor de publicación para Webots.cloud
├── Dockerfile                        # Imagen de ejecución para Webots.cloud
├── abrir_en_webots.bat               # Lanzador local para Windows
├── worlds/
│   ├── cienaga_limpiador.wbt         # Mundo principal de simulación
│   └── .cienaga_limpiador.jpg        # Portada / Miniatura para Webots Cloud
├── controllers/
│   └── robot_limpiador_controller/
│       └── robot_limpiador_controller.py # Controlador principal en Python
├── protos/
│   └── RobotLimpiadorCienaga.proto   # Nodo PROTO reutilizable del robot
└── meshes/                           # Mallas geométricas y materiales (.obj / .mtl)
```

---

## 💻 Ejecución Local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Castillo-lewis/proyecto-cienaga-.git
   ```
2. Ejecuta `abrir_en_webots.bat` o abre `worlds/cienaga_limpiador.wbt` directamente en Webots R2025a.
