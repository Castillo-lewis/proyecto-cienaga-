# Robot recolector de Cienaga — dimensiones y export Webots

Archivo Blender: `C:\Users\lewis\Documents\Robot_Limpiador_Cienaga\Robot_Limpiador_Cienaga.blend`
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
| Chasis | 1.20 L x 0.78 W x 0.38 H | Centro Z = 0.28. Cuerpo base. |
| Ruedas | radio 0.16, ancho 0.10 | 4 objetos. Eje de giro **Y local** de cada `Pivote_Rueda_*`. |
| Distancia entre ejes | 0.72 | X entre ejes delantero/trasero |
| Trocha | 0.70 | Y entre centros de rueda |
| Contenedor_Basura | 0.62 x 0.70 x 0.48 | Trasero superior, hijo de Chasis |
| Brazo_Base | h=0.12 | Yaw en `Pivote_Brazo_Base` (eje Z) |
| Brazo_Segmento_1 | largo 0.42 | Pitch en `Pivote_Brazo_1` (eje Y) |
| Brazo_Segmento_2 | largo 0.38 | Pitch en `Pivote_Brazo_2` (eje Y) |
| Pinza | largo 0.17 | Apertura: rot Z de `Pivote_Pinza_Izquierda/Derecha` |

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
