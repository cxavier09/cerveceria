# Sistema de Detección de Manos 🖐️

Programa completo de detección y seguimiento de puntos clave de manos usando **MediaPipe** y **OpenCV con Deep Learning**.

## Características

### MediaPipe
- ✅ Detección en tiempo real de manos (hasta 2 simultáneamente)
- ✅ Seguimiento de 21 puntos clave por mano
- ✅ Identificación de izquierda/derecha
- ✅ Bajo consumo de recursos
- ✅ Alta precisión y velocidad

### OpenCV + Deep Learning
- ✅ Detección basada en redes neuronales convolucionales
- ✅ Extracción de características de la mano
- ✅ Detección de dedos extendidos
- ✅ Cálculo de contornos convexos
- ✅ Análisis de tamaño y forma

## Instalación

### 1. Requisitos
- Python 3.8+
- Webcam (integrada o externa)

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Uso

### Opción 1: MediaPipe (Recomendado)

```bash
python hand_detection_mediapipe.py
```

**Controles:**
- `q`: Salir
- `s`: Guardar screenshot

**Información mostrada:**
- Número de manos detectadas
- Tipo de mano (izquierda/derecha)
- Confianza de detección
- Coordenadas de puntos clave
- FPS en tiempo real

### Opción 2: Deep Learning (OpenCV)

```bash
python hand_detection_deep_learning.py
```

**Características adicionales:**
- Bounding boxes alrededor de manos
- Detección de casco convexo
- Estimación de dedos extendidos
- Análisis de regiones de interés (ROI)

## Estructura de Puntos Clave (MediaPipe)

Cada mano tiene 21 puntos clave:

```
0  - Muñeca (Wrist)
1-4  - Pulgar (Thumb)
5-8  - Índice (Index)
9-12 - Medio (Middle)
13-16 - Anular (Ring)
17-20 - Meñique (Pinky)
```

### Nombres de puntos:

| ID | Nombre | ID | Nombre |
|----|--------|----|---------|
| 0 | Wrist | 11 | Middle_DIP |
| 1 | Thumb_CMC | 12 | Middle_Tip |
| 2 | Thumb_MCP | 13 | Ring_MCP |
| 3 | Thumb_IP | 14 | Ring_PIP |
| 4 | Thumb_Tip | 15 | Ring_DIP |
| 5 | Index_MCP | 16 | Ring_Tip |
| 6 | Index_PIP | 17 | Pinky_MCP |
| 7 | Index_DIP | 18 | Pinky_PIP |
| 8 | Index_Tip | 19 | Pinky_DIP |
| 9 | Middle_MCP | 20 | Pinky_Tip |
| 10 | Middle_PIP | | |

## Utilidades (utils.py)

Funciones auxiliares disponibles:

### HandUtils

```python
from utils import HandUtils

# Calcular distancia entre puntos
distancia = HandUtils.calculate_distance((x1, y1), (x2, y2))

# Calcular ángulo
angulo = HandUtils.calculate_angle((x1, y1), (x2, y2), (x3, y3))

# Contar dedos extendidos
dedos = HandUtils.count_extended_fingers(landmarks)

# Detectar gesto
gesto = HandUtils.detect_gesture(landmarks)
# Retorna: "Puño", "Índice", "Victoria", "Mano Abierta", "OK", etc.

# Suavizar coordenadas
coords_suavizadas = HandUtils.smooth_coordinates(historia, coords_actuales)

# Estimar pose
pose = HandUtils.estimate_hand_pose(landmarks)
```

### FrameProcessor

```python
from utils import FrameProcessor

processor = FrameProcessor(buffer_size=10)

# Calcular FPS
fps = processor.calculate_fps(cv2.getTickCount())

# Ajustar brillo
frame_bright = FrameProcessor.adjust_brightness(frame, valor)

# Ajustar contraste
frame_contrast = FrameProcessor.adjust_contrast(frame, factor)
```

## Ejemplos de Uso Avanzado

### Ejemplo 1: Detector de Gestos

```python
import cv2
from hand_detection_mediapipe import HandDetector
from utils import HandUtils

detector = HandDetector()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    results, _ = detector.detect_hands(frame)
    frame = detector.draw_landmarks(frame, results)
    
    hands_info = detector.get_hand_info(results, frame)
    
    for hand in hands_info:
        landmarks = [tuple([p['x'], p['y']]) for p in hand['landmarks']]
        gesto = HandUtils.detect_gesture(landmarks)
        print(f"Mano {hand['hand']}: {gesto}")
    
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Ejemplo 2: Seguimiento de Movimiento

```python
from collections import deque
from utils import HandUtils

prev_center = None
movement_history = deque(maxlen=30)

while True:
    # ... código de detección ...
    
    curr_center = hand['landmarks'][0]['x'], hand['landmarks'][0]['y']
    
    if prev_center:
        movement = HandUtils.track_hand_movement(prev_center, curr_center)
        movement_history.append(movement)
        
        if movement['moving']:
            print(f"Mano en movimiento: {movement['distance']:.1f} píxeles")
    
    prev_center = curr_center
```

## Información Técnica

### Arquitectura de MediaPipe
- Modelo: Palm Detection + Hand Landmark Detection
- Entrada: 192x192 píxeles (interno)
- Salida: 21 puntos en coordenadas normalizadas (0-1)
- Latencia: ~5-20ms por frame (CPU)
- Precisión: >95% en condiciones normales

### Arquitectura de Deep Learning (OpenCV)
- Modelo: SSD (Single Shot MultiBox Detector) o YOLO
- Entrada: 300x300 píxeles (variable)
- Salida: Bounding boxes + confianza
- Latencia: 20-50ms por frame
- Framework: Caffe / Darknet

## Solución de Problemas

### La detección es lenta
- Reduce resolución de cámara
- Usa MediaPipe en lugar de Deep Learning
- Verifica procesador (CPU vs GPU)

### Detección inexacta
- Mejora iluminación
- Acerca la mano a la cámara
- Asegura que el fondo sea consistente

### No se detectan manos
- Verifica que la cámara esté funcionando
- Prueba con diferente ángulo
- Ajusta parámetros de confianza

## Mejoras Futuras

- [ ] Detección de gestos específicos avanzados
- [ ] Reconocimiento de lenguaje de señas
- [ ] GPU support con CUDA/OpenCL
- [ ] Interfaz gráfica mejorada
- [ ] Export a diferentes formatos (TFLite, ONNX)

## Referencias

- [MediaPipe Documentation](https://mediapipe.dev/)
- [OpenCV DNN Module](https://docs.opencv.org/master/d6/d0f/group__dnn.html)
- [Hand Pose Estimation](https://github.com/google/mediapipe/blob/master/docs/solutions/hands.md)

## Licencia

MIT License

## Autor

Creado por: cxavier09
Fecha: 2026-04-25
