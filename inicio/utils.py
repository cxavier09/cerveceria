import cv2
import numpy as np
from collections import deque
import math

class HandUtils:
    """Utilidades para procesamiento y análisis de manos"""
    
    @staticmethod
    def calculate_distance(point1, point2):
        """
        Calcula distancia euclidiana entre dos puntos
        
        Args:
            point1: Tupla (x1, y1)
            point2: Tupla (x2, y2)
            
        Returns:
            float: Distancia
        """
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    @staticmethod
    def calculate_angle(point1, point2, point3):
        """
        Calcula el ángulo formado por tres puntos
        
        Args:
            point1, point2, point3: Tuplas (x, y)
            
        Returns:
            float: Ángulo en grados
        """
        v1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
        v2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
        
        dot_product = np.dot(v1, v2)
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        
        angle = math.atan2(cross_product, dot_product)
        return math.degrees(angle)
    
    @staticmethod
    def is_finger_extended(landmarks, finger_tip, finger_pip):
        """
        Determina si un dedo está extendido
        
        Args:
            landmarks: Lista de puntos clave de la mano
            finger_tip: Índice de la punta del dedo
            finger_pip: Índice de la articulación PIP
            
        Returns:
            bool: True si el dedo está extendido
        """
        tip = landmarks[finger_tip]
        pip = landmarks[finger_pip]
        return tip[1] < pip[1]  # Y de punta < Y de PIP
    
    @staticmethod
    def count_extended_fingers(landmarks):
        """
        Cuenta los dedos extendidos
        
        Args:
            landmarks: Lista de puntos clave (21 puntos para mano)
            
        Returns:
            dict: Contador de dedos extendidos
        """
        fingers_status = {
            'thumb': HandUtils.is_finger_extended(landmarks, 4, 3),
            'index': HandUtils.is_finger_extended(landmarks, 8, 6),
            'middle': HandUtils.is_finger_extended(landmarks, 12, 10),
            'ring': HandUtils.is_finger_extended(landmarks, 16, 14),
            'pinky': HandUtils.is_finger_extended(landmarks, 20, 18)
        }
        return fingers_status
    
    @staticmethod
    def detect_gesture(landmarks):
        """
        Detecta gestos básicos de la mano
        
        Args:
            landmarks: Lista de puntos clave
            
        Returns:
            str: Nombre del gesto detectado
        """
        fingers = HandUtils.count_extended_fingers(landmarks)
        extended_count = sum(fingers.values())
        
        if extended_count == 0:
            return "Puño (Fist)"
        elif extended_count == 1 and fingers['index']:
            return "Índice (Point)"
        elif extended_count == 2 and fingers['index'] and fingers['middle']:
            return "Victoria (Victory)"
        elif extended_count == 5:
            return "Mano Abierta (Open Hand)"
        elif fingers['thumb'] and fingers['index']:
            return "OK"
        else:
            return f"Gesto con {extended_count} dedos"
    
    @staticmethod
    def smooth_coordinates(coords_history, current_coords):
        """
        Suaviza coordenadas usando promedio móvil
        
        Args:
            coords_history: Deque con historial de coordenadas
            current_coords: Coordenadas actuales
            
        Returns:
            tuple: Coordenadas suavizadas
        """
        coords_history.append(current_coords)
        
        if len(coords_history) == 0:
            return current_coords
        
        avg_x = np.mean([c[0] for c in coords_history])
        avg_y = np.mean([c[1] for c in coords_history])
        
        return (int(avg_x), int(avg_y))
    
    @staticmethod
    def draw_info_box(frame, text, position=(10, 30), font_size=0.7,
                     bg_color=(0, 0, 0), text_color=(255, 255, 255)):
        """
        Dibuja un cuadro de información en el frame
        
        Args:
            frame: Frame de video
            text: Texto a mostrar
            position: Posición (x, y)
            font_size: Tamaño de fuente
            bg_color: Color de fondo (BGR)
            text_color: Color de texto (BGR)
            
        Returns:
            frame: Frame modificado
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 1
        
        # Obtener tamaño del texto
        text_size = cv2.getTextSize(text, font, font_size, thickness)[0]
        
        # Dibujar rectángulo de fondo
        x, y = position
        cv2.rectangle(frame, (x - 5, y - text_size[1] - 5),
                     (x + text_size[0] + 5, y + 5), bg_color, -1)
        
        # Dibujar texto
        cv2.putText(frame, text, position, font, font_size, text_color, thickness)
        
        return frame
    
    @staticmethod
    def track_hand_movement(prev_center, curr_center, threshold=50):
        """
        Detecta si hay movimiento de la mano
        
        Args:
            prev_center: Centro anterior (x, y)
            curr_center: Centro actual (x, y)
            threshold: Umbral mínimo de movimiento en píxeles
            
        Returns:
            dict: Información de movimiento
        """
        distance = HandUtils.calculate_distance(prev_center, curr_center)
        
        return {
            'distance': distance,
            'moving': distance > threshold,
            'direction': None if distance == 0 else (
                np.arctan2(curr_center[1] - prev_center[1],
                          curr_center[0] - prev_center[0])
            )
        }
    
    @staticmethod
    def estimate_hand_pose(landmarks):
        """
        Estima la pose (orientación) de la mano
        
        Args:
            landmarks: Lista de puntos clave
            
        Returns:
            dict: Información de pose
        """
        wrist = np.array([landmarks[0][0], landmarks[0][1]])
        middle_mcp = np.array([landmarks[9][0], landmarks[9][1]])
        ring_mcp = np.array([landmarks[13][0], landmarks[13][1]])
        
        # Vector de orientación
        direction = middle_mcp - wrist
        
        # Calcular ángulo
        angle = math.atan2(direction[1], direction[0])
        angle_degrees = math.degrees(angle)
        
        return {
            'angle': angle_degrees,
            'direction': direction,
            'orientation': 'Palm Up' if abs(angle_degrees) < 45 else 'Palm Down'
        }


class FrameProcessor:
    """Procesador de frames para video"""
    
    def __init__(self, buffer_size=10):
        """
        Inicializa el procesador
        
        Args:
            buffer_size: Tamaño del buffer de suavizado
        """
        self.coords_history = deque(maxlen=buffer_size)
        self.fps = 0
        self.frame_count = 0
        self.prev_time = 0
    
    def calculate_fps(self, current_time):
        """
        Calcula FPS
        
        Args:
            current_time: Tiempo actual (cv2.getTickCount())
            
        Returns:
            float: FPS
        """
        if self.prev_time == 0:
            self.prev_time = current_time
            return 0
        
        time_diff = (current_time - self.prev_time) / cv2.getTickFrequency()
        self.fps = 1 / time_diff if time_diff > 0 else 0
        self.prev_time = current_time
        
        return self.fps
    
    def draw_fps(self, frame, fps):
        """
        Dibuja FPS en el frame
        
        Args:
            frame: Frame de video
            fps: FPS actual
            
        Returns:
            frame: Frame modificado
        """
        cv2.putText(frame, f'FPS: {fps:.1f}',
                   (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame
    
    @staticmethod
    def adjust_brightness(frame, value):
        """
        Ajusta brillo de la imagen
        
        Args:
            frame: Frame original
            value: Valor a ajustar (-100 a 100)
            
        Returns:
            frame: Frame ajustado
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = hsv[:, :, 2] * (1.0 + value / 100.0)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    @staticmethod
    def adjust_contrast(frame, value):
        """
        Ajusta contraste de la imagen
        
        Args:
            frame: Frame original
            value: Factor de contraste (0.5 a 3.0)
            
        Returns:
            frame: Frame ajustado
        """
        adjusted = cv2.convertScaleAbs(frame, alpha=value, beta=0)
        return adjusted
