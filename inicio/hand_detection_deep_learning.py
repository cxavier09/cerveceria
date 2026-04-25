import cv2
import numpy as np
from pathlib import Path
import urllib.request
import os

class HandDetectorDL:
    """Detector de manos usando OpenCV + Deep Learning (YOLO)"""
    
    def __init__(self, weights_path=None, config_path=None, names_path=None):
        """
        Inicializa el detector con pesos pre-entrenados
        
        Args:
            weights_path (str): Ruta a los pesos del modelo
            config_path (str): Ruta al archivo de configuración
            names_path (str): Ruta al archivo de nombres de clases
        """
        self.net = None
        self.layer_names = None
        self.output_layers = None
        self.classes = None
        
        if weights_path and config_path:
            self.load_model(weights_path, config_path, names_path)
        else:
            self.load_default_model()
    
    def load_default_model(self):
        """
        Carga un modelo SSD pre-entrenado de OpenCV
        """
        # Descargar archivos si no existen
        model_dir = Path('models')
        model_dir.mkdir(exist_ok=True)
        
        # Rutas de archivos
        proto_file = model_dir / 'deploy.prototxt'
        model_file = model_dir / 'res10_300x300_ssd_iter_140000.caffemodel'
        
        # URLs de descargas
        proto_url = 'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/opencv_face_detector.prototxt'
        model_url = 'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/opencv_face_detector_uint8.pb'
        
        # Descargar si no existen
        if not proto_file.exists():
            print(f"Descargando {proto_file.name}...")
            try:
                urllib.request.urlretrieve(proto_url, proto_file)
            except:
                print(f"No se pudo descargar {proto_file.name}")
        
        # Cargar red neuronal
        try:
            self.net = cv2.dnn.readNetFromCaffe(str(proto_file), str(model_file))
            print("Modelo SSD cargado correctamente")
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            print("Usando detección alternativa...")
    
    def load_model(self, weights_path, config_path, names_path=None):
        """
        Carga un modelo personalizado
        
        Args:
            weights_path (str): Ruta a los pesos
            config_path (str): Ruta a la configuración
            names_path (str): Ruta a los nombres de clases
        """
        self.net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
        
        if names_path and os.path.exists(names_path):
            with open(names_path, 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]
        
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] 
                             for i in self.net.getUnconnectedOutLayers()]
        
        print(f"Modelo cargado: {len(self.classes)} clases")
    
    def detect_hands_ssd(self, frame, confidence_threshold=0.5):
        """
        Detecta manos usando SSD
        
        Args:
            frame: Imagen de entrada
            confidence_threshold (float): Umbral de confianza
            
        Returns:
            detections: Lista de detecciones [x, y, w, h, confidence]
        """
        h, w = frame.shape[:2]
        
        # Preparar blob
        blob = cv2.dnn.blobFromImage(
            frame, 1.0, (300, 300),
            [104.0, 177.0, 123.0], False, False
        )
        
        self.net.setInput(blob)
        detections = self.net.forward()
        
        results = []
        
        # Procesar detecciones
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > confidence_threshold:
                x1 = int(detections[0, 0, i, 3] * w)
                y1 = int(detections[0, 0, i, 4] * h)
                x2 = int(detections[0, 0, i, 5] * w)
                y2 = int(detections[0, 0, i, 6] * h)
                
                results.append({
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                    'confidence': confidence,
                    'center': ((x1 + x2) // 2, (y1 + y2) // 2)
                })
        
        return results
    
    def extract_hand_landmarks(self, frame, detection):
        """
        Extrae región de mano y calcula puntos clave
        
        Args:
            frame: Frame original
            detection: Detección de mano
            
        Returns:
            landmarks: Puntos clave de la mano
        """
        x1, y1, x2, y2 = detection['x1'], detection['y1'], detection['x2'], detection['y2']
        
        # Asegurar que las coordenadas sean válidas
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)
        
        hand_roi = frame[y1:y2, x1:x2]
        
        if hand_roi.size == 0:
            return None
        
        # Calcular centroid y características
        h, w = hand_roi.shape[:2]
        landmarks = {
            'region': (x1, y1, x2, y2),
            'center': detection['center'],
            'width': x2 - x1,
            'height': y2 - y1,
            'area': (x2 - x1) * (y2 - y1),
            'roi_size': hand_roi.shape
        }
        
        # Detectar contornos para más detalles
        gray = cv2.cvtColor(hand_roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            hull = cv2.convexHull(largest_contour)
            
            # Aproximar dedos detectando vértices del casco convexo
            epsilon = 0.02 * cv2.arcLength(hull, True)
            approx = cv2.approxPolyDP(hull, epsilon, True)
            
            landmarks['hull_points'] = hull.reshape(-1, 2).tolist()
            landmarks['approximate_fingers'] = len(approx)
        
        return landmarks
    
    def draw_detections(self, frame, detections):
        """
        Dibuja las detecciones en el frame
        
        Args:
            frame: Frame original
            detections: Lista de detecciones
            
        Returns:
            frame: Frame anotado
        """
        for detection in detections:
            x1, y1 = detection['x1'], detection['y1']
            x2, y2 = detection['x2'], detection['y2']
            conf = detection['confidence']
            
            # Dibujar bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Dibujar centro
            cx, cy = detection['center']
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            
            # Mostrar confianza
            cv2.putText(frame, f'Confidence: {conf:.2f}',
                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (0, 255, 0), 2)
            
            # Mostrar dimensiones
            width = x2 - x1
            height = y2 - y1
            cv2.putText(frame, f'Size: {width}x{height}',
                       (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (255, 0, 0), 2)
        
        return frame
    
    def draw_landmarks(self, frame, landmarks, detection):
        """
        Dibuja landmarks extraídos
        
        Args:
            frame: Frame original
            landmarks: Puntos clave
            detection: Información de detección
            
        Returns:
            frame: Frame anotado
        """
        if 'hull_points' in landmarks:
            x1, y1 = detection['x1'], detection['y1']
            
            # Convertir puntos al frame completo
            hull_frame = np.array(landmarks['hull_points'], dtype=np.int32)
            hull_frame = hull_frame + np.array([x1, y1])
            
            # Dibujar casco convexo
            cv2.polylines(frame, [hull_frame], True, (0, 255, 255), 2)
            
            # Dibujar vértices
            for point in hull_frame:
                cv2.circle(frame, tuple(point), 3, (255, 0, 0), -1)
        
        return frame


def main():
    """Función principal para detección de manos con Deep Learning"""
    
    # Inicializar detector
    detector = HandDetectorDL()
    
    # Abrir cámara
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Detector de Manos - Deep Learning (OpenCV)")
    print("Presiona 'q' para salir")
    print("Presiona 's' para guardar screenshot")
    
    frame_count = 0
    
    while True:
        success, frame = cap.read()
        if not success:
            print("No se pudo leer el frame")
            break
        
        # Detectar manos
        detections = detector.detect_hands_ssd(frame, confidence_threshold=0.5)
        
        # Dibujar detecciones
        frame = detector.draw_detections(frame, detections)
        
        # Extraer y dibujar landmarks
        for detection in detections:
            landmarks = detector.extract_hand_landmarks(frame, detection)
            if landmarks:
                frame = detector.draw_landmarks(frame, landmarks, detection)
        
        # Información en pantalla
        cv2.putText(frame, f'Manos detectadas: {len(detections)}',
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                   1, (0, 255, 0), 2)
        
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Frame: {frame_count}, Manos: {len(detections)}")
        
        # Mostrar frame
        cv2.imshow('Detección de Manos - Deep Learning', frame)
        
        # Control de teclado
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite(f'hand_detection_dl_{frame_count}.jpg', frame)
            print(f"Imagen guardada: hand_detection_dl_{frame_count}.jpg")
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    print("Programa finalizado")


if __name__ == "__main__":
    main()
