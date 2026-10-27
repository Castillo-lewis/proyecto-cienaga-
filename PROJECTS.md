# 📊 Tablero de Gestión del Proyecto (GitHub Projects Kanban)
## Robot Limpiador Autónomo de Ciénaga, Magdalena

Este documento detalla la trazabilidad y avance continuo del proyecto organizado bajo la metodología Kanban en los tres bloques operativos: **TO DO**, **IN PROGRESS** y **DONE**.

---

## 🗂️ Vista General del Tablero Kanban

```
┌──────────────────────────────────────┬──────────────────────────────────────┬──────────────────────────────────────┐
│             📋 TO DO                 │           🔄 IN PROGRESS             │               ✅ DONE                │
│            (Por Hacer)               │            (En Progreso)             │             (Completado)             │
├──────────────────────────────────────┼──────────────────────────────────────┼──────────────────────────────────────┤
│ • [TODO-01] Mapeo SLAM con LiDAR 2D  │ • [PROG-01] Despliegue Webots Cloud  │ • [DONE-01] Modelado 3D Robot 100%   │
│ • [TODO-02] Cobertura Boustrophedon  │ • [PROG-02] Visión IA con YOLOv8     │ • [DONE-02] Brazo 4 GDL y Pinzas     │
│ • [TODO-03] Sensor de llenado tolva  │ • [PROG-03] Calibración de Pinza     │ • [DONE-03] Gesto Cinemático Recoge  │
│ • [TODO-04] Ciclo día/noche y faroles│                                      │ • [DONE-04] Circuito Toda la Plaza   │
│ • [TODO-05] Dashboard IoT Telemétrico│                                      │ • [DONE-05] Cámara Persecución y HUD │
│                                      │                                      │ • [DONE-06] El Templete Neoclásico   │
│                                      │                                      │ • [DONE-07] Iglesia San Juan y Sierra│
│                                      │                                      │ • [DONE-08] 13 Residuos Interactivos │
│                                      │                                      │ • [DONE-09] Empaquetado Docker/Cloud │
└──────────────────────────────────────┴──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 1. 📋 Bloque: TO DO (Por Hacer)

### 📌 [TODO-01] Mapeo 2D/3D y Navegación SLAM Urbano
* **Módulo:** Navegación y Percepción
* **Prioridad:** Alta
* **Descripción:** Implementar algoritmos de Simultaneous Localization and Mapping (SLAM) tales como Google Cartographer o RTAB-Map utilizando las nubes de puntos del sensor LiDAR del mástil.
* **Criterios de Aceptación:**
  - Generación de un mapa de ocupación 2D (.yaml/.pgm) de la Plaza del Centenario.
  - Estimación robusta de pose frente a la pérdida eventual de señal GPS bajo los árboles.

### 📌 [TODO-02] Planificación de Cobertura Sistemática (Coverage Path Planning)
* **Módulo:** Control Autónomo
* **Prioridad:** Alta
* **Descripción:** Reemplazar el patrullaje de circuito cerrado por un algoritmo de cobertura exhaustiva tipo *Boustrophedon Decomposition* o *Spanning Tree Coverage*.
* **Criterios de Aceptación:**
  - Limpieza del 100% de la superficie adoquinada de la plaza sin repetir senderos innecesariamente.
  - Registro de mapa de calor de zonas limpiadas.

### 📌 [TODO-03] Sensor Óptico de Nivel de Llenado en Tolva
* **Módulo:** Telemetría y Actuación
* **Prioridad:** Media
* **Descripción:** Incorporar un sensor Time-of-Flight (ToF) o ultrasónico cenital en el interior de la tolva para computar el volumen ocupado por los residuos.
* **Criterios de Aceptación:**
  - Emisión de alerta de tolva llena (100%) al llegar a 12 residuos.
  - Enrutamiento automático hacia punto de acopio o camión recolector municipal.

### 📌 [TODO-04] Ciclo Circadiano Día/Noche con Alumbrado Público Operativo
* **Módulo:** Entorno y Simulación
* **Prioridad:** Baja
* **Descripción:** Configurar ciclo de iluminación solar dinámico en Webots R2025a, encendiendo las luminarias de los 10 faroles coloniales y los faros frontales LED del robot al caer el sol.

### 📌 [TODO-05] Panel Web / Dashboard de Monitoreo IoT
* **Módulo:** Cloud & Frontend
* **Prioridad:** Media
* **Descripción:** Construir un dashboard web interactivo con telemetría en tiempo real: coordenadas GPS, estado de la tolva, video de la cámara superior y comandos de teleoperación.

---

## 2. 🔄 Bloque: IN PROGRESS (En Progreso)

### ⚙️ [PROG-01] Optimización de Despliegue en Webots Cloud
* **Rama:** `main` | **Avance:** 85%
* **Descripción:** Validación y sincronización de las nuevas animaciones 3D generadas tras el rediseño del brazo robótico y la cinemática de recolección para que se reproduzca fluidamente en el navegador sin requerir GPU local.
* **Próximos pasos:** Validar el streaming de texturas PBR y compresión en gzip.

### ⚙️ [PROG-02] Pipeline de Clasificación de Residuos con IA (YOLOv8)
* **Rama:** `feature/vision-yolo` | **Avance:** 60%
* **Descripción:** Entrenamiento de un modelo convolucional liviano (YOLOv8-Nano) a partir del flujo de video de la cámara superior (640×480 px) para categorizar residuos en 4 clases: Plástico, Metal, Cartón y Orgánico.
* **Próximos pasos:** Exportar modelo a ONNX y vincularlo en tiempo real al controlador en Python.

### ⚙️ [PROG-03] Ajuste Fino de Dinámica de Contacto del Gripper
* **Rama:** `main` | **Avance:** 75%
* **Descripción:** Calibración de parámetros de fricción Coulombiana (fricción estática y dinámica), CFM y ERP entre las almohadillas de goma de la pinza y los cuerpos rígidos de latas y botellas cilíndricas.

---

## 3. ✅ Bloque: DONE (Completado)

### 🎉 [DONE-01] Modelado 3D y Visibilidad Total del Robot
* **Entregables:** `protos/RobotLimpiadorCienaga.proto`, `worlds/cienaga_limpiador.wbt`
* **Commit:** [`4ffe39d`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/4ffe39d)
* **Descripción:** 
  - Chasis industrial amarillo municipal (`#F5B814`) con placa inferior en metal grafito.
  - Parachoques frontal negro con chevron reflectivo de seguridad y faros LED dobles de alta intensidad.
  - Mástil de instrumentación con sensor LiDAR cian de 360°, baliza ámbar parpadeante y cámara estéreo.
  - 4 ruedas motrices con neumáticos de goma negra labrada y rines plateados de aleación.
  - Tolva posterior de residuos con placas laterales ecológicas de reciclaje.
  - Todas las piezas 100% visibles, alineadas con sus ejes físicos locales y sin elementos enterrados ni ocultos.

### 🎉 [DONE-02] Brazo Robótico de 4 GDL y Pinzas Recolectoras
* **Entregables:** `protos/RobotLimpiadorCienaga.proto`
* **Commit:** [`4ffe39d`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/4ffe39d)
* **Descripción:**
  - Base giratoria Yaw con torreta de titanio, corona dentada dorada y anillo LED cian (recorrido $\pm3.2\text{ rad}$).
  - Articulación de hombro Pitch con pistón cromado de asistencia hidráulica y paneles amarillos de protección.
  - Codo Pitch con guías de mangueras neumáticas.
  - Muñeca articulada con diodo láser rojo de puntería.
  - Pinza paralela con dos dedos en naranja/amarillo de seguridad y almohadillas de goma negra antideslizante.

### 🎉 [DONE-03] Gesto Cinemático 3D de Recolección y Depósito
* **Entregables:** `controllers/robot_limpiador_controller/robot_limpiador_controller.py`
* **Commit:** [`4ffe39d`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/4ffe39d)
* **Descripción:**
  - Cinemática directa 3D precisa: apuntado de torreta, descenso fluido hasta el suelo ($Z \approx 0.04\text{ m}$), cierre firme de pinzas, elevación aérea con el residuo siguiendo activamente la punta de la garra en 3D, giro circular de 180° sobre el chasis y apertura sobre la tolva trasera depositando el residuo.
  - Tiempos de movimiento optimizados (~5 s por ciclo) para apreciación visual clara en la simulación.

### 🎉 [DONE-04] Circuito de Barrido de Toda la Plaza del Centenario
* **Entregables:** `controllers/robot_limpiador_controller/robot_limpiador_controller.py`
* **Commit:** [`792faee`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/792faee)
* **Descripción:**
  - Circuito de navegación autónoma continua a través de 11 waypoints estratégicos que recorren el Sendero Oeste (Entrada), Rotonda Noroeste, Paseo Norte (Jardineras), Paseo Central Este, Atrio de la Iglesia San Juan Bautista, Rotonda Sureste y Paseo Sur.
  - Evasión reactiva de bordillos mediante sensores ultrasónicos laterales.

### 🎉 [DONE-05] Cámara de Persecución en Tercera Persona y HUD
* **Entregables:** `worlds/cienaga_limpiador.wbt`
* **Commit:** [`792faee`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/792faee)
* **Descripción:**
  - Viewpoint dinámico (`follow "Robot_Limpiador_Cienaga"`) configurado en perspectiva aérea 3/4 para visualización óptima del robot y sus maniobras.
  - HUD interactivo en pantalla con telemetría: contador de residuos limpiados, sector actual, porcentaje de llenado de tolva y guía de controles manuales.

### 🎉 [DONE-06] Modelado Arquitectónico de El Templete Neoclásico
* **Entregables:** `worlds/cienaga_limpiador.wbt`, `meshes/entorno_templete.obj`
* **Commit:** [`8eb7914`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/8eb7914)
* **Descripción:**
  - Monumento histórico central de Ciénaga con 4 niveles concéntricos de escalones, plataforma circular, 8 columnas toscanas con capiteles, cornisa ornamental, balaustrada perimetral y cúpula con linterna y pináculo.

### 🎉 [DONE-07] Fachada de Iglesia San Juan Bautista y Sierra Nevada
* **Entregables:** `worlds/meshes/entorno_iglesia.obj`, `worlds/cienaga_limpiador.wbt`
* **Commit:** [`eef3646`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/eef3646)
* **Descripción:**
  - Fachada colonial blanca con frontón clásico, torre campanario de 24 m con campanas de bronce, cúpula octogonal y pérgola lateral.
  - Paisaje montañoso facetado en el horizonte que recrea la Sierra Nevada de Santa Marta.

### 🎉 [DONE-08] Distribución de 13 Residuos Interactivos
* **Entregables:** `worlds/cienaga_limpiador.wbt`
* **Commit:** [`8eb7914`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/8eb7914)
* **Descripción:**
  - Latas de refresco, botellas de agua, cajas de cartón, bolsas y papeles arrugados distribuidos en el sendero de entrada, rotonda del Templete y atrio de la iglesia, configurados con propiedades de contacto y colisión física.

### 🎉 [DONE-09] Despliegue en la Nube (Webots Cloud)
* **Entregables:** `webots.yaml`, `Dockerfile`
* **Commit:** [`6c51adc`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/6c51adc)
* **Descripción:**
  - Configuración y validación del entorno Webots Cloud para ejecución en línea en navegadores web.

---

## 📜 Registro de Commits Oficiales del Repositorio

| Hash | Tipo | Mensaje del Commit |
|:---:|:---:|---|
| [`4ffe39d`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/4ffe39d) | `fix` | Visibilidad completa del robot, modelado 3D del brazo de 4 GDL y gesto cinemático de recolección |
| [`792faee`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/792faee) | `feat` | Posicionamiento visible del robot con cámara de persecución y circuito de barrido de toda la plaza |
| [`e45a359`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/e45a359) | `feat` | Implementación completa del sistema autónomo de recolección de basura con brazo de 4 GDL y HUD |
| [`46bbe58`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/46bbe58) | `feat` | Sincronización de mallas visuales de alta fidelidad para el mundo de Webots |
| [`eef3646`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/eef3646) | `feat` | Modelado detallado de fachada clásica de Iglesia San Juan Bautista y relieve facetado de la Sierra Nevada |
| [`8eb7914`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/8eb7914) | `feat` | Integración de la Plaza del Centenario en Webots con físicas, colisiones y circuito de recolección |
| [`ab356df`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/ab356df) | `feat` | Modelado 3D de la Plaza del Centenario, El Templete neoclásico e Iglesia San Juan Bautista |
| [`7396891`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/7396891) | `docs` | Actualizar sección de gestión del proyecto, roadmap, entregables e hitos |
| [`d8e7e64`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/d8e7e64) | `chore`| Ignore local animation exports |
| [`6c51adc`](https://github.com/Castillo-lewis/proyecto-cienaga-/commit/6c51adc) | `ci` | Configuración para despliegue en Webots.cloud y documentación completa |

---

*Proyecto desarrollado para la preservación patrimonial y ambiental de Ciénaga, Magdalena.*
