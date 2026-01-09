import cv2
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal
import time
import math
import numpy as np

class GestureEngine(QThread):
    """Enhanced gesture recognition engine with ML-ready architecture"""
    
    # Signals
    gesture_detected = pyqtSignal(str, float)  # digit, confidence
    scroll_detected = pyqtSignal(str)
    select_detected = pyqtSignal()
    disconnect_detected = pyqtSignal()
    swipe_detected = pyqtSignal(str)  # LEFT or RIGHT
    cancel_detected = pyqtSignal()
    confidence_update = pyqtSignal(float)  # Real-time confidence
    
    # ---- ENHANCED CONFIG ----
    STABILITY_THRESHOLD = 6
    COOLDOWN_SECONDS = 0.8
    SCROLL_INTERVAL = 0.3
    PINCH_THRESHOLD = 0.06
    DISCONNECT_HOLD_TIME = 1.5
    CANCEL_HOLD_TIME = 1.0
    SCROLL_TOP_ZONE = 0.22
    SCROLL_BOTTOM_ZONE = 0.78
    SWIPE_THRESHOLD = 0.2
    CONFIDENCE_THRESHOLD = 0.7
    # -------------------------

    def __init__(self, settings=None):
        super().__init__()
        self.running = True
        self.settings = settings or {}
        
        # Apply custom settings
        self.hand_mode = self.settings.get('hand_mode', 'right')  # 'left' or 'right'
        self.sensitivity = self.settings.get('sensitivity', 1.0)
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=1,  # Upgraded for better accuracy
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
        
        # Gesture state
        self.is_pinching = False
        self.disconnect_start_time = None
        self.cancel_start_time = None
        
        # Swipe detection
        self.prev_wrist_x = None
        self.swipe_samples = []
        
        # Performance metrics
        self.metrics = {
            'detections': 0,
            'false_positives': 0,
            'avg_confidence': [],
            'frame_times': []
        }

    def get_dist(self, p1, p2):
        """Calculate Euclidean distance between two landmarks"""
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def calculate_hand_stability(self, landmarks):
        """Calculate gesture stability/confidence score"""
        # Check finger tip distances from palm center
        palm_center = landmarks[9]
        
        # Measure finger extension consistency
        finger_tips = [landmarks[i] for i in [4, 8, 12, 16, 20]]
        distances = [self.get_dist(tip, palm_center) for tip in finger_tips]
        
        # Lower variance = more stable gesture
        variance = np.var(distances)
        confidence = max(0.0, min(1.0, 1.0 - variance * 10))
        
        return confidence

    def detect_swipe(self, wrist):
        """Detect horizontal swipe gestures"""
        if self.prev_wrist_x is None:
            self.prev_wrist_x = wrist.x
            return None
        
        dx = wrist.x - self.prev_wrist_x
        self.swipe_samples.append(dx)
        
        # Keep last 5 frames
        if len(self.swipe_samples) > 5:
            self.swipe_samples.pop(0)
        
        # Check for consistent movement
        if len(self.swipe_samples) >= 5:
            avg_dx = sum(self.swipe_samples) / len(self.swipe_samples)
            if abs(avg_dx) > self.SWIPE_THRESHOLD / 5:
                self.swipe_samples.clear()
                self.prev_wrist_x = wrist.x
                return "RIGHT" if avg_dx > 0 else "LEFT"
        
        self.prev_wrist_x = wrist.x
        return None

    def process_hand(self, lm, handedness):
        """Enhanced gesture processing with confidence scoring"""
        # Calculate stability
        confidence = self.calculate_hand_stability(lm)
        self.last_confidence = confidence
        
        if confidence < self.CONFIDENCE_THRESHOLD:
            return -1, None, 0.0
        
        # Key landmarks
        thumb_tip, thumb_ip, thumb_mcp = lm[4], lm[3], lm[2]
        index_tip, index_mcp = lm[8], lm[5]
        middle_tip = lm[12]
        ring_tip = lm[16]
        pinky_tip, pinky_base = lm[20], lm[17]
        wrist = lm[0]

        # Mirror gestures for left-handed mode
        if self.hand_mode == 'left' and handedness == 'Right':
            # User is using wrong hand, reduce confidence
            confidence *= 0.7

        # 1. CANCEL GESTURE (Open palm hold)
        all_fingers_open = all(lm[tip].y < lm[tip-2].y for tip in [8, 12, 16, 20])
        thumb_open = self.get_dist(thumb_tip, pinky_base) > self.get_dist(thumb_ip, pinky_base)
        
        if all_fingers_open and thumb_open:
            if self.cancel_start_time is None:
                self.cancel_start_time = time.time()
            elif time.time() - self.cancel_start_time > self.CANCEL_HOLD_TIME:
                return -1, "CANCEL", confidence
        else:
            self.cancel_start_time = None

        # 2. DISCONNECT (Thumbs down - Highest Priority)
        thumbs_down = thumb_tip.y > thumb_mcp.y and index_tip.y < thumb_mcp.y
        if thumbs_down:
            if self.disconnect_start_time is None:
                self.disconnect_start_time = time.time()
            elif time.time() - self.disconnect_start_time > self.DISCONNECT_HOLD_TIME:
                return -1, "DISCONNECT", confidence
        else:
            self.disconnect_start_time = None

        # 3. SWIPE DETECTION (Alphabet jump)
        swipe_dir = self.detect_swipe(wrist)
        if swipe_dir:
            return -1, f"SWIPE_{swipe_dir}", confidence

        # 4. SCROLL CHECK (Zone Locking)
        if wrist.y < self.SCROLL_TOP_ZONE:
            return -1, "SCROLL_UP", confidence
        elif wrist.y > self.SCROLL_BOTTOM_ZONE:
            return -1, "SCROLL_DOWN", confidence

        # 5. PINCH (Select)
        pinch_dist = self.get_dist(thumb_tip, index_tip)
        if pinch_dist < self.PINCH_THRESHOLD * self.sensitivity:
            if not self.is_pinching:
                self.is_pinching = True
                return -1, "SELECT", confidence
            return -1, None, confidence
        self.is_pinching = False

        # 6. NUMERIC GESTURES (T9-Style: 0-9)
        fingers = []
        thumb_open = self.get_dist(thumb_tip, pinky_base) > self.get_dist(thumb_ip, pinky_base)

        # Count extended fingers
        for tip in [8, 12, 16, 20]:
            fingers.append(1 if lm[tip].y < lm[tip - 2].y else 0)

        count = fingers.count(1)

        # Digit mapping
        if thumb_open:
            # With thumb: 5-9
            digit = {0: -1, 1: 6, 2: 7, 3: 8, 4: 9}.get(count, -1)
            if count == 4:  # All fingers + thumb = 5
                digit = 5
        else:
            # Without thumb: 0-4
            digit = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}.get(count, -1)

        return digit, None, confidence

    def run(self):
        """Main detection loop with performance monitoring"""
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
            if not ret:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            
            # Adaptive brightness (lighting normalization)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)
            if avg_brightness < 100:
                frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=20)
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            digit, action, confidence = -1, None, 0.0

            # Cooldown check
            if time.time() - self.last_trigger_time < self.COOLDOWN_SECONDS:
                self.draw_debug_ui(frame, "COOLDOWN", confidence)
                cv2.imshow("Gesture Engine", frame)
                cv2.waitKey(1)
                continue

            if results.multi_hand_landmarks and results.multi_handedness:
                lm = results.multi_hand_landmarks[0]
                handedness = results.multi_handedness[0].classification[0].label
                
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(
                    frame, lm, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2),
                    self.mp_draw.DrawingSpec(color=(255, 0, 255), thickness=2)
                )
                
                digit, action, confidence = self.process_hand(lm.landmark, handedness)

            # Emit confidence updates
            self.confidence_update.emit(confidence)

            triggered = False

            # Handle actions
            if action == "CANCEL":
                self.cancel_detected.emit()
                triggered = True

            elif action == "DISCONNECT":
                self.disconnect_detected.emit()
                triggered = True

            elif action == "SELECT":
                self.select_detected.emit()
                triggered = True

            elif action and action.startswith("SWIPE_"):
                direction = action.split("_")[1]
                self.swipe_detected.emit(direction)
                triggered = True

            elif action in ["SCROLL_UP", "SCROLL_DOWN"]:
                if time.time() - self.last_scroll_time > self.SCROLL_INTERVAL:
                    self.scroll_detected.emit(action.split("_")[1])
                    self.last_scroll_time = time.time()

            elif digit != -1:
                if digit == self.last_prediction:
                    self.stable_frame_count += 1
                else:
                    self.last_prediction = digit
                    self.stable_frame_count = 0

                if self.stable_frame_count >= self.STABILITY_THRESHOLD:
                    self.gesture_detected.emit(str(digit), confidence)
                    triggered = True
                    self.metrics['detections'] += 1
                    self.metrics['avg_confidence'].append(confidence)

            if triggered:
                self.last_trigger_time = time.time()
                self.stable_frame_count = 0

            # Draw debug UI
            status = action or (f"DIGIT: {digit}" if digit != -1 else "READY")
            self.draw_debug_ui(frame, status, confidence)

            # Performance tracking
            frame_time = time.time() - frame_start
            self.metrics['frame_times'].append(frame_time)
            if len(self.metrics['frame_times']) > 100:
                self.metrics['frame_times'].pop(0)

            cv2.imshow("Gesture Engine", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.print_metrics()

    def draw_debug_ui(self, frame, status, confidence):
        """Draw debug overlay on camera feed"""
        h, w = frame.shape[:2]
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Status text
        cv2.putText(frame, f"STATUS: {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Confidence bar
        bar_width = int(confidence * 300)
        color = (0, 255, 0) if confidence > 0.7 else (0, 165, 255)
        cv2.rectangle(frame, (10, 50), (10 + bar_width, 70), color, -1)
        cv2.rectangle(frame, (10, 50), (310, 70), (255, 255, 255), 2)
        cv2.putText(frame, f"{confidence:.2f}", (320, 67),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Zone indicators
        top_line = int(h * self.SCROLL_TOP_ZONE)
        bottom_line = int(h * self.SCROLL_BOTTOM_ZONE)
        cv2.line(frame, (0, top_line), (w, top_line), (255, 0, 0), 1)
        cv2.line(frame, (0, bottom_line), (w, bottom_line), (255, 0, 0), 1)

    def print_metrics(self):
        """Print performance metrics on shutdown"""
        if self.metrics['avg_confidence']:
            avg_conf = sum(self.metrics['avg_confidence']) / len(self.metrics['avg_confidence'])
            avg_fps = 1.0 / (sum(self.metrics['frame_times']) / len(self.metrics['frame_times']))
            print(f"\n=== GESTURE ENGINE METRICS ===")
            print(f"Total Detections: {self.metrics['detections']}")
            print(f"Average Confidence: {avg_conf:.2f}")
            print(f"Average FPS: {avg_fps:.1f}")
            print(f"==============================\n")

    def stop(self):
        """Clean shutdown"""
        self.running = False
        self.wait()
