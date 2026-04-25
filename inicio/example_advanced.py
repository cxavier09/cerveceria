"""Ejemplos avanzados de uso del detector de manos"""

import cv2
import numpy as np
from hand_detection_mediapipe import HandDetector
from hand_detection_deep_learning import HandDetectorDL
from utils import HandUtils, FrameProcessor
from collections import deque


class GestureRecognizer:
    """Reconocedor de gestos avanzado"""
    
    def __init__(self):
        self.detector = HandDetector()
        self.gesture_history = deque(maxlen=5)
        self.processor = FrameProcessor()
    
    def recognize_gestures(self, frame):
        """
        Reconoce gestos complejos
        
        Args:
            frame: Frame de entrada
            
        Returns:
            dict: Información de gestos detectados
        """
        results, _ = self.detector.detect_hands(frame)
        hands_info = self.detector.get_hand_info(results, frame)
        
        gestures_data = []
        
        for hand in hands_info:
            landmarks = [(p['x'], p['y']) for p in hand['landmarks']]
            
            # Información básica
            gesture = HandUtils.detect_gesture(landmarks)
            fingers = HandUtils.count_extended_fingers(landmarks)
            pose = HandUtils.estimate_hand_pose(landmarks)
            
            # Almacenar en historial
            self.gesture_history.append(gesture)
            
            # Analizar consistencia
            consistent_gesture = max(
                set(self.gesture_history),
                key=list(self.gesture_history).count
            ) if self.gesture_history else gesture
            
            gestures_data.append({
                'hand': hand['hand'],
                'current_gesture': gesture,
                'consistent_gesture': consistent_gesture,
                'fingers': fingers,
                'pose': pose,
                'confidence': hand['confidence']
            })
        
        return gestures_data
    
    def draw_gesture_info(self, frame, gestures_data):
        """
        Dibuja información de gestos en el frame
        
        Args:
            frame: Frame original
            gestures_data: Datos de gestos
            
        Returns:
            frame: Frame anotado
        """
        y_offset = 30
        
        for i, gesto in enumerate(gestures_data):
            # Título
            text = f"Mano {i+1}: {gesto['hand']}"
            frame = HandUtils.draw_info_box(
                frame, text, (10, y_offset),
                bg_color=(0, 0, 100), text_color=(0, 255, 0)
            )
            
            y_offset += 40
            
            # Gesto
            text = f"Gesto: {gesto['consistent_gesture']}"
            cv2.putText(frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            y_offset += 30
            
            # Dedos extendidos
            fingers_ext = ', '.join(
                [k for k, v in gesto['fingers'].items() if v]
            )
            text = f"Dedos: {fingers_ext if fingers_ext else 'Ninguno'}"
            cv2.putText(frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 255), 2)
            
            y_offset += 30
            
            # Pose
            text = f"Orientación: {gesto['pose']['orientation']}"
            cv2.putText(frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 255), 2)
            
            y_offset += 40
        
        return frame


class HandTracker:
    """Seguidor de manos con historial de movimiento"""
    
    def __init__(self):
        self.detector = HandDetector()
        self.hand_trails = {}  # Historial de movimiento por mano
        self.frame_id = 0
    
    def track_hands(self, frame):
        """
        Sigue el movimiento de manos
        
        Args:
            frame: Frame actual
            
        Returns:
            dict: Información de seguimiento
        """
        results, _ = self.detector.detect_hands(frame)
        hands_info = self.detector.get_hand_info(results, frame)
        
        tracking_info = []
        
        for hand in hands_info:
            hand_id = f"{hand['hand']}_{self.frame_id}"
            center = (hand['landmarks'][0]['x'], hand['landmarks'][0]['y'])
            
            # Inicializar trail si es nueva
            if hand_id not in self.hand_trails:
                self.hand_trails[hand_id] = deque(maxlen=50)
            
            self.hand_trails[hand_id].append(center)
            
            # Calcular velocidad
            if len(self.hand_trails[hand_id]) > 1:
                prev_center = list(self.hand_trails[hand_id])[-2]
                velocity = HandUtils.calculate_distance(prev_center, center)
            else:
                velocity = 0
            
            tracking_info.append({
                'hand': hand['hand'],
                'center': center,
                'velocity': velocity,
                'trail': list(self.hand_trails[hand_id])
            })
        
        self.frame_id += 1
        return tracking_info
    
    def draw_trails(self, frame, tracking_info):
        """
        Dibuja los trails de movimiento
        
        Args:
            frame: Frame original
            tracking_info: Información de seguimiento
            
        Returns:
            frame: Frame con trails
        """
        colors = [(0, 255, 0), (255, 0, 0)]  # Verde y Rojo
        
        for i, info in enumerate(tracking_info):
            trail = info['trail']
            color = colors[i % len(colors)]
            
            # Dibujar trail con degradado de opacidad
            for j in range(len(trail) - 1):
                alpha = j / len(trail)  # Opacidad progresiva
                pt1 = trail[j]
                pt2 = trail[j + 1]
                
                # Crear overlay para transparencia
                overlay = frame.copy()
                cv2.line(overlay, pt1, pt2, color, 3)
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
            
            # Dibujar círculo en posición actual
            cv2.circle(frame, trail[-1], 8, color, -1)
            
            # Mostrar velocidad
            cv2.putText(frame,
                       f"{info['hand']}: {info['velocity']:.1f} px/frame",
                       (int(trail[-1][0]) + 10, int(trail[-1][1])),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame


class MultiHandAnalyzer:
    """Analizador de interacciones entre múltiples manos"""
    
    def __init__(self):
        self.detector = HandDetector(max_hands=2)
    
    def analyze_interaction(self, frame):
        """
        Analiza la interacción entre dos manos
        
        Args:
            frame: Frame actual
            
        Returns:
            dict: Información de interacción
        """
        results, _ = self.detector.detect_hands(frame)
        hands_info = self.detector.get_hand_info(results, frame)
        
        interaction_data = {
            'hands_count': len(hands_info),
            'distance': None,
            'relative_position': None,
            'interacting': False
        }
        
        if len(hands_info) == 2:
            # Obtener puntas de dedos medios
            hand1_tip = hands_info[0]['landmarks'][12]
            hand2_tip = hands_info[1]['landmarks'][12]
            
            hand1_pos = (hand1_tip['x'], hand1_tip['y'])
            hand2_pos = (hand2_tip['x'], hand2_tip['y'])
            
            distance = HandUtils.calculate_distance(hand1_pos, hand2_pos)
            
            interaction_data['distance'] = distance
            interaction_data['interacting'] = distance < 100  # 100 píxeles
            
            # Relación espacial
            if hand1_pos[0] < hand2_pos[0]:
                interaction_data['relative_position'] = 'Left hand is left'
            else:
                interaction_data['relative_position'] = 'Right hand is left'
        
        return interaction_data
    
    def draw_interaction_info(self, frame, interaction_data):
        """
        Dibuja información de interacción
        
        Args:
            frame: Frame original
            interaction_data: Datos de interacción
            
        Returns:
            frame: Frame anotado
        """
        y_offset = 30
        
        # Manos detectadas
        text = f"Manos: {interaction_data['hands_count']}"
        cv2.putText(frame, text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if interaction_data['distance']:
            y_offset += 40
            text = f"Distancia: {interaction_data['distance']:.1f} px"
            cv2.putText(frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            y_offset += 40
            if interaction_data['interacting']:
                text = "¡INTERACCIÓN DETECTADA!"
                color = (0, 0, 255)
                thickness = 3
            else:
                text = "Sin interacción"
                color = (0, 255, 0)
                thickness = 2
            
            cv2.putText(frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness)
        
        return frame


def demo_gesture_recognition():
    """Demo del reconocedor de gestos"""
    print("=== Demo: Reconocimiento de Gestos ===")
    
    recognizer = GestureRecognizer()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gestures = recognizer.recognize_gestures(frame)
        frame = recognizer.draw_gesture_info(frame, gestures)
        
        cv2.imshow('Gesture Recognition', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def demo_hand_tracking():
    """Demo del seguidor de manos"""
    print("=== Demo: Seguimiento de Manos ===")
    
    tracker = HandTracker()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        tracking_info = tracker.track_hands(frame)
        frame = tracker.draw_trails(frame, tracking_info)
        
        cv2.imshow('Hand Tracking', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def demo_multi_hand_analysis():
    """Demo del analizador de múltiples manos"""
    print("=== Demo: Análisis de Múltiples Manos ===")
    
    analyzer = MultiHandAnalyzer()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        results, _ = analyzer.detector.detect_hands(frame)
        frame = analyzer.detector.draw_landmarks(frame, results)
        
        interaction_data = analyzer.analyze_interaction(frame)
        frame = analyzer.draw_interaction_info(frame, interaction_data)
        
        cv2.imshow('Multi-Hand Analysis', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("Ejemplos Avanzados de Detección de Manos")
    print("\nSelecciona una opción:")
    print("1. Reconocimiento de Gestos")
    print("2. Seguimiento de Manos")
    print("3. Análisis de Múltiples Manos")
    
    choice = input("\nOpción (1-3): ").strip()
    
    if choice == '1':
        demo_gesture_recognition()
    elif choice == '2':
        demo_hand_tracking()
    elif choice == '3':
        demo_multi_hand_analysis()
    else:
        print("Opción inválida")
