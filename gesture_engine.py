import cv2
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal
import time
import math
import numpy as np

class GestureEngine(QThread):
    """Enhanced gesture recognition engine with Fixed Spatial Zones"""
    
    # Signals
    gesture_detected = pyqtSignal(str, float)
    spatial_update = pyqtSignal(int)   # -1 (Left) to 2 (Far Right)
    spatial_commit = pyqtSignal()      # NEW: Triggered by Fist
    scroll_detected = pyqtSignal(str)
    select_detected = pyqtSignal()
    disconnect_detected = pyqtSignal()
    swipe_detected = pyqtSignal(str)
    cancel_detected = pyqtSignal()
    confidence_update = pyqtSignal(float)
    
    # ---- ENHANCED CONFIG ----
    STABILITY_THRESHOLD = 5 # Reduced slightly for faster fist reaction
    COOLDOWN_SECONDS = 0.8
    SCROLL_INTERVAL = 0.3
    PINCH_THRESHOLD = 0.06
    DISCONNECT_HOLD_TIME = 1.5
    CANCEL_HOLD_TIME = 1.0
    
    # Y-Axis Zones (Scrolling)
    SCROLL_TOP_ZONE = 0.22
    SCROLL_BOTTOM_ZONE = 0.78
    
    # X-Axis Zones (Spatial T9 - FIXED CENTER)
    # 0.0 is Left, 1.0 is Right
    ZONE_LEFT_LIMIT = 0.40   # < 40% is Left
    ZONE_RIGHT_LIMIT = 0.60  # > 60% is Right
    ZONE_EXTREME_LEFT = 0.20 
    ZONE_EXTREME_RIGHT = 0.80
    
    SWIPE_THRESHOLD = 0.2
    CONFIDENCE_THRESHOLD = 0.7
    # -------------------------

    def __init__(self, settings=None):
        super().__init__()
        self.running = True
        self.settings = settings or {}
        
        self.hand_mode = self.settings.get('hand_mode', 'right')
        self.sensitivity = self.settings.get('sensitivity', 1.0)
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.6
        )
        self.mp_draw = mp.solutions.drawing_utils

        # State tracking
        self.last_prediction = -1
        self.stable_frame_count = 0
        self.last_trigger_time = 0
        self.last_scroll_time = 0
        self.last_confidence = 0.0
        
        # Spatial State
        self.current_spatial_index = 1
        self.was_holding_t9 = False # Track if we were just using T9
        
        self.is_pinching = False
        self.disconnect_start_time = None
        self.cancel_start_time = None
        
        self.prev_wrist_x = None
        self.swipe_samples = []
        
        self.metrics = {'detections': 0, 'false_positives': 0, 'avg_confidence': [], 'frame_times': []}

    def get_dist(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def calculate_hand_stability(self, landmarks):
        palm_center = landmarks[9]
        finger_tips = [landmarks[i] for i in [4, 8, 12, 16, 20]]
        distances = [self.get_dist(tip, palm_center) for tip in finger_tips]
        variance = np.var(distances)
        confidence = max(0.0, min(1.0, 1.0 - variance * 10))
        return confidence

    def detect_swipe(self, wrist):
        if self.prev_wrist_x is None:
            self.prev_wrist_x = wrist.x
            return None
        dx = wrist.x - self.prev_wrist_x
        self.swipe_samples.append(dx)
        if len(self.swipe_samples) > 5: self.swipe_samples.pop(0)
        
        if len(self.swipe_samples) >= 5:
            avg_dx = sum(self.swipe_samples) / len(self.swipe_samples)
            if abs(avg_dx) > self.SWIPE_THRESHOLD / 5:
                self.swipe_samples.clear()
                self.prev_wrist_x = wrist.x
                return "RIGHT" if avg_dx > 0 else "LEFT"
        self.prev_wrist_x = wrist.x
        return None

    def process_hand(self, lm, handedness):
        """Enhanced gesture processing"""
        confidence = self.calculate_hand_stability(lm)
        self.last_confidence = confidence
        
        if confidence < self.CONFIDENCE_THRESHOLD:
            # Lost tracking -> Reset T9 hold state safely
            self.was_holding_t9 = False 
            return -1, None, 0.0
        
        thumb_tip, thumb_ip, thumb_mcp = lm[4], lm[3], lm[2]
        index_tip = lm[8]
        pinky_tip, pinky_base = lm[20], lm[17]
        wrist = lm[0]

        if self.hand_mode == 'left' and handedness == 'Right':
            confidence *= 0.7

        # --- 1. STRICT DISCONNECT (Thumbs Down + Index Curled) ---
        thumb_is_down = thumb_tip.y > thumb_mcp.y
        index_is_closed = lm[8].y > lm[6].y 

        if thumb_is_down and index_is_closed:
            if self.disconnect_start_time is None:
                self.disconnect_start_time = time.time()
            elif time.time() - self.disconnect_start_time > self.DISCONNECT_HOLD_TIME:
                return -1, "DISCONNECT", confidence
        else:
            self.disconnect_start_time = None

        # --- 2. CANCEL GESTURE (Shaka) ---
        thumb_open = self.get_dist(thumb_tip, pinky_base) > self.get_dist(thumb_ip, pinky_base)
        pinky_open = lm[20].y < lm[18].y
        middle_closed = (lm[8].y > lm[6].y and lm[12].y > lm[10].y and lm[16].y > lm[14].y)
        
        if thumb_open and pinky_open and middle_closed:
            if self.cancel_start_time is None:
                self.cancel_start_time = time.time()
            elif time.time() - self.cancel_start_time > self.CANCEL_HOLD_TIME:
                return -1, "CANCEL", confidence
        else:
            self.cancel_start_time = None

        # --- 3. SWIPE ---
        swipe_dir = self.detect_swipe(wrist)
        if swipe_dir: return -1, f"SWIPE_{swipe_dir}", confidence

        # --- 4. SCROLL ---
        if wrist.y < self.SCROLL_TOP_ZONE: return -1, "SCROLL_UP", confidence
        elif wrist.y > self.SCROLL_BOTTOM_ZONE: return -1, "SCROLL_DOWN", confidence

        # --- 5. PINCH ---
        pinch_dist = self.get_dist(thumb_tip, index_tip)
        if pinch_dist < self.PINCH_THRESHOLD * self.sensitivity:
            if not self.is_pinching:
                self.is_pinching = True
                return -1, "SELECT", confidence
            return -1, None, confidence
        self.is_pinching = False

        # --- 6. NUMERIC GESTURES + SPATIAL ---
        fingers = []
        for tip in [8, 12, 16, 20]:
            fingers.append(1 if lm[tip].y < lm[tip - 2].y else 0)

        count = fingers.count(1)
        thumb_is_open = self.get_dist(thumb_tip, pinky_base) > self.get_dist(thumb_ip, pinky_base)

        if thumb_is_open:
            digit = {0: 6, 1: 7, 2: 8, 3: 9, 4: 5}.get(count, -1)
        else:
            digit = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}.get(count, -1)

        # === SPATIAL LOGIC (FIXED CENTER) ===
        
        # A. FIST COMMIT LOGIC
        # If we detect a Fist (0) AND we were previously holding a number -> Commit
        if digit == 0 and self.was_holding_t9:
            self.was_holding_t9 = False # Consume the commit
            return -1, "SPATIAL_COMMIT", confidence

        # B. T9 NUMBER HOLDING
        if digit != -1 and digit not in [0, 1]:
            self.was_holding_t9 = True # Mark that user is selecting
            
            # Use Fixed Screen Zones based on Wrist X Position
            x = wrist.x 
            new_index = 1 # Default Center
            
            if x < self.ZONE_EXTREME_LEFT: new_index = 0   # Far Left
            elif x < self.ZONE_LEFT_LIMIT: new_index = 0   # Left
            elif x > self.ZONE_EXTREME_RIGHT: new_index = 3 # Far Right
            elif x > self.ZONE_RIGHT_LIMIT: new_index = 2  # Right
            else: new_index = 1 # Center
            
            if new_index != self.current_spatial_index:
                self.current_spatial_index = new_index
                self.spatial_update.emit(new_index)
                
        # If hand drops or gesture becomes invalid, just maintain state briefly
        # until confidence drops or a specific "Disconnect" happens
        
        return digit, None, confidence

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Cannot open camera")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        while self.running:
            frame_start = time.time()
            ret, frame = cap.read()
            if not ret: time.sleep(0.1); continue

            frame = cv2.flip(frame, 1)
            
            # Brightness Norm
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if np.mean(gray) < 100:
                frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=20)
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            digit, action, confidence = -1, None, 0.0

            if time.time() - self.last_trigger_time < self.COOLDOWN_SECONDS:
                self.draw_debug_ui(frame, "COOLDOWN", confidence)
                cv2.imshow("Gesture Engine", frame)
                cv2.waitKey(1)
                continue

            if results.multi_hand_landmarks:
                lm = results.multi_hand_landmarks[0]
                handedness = results.multi_handedness[0].classification[0].label
                
                self.mp_draw.draw_landmarks(
                    frame, lm, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2),
                    self.mp_draw.DrawingSpec(color=(255, 0, 255), thickness=2)
                )
                
                digit, action, confidence = self.process_hand(lm.landmark, handedness)

            self.confidence_update.emit(confidence)
            triggered = False

            # Signal Routing
            if action == "SPATIAL_COMMIT": self.spatial_commit.emit(); triggered = True # NEW
            elif action == "CANCEL": self.cancel_detected.emit(); triggered = True
            elif action == "DISCONNECT": self.disconnect_detected.emit(); triggered = True
            elif action == "SELECT": self.select_detected.emit(); triggered = True
            elif action and action.startswith("SWIPE"): self.swipe_detected.emit(action.split("_")[1]); triggered = True
            elif action and "SCROLL" in action:
                if time.time() - self.last_scroll_time > self.SCROLL_INTERVAL:
                    self.scroll_detected.emit(action.split("_")[1])
                    self.last_scroll_time = time.time()
            elif digit != -1:
                if digit == self.last_prediction: self.stable_frame_count += 1
                else: self.last_prediction = digit; self.stable_frame_count = 0
                
                if self.stable_frame_count >= self.STABILITY_THRESHOLD:
                    self.gesture_detected.emit(str(digit), confidence)
                    self.metrics['detections'] += 1
                    # Note: We do NOT trigger cool-down for digits, to allow holding for spatial selection

            if triggered:
                self.last_trigger_time = time.time()
                self.stable_frame_count = 0
                self.was_holding_t9 = False # Reset state

            status = action or (f"DIGIT: {digit}" if digit != -1 else "READY")
            self.draw_debug_ui(frame, status, confidence)

            frame_time = time.time() - frame_start
            self.metrics['frame_times'].append(frame_time)
            if len(self.metrics['frame_times']) > 100: self.metrics['frame_times'].pop(0)

            cv2.imshow("Gesture Engine", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()
        self.print_metrics()

    def draw_debug_ui(self, frame, status, confidence):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        cv2.putText(frame, f"STATUS: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Draw Fixed Vertical Zones (Green Lines)
        cx_left = int(w * self.ZONE_LEFT_LIMIT)
        cx_right = int(w * self.ZONE_RIGHT_LIMIT)
        
        # Center Zone
        cv2.line(frame, (cx_left, 100), (cx_left, 380), (0, 255, 0), 2)
        cv2.line(frame, (cx_right, 100), (cx_right, 380), (0, 255, 0), 2)
        
        # Labels
        cv2.putText(frame, "LEFT", (cx_left - 60, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, "RIGHT", (cx_right + 10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Scroll Zones (Blue Lines)
        top_line = int(h * self.SCROLL_TOP_ZONE)
        bottom_line = int(h * self.SCROLL_BOTTOM_ZONE)
        cv2.line(frame, (0, top_line), (w, top_line), (255, 0, 0), 1)
        cv2.line(frame, (0, bottom_line), (w, bottom_line), (255, 0, 0), 1)

    def print_metrics(self):
        if self.metrics['avg_confidence']:
            avg_conf = sum(self.metrics['avg_confidence']) / len(self.metrics['avg_confidence'])
            avg_fps = 1.0 / (sum(self.metrics['frame_times']) / len(self.metrics['frame_times']))
            print(f"\n=== GESTURE ENGINE METRICS ===")
            print(f"Total Detections: {self.metrics['detections']}")
            print(f"Average Confidence: {avg_conf:.2f}")
            print(f"Average FPS: {avg_fps:.1f}")
            print(f"==============================\n")

    def stop(self):
        self.running = False
        self.wait()