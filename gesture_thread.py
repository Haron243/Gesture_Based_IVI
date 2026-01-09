import cv2
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal
import time
import math

class GestureThread(QThread):
    gesture_detected = pyqtSignal(str) # For numbers
    scroll_detected = pyqtSignal(str)  # "UP" or "DOWN"
    select_detected = pyqtSignal()     # For Pinch click
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Stability / Debouncing
        self.last_prediction = -1
        self.stable_frame_count = 0
        self.STABILITY_THRESHOLD = 8
        self.last_gesture_time = 0
        self.current_sequence = ""
        
        # Motion Tracking for Scroll
        self.prev_index_y = None
        self.SCROLL_THRESH = 0.03 # Sensitivity for scroll motion
        
        # Pinch State
        self.is_pinching = False

    def calculate_distance(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def detect_gesture_and_action(self, landmarks):
        """
        Returns:
        - digit (int or -1)
        - action (str: "SCROLL_UP", "SCROLL_DOWN", "SELECT", or None)
        """
        # 1. Check Finger States (Up/Down)
        # Tips: Thumb=4, Index=8, Middle=12, Ring=16, Pinky=20
        fingers = []
        
        # Thumb (Complex: Check if tip is to the right/left of IP joint)
        # Assuming Right Hand logic for simplicity (can be flipped)
        if landmarks[4].x < landmarks[3].x: # Adjust based on hand (L/R)
            fingers.append(1)
        else:
            fingers.append(0)
            
        # Other 4 fingers (Check Y position relative to PIP joint)
        for tip in [8, 12, 16, 20]:
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        total_fingers = fingers.count(1)
        
        # --- ACTION: PINCH (SELECT) ---
        # Distance between Thumb(4) and Index(8)
        pinch_dist = self.calculate_distance(landmarks[4], landmarks[8])
        if pinch_dist < 0.05:
            if not self.is_pinching: # Trigger only on fresh pinch
                self.is_pinching = True
                return -1, "SELECT"
            return -1, None # Holding pinch
        else:
            self.is_pinching = False

        # --- ACTION: SCROLL (Index Finger Only) ---
        # If only Index is up (Pattern: 0,1,0,0,0) or (1,1,0,0,0 - thumb loose)
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            current_y = landmarks[8].y
            if self.prev_index_y is not None:
                diff = self.prev_index_y - current_y
                if diff > self.SCROLL_THRESH:
                    self.prev_index_y = current_y
                    return -1, "SCROLL_UP" # Finger moved Up
                elif diff < -self.SCROLL_THRESH:
                    self.prev_index_y = current_y
                    return -1, "SCROLL_DOWN" # Finger moved Down
            else:
                self.prev_index_y = current_y
            return -1, None # Moved, but not enough for threshold
        else:
            self.prev_index_y = None # Reset if gesture changes

        # --- DIGIT RECOGNITION (0-9) ---
        # Standard 0-5
        if total_fingers <= 5 and total_fingers > 0:
            # Check for ASL overrides (Touching Thumb)
            # ASL 6: Pinky(20) touches Thumb(4)
            if self.calculate_distance(landmarks[4], landmarks[20]) < 0.05:
                return 6, None
            # ASL 7: Ring(16) touches Thumb(4)
            elif self.calculate_distance(landmarks[4], landmarks[16]) < 0.05:
                return 7, None
            # ASL 8: Middle(12) touches Thumb(4)
            elif self.calculate_distance(landmarks[4], landmarks[12]) < 0.05:
                return 8, None
            
            # Default Count
            return total_fingers, None
            
        elif total_fingers == 0:
            return 0, None

        return -1, None

    def run(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if not ret: continue
            
            # Pre-process
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            
            digit = -1
            action = None
            
            if results.multi_hand_landmarks:
                # Only process first hand
                hand_lm = results.multi_hand_landmarks[0]
                digit, action = self.detect_gesture_and_action(hand_lm.landmark)
            
            # --- HANDLE ACTIONS IMMEDIATELLY (Low Latency) ---
            if action == "SELECT":
                self.select_detected.emit()
                self.stable_frame_count = 0 # Reset digits
            elif action == "SCROLL_UP":
                self.scroll_detected.emit("UP")
            elif action == "SCROLL_DOWN":
                self.scroll_detected.emit("DOWN")
                
            # --- HANDLE DIGITS (With Debounce) ---
            if digit != -1 and action is None:
                if digit == self.last_prediction:
                    self.stable_frame_count += 1
                else:
                    self.stable_frame_count = 0
                    self.last_prediction = digit
                
                if self.stable_frame_count == self.STABILITY_THRESHOLD:
                    self.process_digit(digit)
                    
        cap.release()

    def process_digit(self, digit):
        # ... (Same sequence logic as before: 5 -> 55 -> 552) ...
        # Copy the 'process_valid_input' logic from previous response here
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