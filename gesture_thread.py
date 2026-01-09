import cv2
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal
import time
import math

class GestureThread(QThread):
    gesture_detected = pyqtSignal(str) 
    scroll_detected = pyqtSignal(str)  
    select_detected = pyqtSignal()
    disconnect_detected = pyqtSignal() 
    
    def __init__(self):
        super().__init__()
        self.running = True
        
        # Optimized MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils 
        
        # State Variables
        self.last_prediction = -1
        self.stable_frame_count = 0
        self.STABILITY_THRESHOLD = 8 
        self.last_trigger_time = 0
        self.COOLDOWN_SECONDS = 1.0
        self.is_pinching = False

    def get_dist(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def process_hand(self, landmarks):
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        index_tip = landmarks[8]
        pinky_base = landmarks[17]
        wrist = landmarks[0] # Use Wrist for Height check

        # --- 1. DISCONNECT (Thumbs Down) ---
        # Logic: Thumb is below Knuckle, and Index is above Thumb Knuckle
        if thumb_tip.y > thumb_mcp.y and index_tip.y < thumb_mcp.y:
             return -1, "DISCONNECT"

        # --- 2. PINCH (Select) ---
        if self.get_dist(thumb_tip, index_tip) < 0.07:
            if not self.is_pinching:
                self.is_pinching = True
                return -1, "SELECT"
            return -1, None 
        else:
            self.is_pinching = False

        # --- 3. SCROLL (Elevation Based - Joystick) ---
        # If Hand (Wrist) is in Top 20% of screen -> Scroll UP
        # If Hand (Wrist) is in Bottom 20% of screen -> Scroll DOWN
        # Note: In CV coords, y=0 is top, y=1 is bottom.
        
        if wrist.y < 0.25: # High up
            return -1, "SCROLL_UP"
        elif wrist.y > 0.75: # Low down
            return -1, "SCROLL_DOWN"

        # --- 4. DIGIT RECOGNITION (1-9) ---
        # Count Fingers
        fingers = []
        
        # Thumb Open Check
        if self.get_dist(thumb_tip, pinky_base) > self.get_dist(thumb_ip, pinky_base):
            thumb_is_open = True
        else:
            thumb_is_open = False
            
        for tip_id in [8, 12, 16, 20]:
            if landmarks[tip_id].y < landmarks[tip_id - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        total_fingers = fingers.count(1)

        if thumb_is_open:
            if total_fingers == 0: return 6, None
            if total_fingers == 1: return 7, None
            if total_fingers == 2: return 8, None
            if total_fingers == 3: return 9, None
            if total_fingers == 4: return 5, None
        else:
            if total_fingers == 1: return 1, None
            if total_fingers == 2: return 2, None
            if total_fingers == 3: return 3, None
            if total_fingers == 4: return 4, None
            if total_fingers == 0: return 0, None # "0"

        return -1, None

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, 640) # Width
        cap.set(4, 480) # Height

        while self.running:
            ret, frame = cap.read()
            if not ret: 
                time.sleep(0.1)
                continue
            
            frame = cv2.flip(frame, 1) 
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            
            digit = -1
            action = None
            
            # Draw visual zones for Scrolling
            h, w, _ = frame.shape
            cv2.line(frame, (0, int(h*0.25)), (w, int(h*0.25)), (0, 255, 255), 2) # Top Line
            cv2.line(frame, (0, int(h*0.75)), (w, int(h*0.75)), (0, 255, 255), 2) # Bottom Line

            # COOLDOWN BLOCK
            if time.time() - self.last_trigger_time < self.COOLDOWN_SECONDS:
                cv2.imshow("Gesture Debug", frame)
                cv2.waitKey(1)
                continue 

            if results.multi_hand_landmarks:
                for hand_lm in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_lm, self.mp_hands.HAND_CONNECTIONS)
                    digit, action = self.process_hand(hand_lm.landmark)
                    if digit != -1 or action is not None:
                        break 

            # EMIT SIGNALS
            triggered = False
            if action == "DISCONNECT":
                self.disconnect_detected.emit()
                triggered = True
            elif action == "SELECT":
                self.select_detected.emit()
                triggered = True
            elif action == "SCROLL_UP":
                self.scroll_detected.emit("UP")
                # No trigger delay for scroll to allow continuous movement
            elif action == "SCROLL_DOWN":
                self.scroll_detected.emit("DOWN")
            
            elif digit != -1:
                if digit == self.last_prediction:
                    self.stable_frame_count += 1
                else:
                    self.stable_frame_count = 0
                    self.last_prediction = digit
                
                if self.stable_frame_count == self.STABILITY_THRESHOLD:
                    # Fix: Send digit immediately
                    self.gesture_detected.emit(str(digit))
                    triggered = True

            if triggered:
                self.last_trigger_time = time.time()
                self.stable_frame_count = 0

            cv2.imshow("Gesture Debug", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        
        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False
        self.wait()