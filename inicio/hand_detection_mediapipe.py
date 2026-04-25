import cv2
import mediapipe as mp
import numpy as np
from collections import deque

class HandDetector:
    """Detector de manos usando MediaPipe con seguimiento de puntos clave"""
    
    def __init__(self, max_hands=2, confidence=0.7):
        """
        Inicializa el detector de manos
        
        Args:
            max_hands (int): Número máximo de manos a detectar
            confidence (float): Confianza mínima para detección (0-1)
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=confidence,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.landmarks_history = deque(maxlen=10)  # Historial de puntos
        
    def detect_hands(self, frame):
        """
        Detecta manos en un frame
        
        Args:
            frame: Imagen de entrada (BGR)
            
        Returns:
            results: Resultados de MediaPipe
            frame_rgb: Frame convertido a RGB
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        return results, frame_rgb
    
    def draw_landmarks(self, frame, results):
        """
        Dibuja los puntos clave de las manos detectadas
        
        Args:
            frame: Frame original
            results: Resultados de MediaPipe
            
        Returns:
            frame: Frame con landmarks dibujados
        """
        h, w, c = frame.shape
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dibujar conexiones y puntos
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(
                        color=(0, 255, 0),
                        thickness=2,
                        circle_radius=1
                    ),
                    self.mp_drawing.DrawingSpec(
                        color=(255, 0, 0),
                        thickness=2
                    )
                )
                
                # Guardar coordenadas de puntos clave
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    z = landmark.z
                    landmarks.append((x, y, z))
                
                self.landmarks_history.append(landmarks)
        
        return frame
    
    def get_hand_info(self, results, frame):
        """
        Obtiene información detallada de cada mano detectada
        
        Args:
            results: Resultados de MediaPipe
            frame: Frame original
            
        Returns:
            dict: Información de manos detectadas
        """
        h, w, c = frame.shape
        hands_info = []
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                hand_label = handedness.classification[0].label  # "Left" o "Right"
                confidence = handedness.classification[0].score
                
                landmarks = []
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    z = landmark.z
                    landmarks.append({
                        'point_id': idx,
                        'x': x,
                        'y': y,
                        'z': z,
                        'name': self._get_landmark_name(idx)
                    })
                
                hands_info.append({
                    'hand': hand_label,
                    'confidence': confidence,
                    'landmarks': landmarks
                })
        
        return hands_info
    
    def _get_landmark_name(self, idx):
        """Obtiene el nombre del punto clave"""
        names = [
            'Wrist', 'Thumb_CMC', 'Thumb_MCP', 'Thumb_IP', 'Thumb_Tip',
            'Index_MCP', 'Index_PIP', 'Index_DIP', 'Index_Tip',
            'Middle_MCP', 'Middle_PIP', 'Middle_DIP', 'Middle_Tip',
            'Ring_MCP', 'Ring_PIP', 'Ring_DIP', 'Ring_Tip',
            'Pinky_MCP', 'Pinky_PIP', 'Pinky_DIP', 'Pinky_Tip'
        ]
        return names[idx] if idx < len(names) else f'Point_{idx}'
    
    def calculate_hand_distance(self, landmarks):
        """
        Calcula distancia entre puntos clave de la mano
        
        Args:
            landmarks: Lista de puntos clave
            
        Returns:
            float: Distancia entre muñeca y punta del dedo medio
        """
        wrist = np.array([landmarks[0][0], landmarks[0][1]])
        middle_tip = np.array([landmarks[12][0], landmarks[12][1]])
        distance = np.linalg.norm(wrist - middle_tip)
        return distance
    
    def release(self):
        """Libera recursos"""
        self.hands.close()


def main():
    """Función principal para detección de manos en tiempo real"""
    
    # Inicializar detector
    detector = HandDetector(max_hands=2, confidence=0.7)
    
    # Abrir cámara
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Presiona 'q' para salir")
    print("Presiona 's' para guardar screenshot")
    
    frame_count = 0
    
    while True:
        success, frame = cap.read()
        if not success:
            print("No se pudo leer el frame")
            break
        
        # Detectar manos
        results, frame_rgb = detector.detect_hands(frame)
        
        # Dibujar landmarks
        frame = detector.draw_landmarks(frame, results)
        
        # Obtener información de manos
        hands_info = detector.get_hand_info(results, frame)
        
        # Mostrar información
        y_offset = 30
        cv2.putText(frame, f'Manos detectadas: {len(hands_info)}',
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                   1, (0, 255, 0), 2)
        
        for i, hand in enumerate(hands_info):
            y_offset += 40
            cv2.putText(frame,
                       f"Mano {i+1}: {hand['hand']} ({hand['confidence']:.2f})",
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (255, 0, 0), 2)
            
            # Mostrar algunos puntos clave importantes
            if len(hand['landmarks']) > 12:
                y_offset += 30
                middle_tip = hand['landmarks'][12]
                cv2.putText(frame,
                           f"Dedo Medio: ({middle_tip['x']}, {middle_tip['y']})",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (0, 255, 255), 1)
        
        # Mostrar FPS
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Frame: {frame_count}")
        
        # Mostrar frame
        cv2.imshow('Detección de Manos - MediaPipe', frame)
        
        # Control de teclado
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite(f'hand_detection_{frame_count}.jpg', frame)
            print(f"Imagen guardada: hand_detection_{frame_count}.jpg")
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    detector.release()
    print("Programa finalizado")


if __name__ == "__main__":
    main()
