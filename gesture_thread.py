import cv2
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal
import time
import math

class GestureThread(QThread):
    gesture_detected = pyqtSignal(str) 
    scroll_detected = pyqtSignal(str)  
    select_detected = pyqtSignal()     
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        # VISUAL DEBUGGER TOOL
        self.mp_draw = mp.solutions.drawing_utils 
        
        # Stability / Debouncing
        self.last_prediction = -1
        self.stable_frame_count = 0
        self.STABILITY_THRESHOLD = 5 # Reduced for faster response during testing
        self.last_gesture_time = 0
        self.current_sequence = ""
        
        # Motion Tracking
        self.prev_index_y = None
        self.SCROLL_THRESH = 0.04 
        self.is_pinching = False

    def calculate_distance(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def detect_gesture_and_action(self, landmarks):
        fingers = []
        
        # Thumb Logic (Simplified for general use)
        # If thumb tip (4) is to the left of IP joint (3) -> Open (For Right Hand)
        if landmarks[4].x < landmarks[3].x: 
            fingers.append(1)
        else:
            fingers.append(0)
            
        # Fingers 2-5 (Index to Pinky)
        for tip in [8, 12, 16, 20]:
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        total_fingers = fingers.count(1)
        
        # --- ACTION: PINCH (SELECT) ---
        pinch_dist = self.calculate_distance(landmarks[4], landmarks[8])
        if pinch_dist < 0.05:
            if not self.is_pinching:
                self.is_pinching = True
                return -1, "SELECT"
            return -1, None 
        else:
            self.is_pinching = False

        # --- ACTION: SCROLL (Index Only) ---
        # Pattern: Index(1) is UP, others are DOWN
        # Note: We check if total_fingers is 1 AND index is the one up
        if total_fingers == 1 and fingers[1] == 1:
            current_y = landmarks[8].y
            if self.prev_index_y is not None:
                diff = self.prev_index_y - current_y
                if diff > self.SCROLL_THRESH:
                    self.prev_index_y = current_y
                    return -1, "SCROLL_UP"
                elif diff < -self.SCROLL_THRESH:
                    self.prev_index_y = current_y
                    return -1, "SCROLL_DOWN"
            else:
                self.prev_index_y = current_y
            return -1, None
        else:
            self.prev_index_y = None

        # --- DIGIT RECOGNITION ---
        if total_fingers <= 5 and total_fingers > 0:
            # Check ASL 6 (Pinky + Thumb touch)
            if self.calculate_distance(landmarks[4], landmarks[20]) < 0.05: return 6, None
            # ASL 7 (Ring + Thumb touch)
            elif self.calculate_distance(landmarks[4], landmarks[16]) < 0.05: return 7, None
            # ASL 8 (Middle + Thumb touch)
            elif self.calculate_distance(landmarks[4], landmarks[12]) < 0.05: return 8, None
            
            return total_fingers, None
            
        elif total_fingers == 0:
            return 0, None

        return -1, None

    def run(self):
        # Try index 0 first, then 1 if camera doesn't open
        cap = cv2.VideoCapture(0) 
        
        while self.running:
            ret, frame = cap.read()
            if not ret: 
                print("Camera not detected! Trying to reconnect...")
                time.sleep(1)
                continue
            
            # Flip and Convert
            frame = cv2.flip(frame, 1) 
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            
            digit = -1
            action = None
            
            if results.multi_hand_landmarks:
                for hand_lm in results.multi_hand_landmarks:
                    # DRAW SKELETON (Visual Debug)
                    self.mp_draw.draw_landmarks(frame, hand_lm, self.mp_hands.HAND_CONNECTIONS)
                    
                    digit, action = self.detect_gesture_and_action(hand_lm.landmark)
            
            # --- SHOW DEBUG WINDOW ---
            cv2.imshow("Gesture Debug View (Press 'q' to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # --- EMIT SIGNALS ---
            if action == "SELECT":
                print(">>> Action: SELECT (Pinch)")
                self.select_detected.emit()
            elif action == "SCROLL_UP":
                print(">>> Action: SCROLL UP")
                self.scroll_detected.emit("UP")
            elif action == "SCROLL_DOWN":
                print(">>> Action: SCROLL DOWN")
                self.scroll_detected.emit("DOWN")
            
            if digit != -1 and action is None:
                if digit == self.last_prediction:
                    self.stable_frame_count += 1
                else:
                    self.stable_frame_count = 0
                    self.last_prediction = digit
                
                if self.stable_frame_count == self.STABILITY_THRESHOLD:
                    print(f">>> Digit Confirmed: {digit}")
                    self.process_digit(digit)
                    
        cap.release()
        cv2.destroyAllWindows()

    def process_digit(self, digit):
        current_time = time.time()
        if current_time - self.last_gesture_time > 2.0:
            self.current_sequence = ""
        self.last_gesture_time = current_time
        self.current_sequence += str(digit)
        self.gesture_detected.emit(self.current_sequence)
        self.stable_frame_count = 0
    
    def stop(self):
        self.running = False
        self.wait()