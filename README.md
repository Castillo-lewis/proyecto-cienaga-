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

## 🏛️ Entorno Histórico: Plaza del Centenario de Ciénaga, Magdalena

El plano de recolección de basura del robot recrea con fidelidad arquitectónica el corazón del centro histórico de Ciénaga:
* **El Templete Neoclásico (Monumento Central)**: Podio circular de 4 niveles de escalones, anillo concéntrico de 8 columnas clásicas, entablamento, balaustrada ornamental y cúpula con pináculo.
* **Iglesia San Juan Bautista**: Fachada colonial blanca, gran portal en arco con frontón, torre campanario de 24 metros con campanas de bronce, monumental cúpula de crucero con tambor octogonal y pérgola lateral blanca.
* **La Plaza del Centenario**: Explanada peatonal adoquinada de 52 × 42 m con rotonda circular alrededor del Templete, jardineras concéntricas con flores caribeñas, senderos de losas, 10 bancas coloniales de hierro forjado y faroles ornamentales.
* **Vegetación Típica**: Palmeras reales de gran porte y árboles frondosos tropicales (almendros y ficus) idénticos a los del parque central.
* **Fondo de la Sierra Nevada de Santa Marta**: Relieve montañoso imponente que corona la perspectiva en el horizonte.
* **Circuito de Residuos Dinámicos**: 12 puntos de basura interactivos (botellas, latas, papeles arrugados, cajas y bolsas) ubicados estratégicamente sobre los senderos peatonales y alrededor del Templete para su recolección y limpieza autónoma.

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

## 📊 Gestión del Proyecto y Tablero Kanban (GitHub Projects)

El desarrollo del proyecto se gestiona mediante un tablero ágil estructurado en los 3 bloques principales de trabajo:

```
┌───────────────────────────┬───────────────────────────┬───────────────────────────┐
│       📋 TO DO            │     🔄 IN PROGRESS        │         ✅ DONE           │
│      (Por Hacer)          │      (En Progreso)        │       (Completado)        │
└───────────────────────────┴───────────────────────────┴───────────────────────────┘
```

---

### 1. 📋 Bloque TO DO (Por Hacer)

| ID | Tarea / Característica | Prioridad | Módulo | Descripción Técnica |
|---|---|:---:|:---:|---|
| **TODO-01** | **Mapeo 2D/3D y SLAM Urbano** | Alta | Navegación | Integración de algoritmo SLAM (Cartographer / RTAB-Map) utilizando la nube de puntos del sensor LiDAR en el mástil para cartografiado autónomo de la Plaza del Centenario. |
| **TODO-02** | **Algoritmo de Cobertura Sistemática** | Alta | Control | Implementación de patrón de barrido por celdas (Boustrophedon / Spanning Tree Coverage) para garantizar la limpieza del 100% de la superficie peatonal sin rutas redundantes. |
| **TODO-03** | **Sensor Óptico de Nivel de Tolva** | Media | Telemetría | Estimación volumétrica del nivel de basura dentro de la tolva mediante sensor TOF/óptico con retorno autónomo a estación de descarga municipal al llegar al 100%. |
| **TODO-04** | **Ciclo Día/Noche con Iluminación Urbana** | Baja | Entorno | Configuración de ciclo circadiano dinámico con activación de bombillas en los faroles coloniales de la plaza y faros LED frontales automáticos del robot. |
| **TODO-05** | **App Web / Dashboard de Monitoreo IoT** | Media | Cloud/IoT | Panel web en tiempo real para visualizar ruta GPS, estado de batería, residuos recolectados y teleoperación remota vía WebSockets. |

---

### 2. 🔄 Bloque IN PROGRESS (En Progreso)

| ID | Tarea / Característica | Responsable / Rama | Avance | Descripción Técnica |
|---|---|:---:|:---:|---|
| **PROG-01** | **Despliegue y Streaming en Webots Cloud** | `main` | 85% | Empaquetado Docker y sincronización de las nuevas animaciones 3D del robot y mallas de la plaza para reproducción directa en navegador en [Webots.cloud](https://webots.cloud). |
| **PROG-02** | **Pipeline de Clasificación de Basura (YOLOv8)** | `feature/vision-yolo` | 60% | Entrenamiento y validación de modelo de visión artificial con la cámara superior (640×480) para discriminar entre botellas PET, latas de aluminio, cartón y bolsas plásticas. |
| **PROG-03** | **Calibración Fina de Fricción en Pinzas** | `main` | 75% | Optimización de coeficientes de fricción Coulombiana y CFM/ERP entre las almohadillas de goma de la pinza y residuos de geometrías cilíndricas/esféricas en Webots. |

---

### 3. ✅ Bloque DONE (Completado)

| ID | Tarea / Característica | Entregable / Archivo | Commit | Descripción Técnica |
|---|---|:---:|:---:|---|
| **DONE-01** | **Modelado 3D y Visibilidad Total del Robot** | `protos/RobotLimpiadorCienaga.proto` | [`4ffe39d`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/4ffe39d) | Modelado de alta definición con materiales PBR vibrantes: carrocería amarillo municipal (`#F5B814`), parachoques negro con chevron reflectivo, mástil con LiDAR cian, baliza ámbar, cámara estéreo, 4 ruedas motrices y tolva de reciclaje. Todas las piezas 100% visibles. |
| **DONE-02** | **Brazo Robótico de 4 GDL y Pinzas Recolectoras** | `protos/RobotLimpiadorCienaga.proto` | [`4ffe39d`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/4ffe39d) | Modelado y ensamble de torreta giratoria (Yaw, ±3.2 rad), hombro con pistón hidráulico cromado, codo articulado con mangueras neumáticas, muñeca con diodo láser y doble pinza paralela con almohadillas de goma antideslizante. |
| **DONE-03** | **Gesto Cinemático 3D de Recolección de Basura** | `controllers/robot_limpiador_controller/` | [`4ffe39d`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/4ffe39d) | Cinemática directa 3D completa: orientación de base, descenso fluido al suelo ($Z \approx 0.04$ m), sujeción firme con pinzas, elevación aérea, giro en arco de 180° sobre el chasis y depósito dentro de la tolva con transporte dinámico del residuo. |
| **DONE-04** | **Circuito Autónomo de Barrido de la Plaza** | `controllers/robot_limpiador_controller/` | [`792faee`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/792faee) | Algoritmo de patrullaje con waypoints que recorre sistemáticamente Sendero Oeste, Rotonda Noroeste, Paseo Norte, Sendero de la Iglesia, Atrio de San Juan Bautista, Rotonda Sureste y Paseo Sur. |
| **DONE-05** | **Cámara de Persecución 3D y HUD en Pantalla** | `worlds/cienaga_limpiador.wbt` | [`792faee`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/792faee) | Punto de vista dinámico en tercera persona (`follow "Robot_Limpiador_Cienaga"`) con telemetría HUD en pantalla que muestra residuos recogidos, sector actual, % de llenado de tolva y controles. |
| **DONE-06** | **Modelado de El Templete Neoclásico** | `worlds/cienaga_limpiador.wbt` | [`8eb7914`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/8eb7914) | Recreación del monumento central de Ciénaga con 4 niveles escalonados, 8 columnas toscanas, entablamento, balaustrada ornamental y cúpula con pináculo. |
| **DONE-07** | **Modelado de Iglesia San Juan Bautista y Sierra Nevada** | `worlds/meshes/` | [`eef3646`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/eef3646) | Fachada colonial blanca con frontón, campanario de 24 m con campanas de bronce, cúpula octogonal y relieve montañoso de la Sierra Nevada de Santa Marta en el horizonte. |
| **DONE-08** | **Distribución de 13 Residuos Interactivos** | `worlds/cienaga_limpiador.wbt` | [`8eb7914`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/8eb7914) | Catálogo físico de latas de refresco, botellas plásticas, cajas de cartón, bolsas y papel arrugado con masas y geometrías de colisión para recolección autónoma. |
| **DONE-09** | **Despliegue y Empaquetado Webots Cloud** | `webots.yaml`, `Dockerfile` | [`6c51adc`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/6c51adc) | Configuración de contenedor Docker y metadatos YAML para ejecución en línea en [webots.cloud](https://webots.cloud). |

---

### 📈 Historial de Commits del Proyecto

```
* 4ffe39d - fix(robot): Visibilidad completa del robot, modelado 3D del brazo de 4 GDL y gesto cinematico de recoleccion
* 792faee - feat(simulation): Posicionamiento visible del robot con camara de persecucion y circuito de barrido de toda la plaza
* e45a359 - feat(robot): Implementacion completa del sistema autonomo de recoleccion de basura con brazo de 4 GDL y HUD
* 46bbe58 - feat(simulation): Sincronizacion de mallas visuales de alta fidelidad para el mundo de Webots
* eef3646 - feat(environment): Modelado detallado de fachada clasica de Iglesia San Juan Bautista y relieve facetado de la Sierra Nevada
* 8eb7914 - feat(simulation): Integracion de la Plaza del Centenario en Webots con fisicas, colisiones y circuito de recoleccion
* ab356df - feat(environment): Modelado 3D de la Plaza del Centenario, El Templete neoclasico e Iglesia San Juan Bautista
* 7396891 - docs(project): Actualizar seccion de gestion del proyecto, roadmap, entregables e hitos
* d8e7e64 - chore: ignore local animation exports
* 6c51adc - ci(webots-cloud): Configuracion para despliegue en Webots.cloud y documentacion completa
```

---

### 🎯 Enlaces de Seguimiento en GitHub
* 📊 **Tablero de Proyecto (Projects)**: [Ver Tablero Kanban en GitHub](https://github.com/Castillo-lewis/proyecto-cienaga-/projects)
* 📌 **Hitos del Proyecto (Milestones)**: [Ver Hitos y Entregables](https://github.com/Castillo-lewis/proyecto-cienaga-/milestones)
* 📋 **Tareas y Trazabilidad (Issues)**: [Ver Listado de Tareas](https://github.com/Castillo-lewis/proyecto-cienaga-/issues)

---

## 💻 Ejecución Local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Castillo-lewis/proyecto-cienaga-.git
   ```
2. Ejecuta `abrir_en_webots.bat` o abre `worlds/cienaga_limpiador.wbt` directamente en Webots R2025a.

