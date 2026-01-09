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

    # ---- CONFIG ----
    STABILITY_THRESHOLD = 8
    COOLDOWN_SECONDS = 1.0
    SCROLL_INTERVAL = 0.35
    PINCH_THRESHOLD = 0.07
    DISCONNECT_HOLD_TIME = 1.5
    SCROLL_TOP_ZONE = 0.25
    SCROLL_BOTTOM_ZONE = 0.75
    # ----------------

    def __init__(self):
        super().__init__()
        self.running = True

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.last_prediction = -1
        self.stable_frame_count = 0
        self.last_trigger_time = 0
        self.last_scroll_time = 0

        self.is_pinching = False
        self.disconnect_start_time = None

    def get_dist(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def process_hand(self, lm):
        thumb_tip, thumb_ip, thumb_mcp = lm[4], lm[3], lm[2]
        index_tip = lm[8]
        pinky_base = lm[17]
        wrist = lm[0]

        # 1. DISCONNECT (Highest Priority)
        thumbs_down = thumb_tip.y > thumb_mcp.y and index_tip.y < thumb_mcp.y
        if thumbs_down:
            if self.disconnect_start_time is None:
                self.disconnect_start_time = time.time()
            elif time.time() - self.disconnect_start_time > self.DISCONNECT_HOLD_TIME:
                return -1, "DISCONNECT"
        else:
            self.disconnect_start_time = None

        # 2. SCROLL CHECK (Zone Locking)
        # Fix: Check Scroll BEFORE Pinch. If in scroll zone, ignoring pinching.
        if wrist.y < self.SCROLL_TOP_ZONE:
            return -1, "SCROLL_UP"
        elif wrist.y > self.SCROLL_BOTTOM_ZONE:
            return -1, "SCROLL_DOWN"

        # 3. PINCH (Select)
        # Only reachable if hand is in the "Neutral Center Zone"
        if self.get_dist(thumb_tip, index_tip) < self.PINCH_THRESHOLD:
            if not self.is_pinching:
                self.is_pinching = True
                return -1, "SELECT"
            return -1, None
        self.is_pinching = False

        # 4. DIGITS
        # Only reachable if hand is in Neutral Zone and NOT pinching
        fingers = []
        thumb_open = self.get_dist(thumb_tip, pinky_base) > self.get_dist(thumb_ip, pinky_base)

        for tip in [8, 12, 16, 20]:
            fingers.append(1 if lm[tip].y < lm[tip - 2].y else 0)

        count = fingers.count(1)

        if thumb_open:
            # 1-5 European/Thumb logic
            return {0: 6, 1: 7, 2: 8, 3: 9, 4: 5}.get(count, -1), None
        else:
            # 1-4 Standard logic + 0 for Fist
            return {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}.get(count, -1), None

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return

        cap.set(3, 640)
        cap.set(4, 480)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            digit, action = -1, None

            if time.time() - self.last_trigger_time < self.COOLDOWN_SECONDS:
                cv2.imshow("Gesture Debug", frame)
                cv2.waitKey(1)
                continue

            if results.multi_hand_landmarks:
                lm = results.multi_hand_landmarks[0]
                self.mp_draw.draw_landmarks(frame, lm, self.mp_hands.HAND_CONNECTIONS)
                digit, action = self.process_hand(lm.landmark)

            triggered = False

            if action == "DISCONNECT":
                self.disconnect_detected.emit()
                triggered = True

            elif action == "SELECT":
                self.select_detected.emit()
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
                    self.gesture_detected.emit(str(digit))
                    triggered = True

            if triggered:
                self.last_trigger_time = time.time()
                self.stable_frame_count = 0

            cv2.imshow("Gesture Debug", frame)
            cv2.waitKey(1)

        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False
        self.wait()
