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
        
        # --- MediaPipe Setup ---
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils 
        
        # --- TIMING & STABILITY CONTROLS ---
        self.last_prediction = -1
        self.stable_frame_count = 0
        self.STABILITY_THRESHOLD = 8 
        
        self.current_sequence = ""
        self.last_digit_time = 0 # Track when we last added to the sequence (e.g. 5-5-2)
        
        # --- NEW: COOLDOWN TIMER ---
        self.last_trigger_time = 0
        self.COOLDOWN_SECONDS = 1.0 # <--- 1 Second Delay between inputs
        
        # Motion State
        self.prev_index_y = None
        self.is_pinching = False

    def get_dist(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def process_hand(self, landmarks, label):
        # 1. Left Hand Only (Mirrored label is "Right")
        if label == "Left": return -1, None

        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        index_tip = landmarks[8]
        pinky_base = landmarks[17]

        # 2. Disconnect (Thumbs Down)
        if thumb_tip.y > thumb_mcp.y and index_tip.y < thumb_mcp.y:
            return -1, "DISCONNECT"

        # 3. Finger States
        fingers = []
        # Thumb Open Check
        if self.get_dist(thumb_tip, pinky_base) > self.get_dist(thumb_ip, pinky_base):
            thumb_is_open = True
        else:
            thumb_is_open = False
            
        # Fingers 2-5
        for tip_id in [8, 12, 16, 20]:
            if landmarks[tip_id].y < landmarks[tip_id - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        total_fingers = fingers.count(1)

        # 4. Pinch (Select) - Increased distance for easier pinch
        if self.get_dist(thumb_tip, index_tip) < 0.07:
            if not self.is_pinching:
                self.is_pinching = True
                return -1, "SELECT"
            return -1, None 
        else:
            self.is_pinching = False

        # 5. Scroll (Index Only)
        if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0:
            current_y = index_tip.y
            if self.prev_index_y is not None:
                diff = self.prev_index_y - current_y
                if diff > 0.05: # Stricter threshold for scroll
                    self.prev_index_y = current_y
                    return -1, "SCROLL_UP"
                elif diff < -0.05:
                    self.prev_index_y = current_y
                    return -1, "SCROLL_DOWN"
            else:
                self.prev_index_y = current_y
            return -1, None
        else:
            self.prev_index_y = None

        # 6. Digits (1-9)
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
            # if total_fingers == 0: return 0, None # Optional: Ignore 0/Fist to avoid noise

        return -1, None

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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
            
            # --- COOLDOWN CHECK ---
            # If we just triggered an action, skip processing for 1 second
            if time.time() - self.last_trigger_time < self.COOLDOWN_SECONDS:
                # We still draw the skeleton so the UI doesn't look frozen
                if results.multi_hand_landmarks:
                    for hand_lm in results.multi_hand_landmarks:
                        self.mp_draw.draw_landmarks(frame, hand_lm, self.mp_hands.HAND_CONNECTIONS)
                
                cv2.imshow("Gesture Debug", frame)
                cv2.waitKey(1)
                continue # SKIP LOGIC LOOP
            
            if results.multi_hand_landmarks:
                for idx, hand_lm in enumerate(results.multi_hand_landmarks):
                    lbl = results.multi_handedness[idx].classification[0].label
                    self.mp_draw.draw_landmarks(frame, hand_lm, self.mp_hands.HAND_CONNECTIONS)
                    
                    digit, action = self.process_hand(hand_lm.landmark, lbl)
                    if digit != -1 or action is not None:
                        break 

            # --- EMIT SIGNALS (With Cooldown Trigger) ---
            triggered = False
            
            if action == "DISCONNECT":
                print(">>> Action: DISCONNECT")
                self.disconnect_detected.emit()
                triggered = True
                
            elif action == "SELECT":
                print(">>> Action: SELECT")
                self.select_detected.emit()
                triggered = True
                
            elif action == "SCROLL_UP":
                print(">>> Action: SCROLL UP")
                self.scroll_detected.emit("UP")
                triggered = True # Scroll also gets a delay (prevents jumpy lists)
                
            elif action == "SCROLL_DOWN":
                print(">>> Action: SCROLL DOWN")
                self.scroll_detected.emit("DOWN")
                triggered = True

            # Digit Logic
            if digit != -1 and action is None:
                if digit == self.last_prediction:
                    self.stable_frame_count += 1
                else:
                    self.stable_frame_count = 0
                    self.last_prediction = digit
                
                if self.stable_frame_count == self.STABILITY_THRESHOLD:
                    print(f">>> Digit: {digit}")
                    self.process_digit(digit)
                    triggered = True

            # If ANY action happened, reset the cooldown timer
            if triggered:
                self.last_trigger_time = time.time()
                self.stable_frame_count = 0 # Reset stability
                self.prev_index_y = None    # Reset scroll state

            cv2.imshow("Gesture Debug", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        
        cap.release()
        cv2.destroyAllWindows()

    def process_digit(self, digit):
        current_time = time.time()
        # Reset sequence if user waited more than 2 seconds between digits
        if current_time - self.last_digit_time > 2.0:
            self.current_sequence = ""
            
        self.last_digit_time = current_time
        self.current_sequence += str(digit)
        self.gesture_detected.emit(self.current_sequence)

    def stop(self):
        self.running = False
        self.wait()