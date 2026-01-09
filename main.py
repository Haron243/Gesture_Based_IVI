import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLabel, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor
from gesture_thread import GestureThread

class ModernContactUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IVI Gesture Contact List")
        self.setGeometry(100, 100, 1024, 600) # Standard Car Display Ratio
        
        # --- DATA & MAPPING ---
        # Standard T9 Mapping as requested by "T9-like" requirement 
        self.t9_map = {
            1: ".,!", 2: "ABC", 3: "DEF", 
            4: "GHI", 5: "JKL", 6: "MNO", 
            7: "PQRS", 8: "TUV", 9: "WXYZ", 0: " "
        }
        
        # Mock Contacts Data
        self.all_contacts = [
            "Aaron Smith", "Adam Driver", "Ben Affleck", "Brian O'Conner", 
            "Charlie Puth", "Chris Evans", "Daniel Craig", "David Beckham", 
            "Electrifex Support", "Elon Musk", "Frank Ocean", "George Clooney",
            "Harry Styles", "Henry Cavill", "Ian Somerhalder", "Jack Sparrow", 
            "Jason Statham", "Kevin Hart", "Liam Neeson", "Luke Skywalker"
        ]
        
        # State
        self.current_filter = ""
        
        # --- UI SETUP ---
        self.init_ui()
        self.apply_styles()
        # --- START GESTURE ENGINE ---
        self.thread = GestureThread()
        
        # 1. Connect Digit Logic (Existing)
        self.thread.gesture_detected.connect(self.update_filter)
        
        # 2. Connect Scroll Logic (NEW)
        self.thread.scroll_detected.connect(self.handle_scroll)
        
        # 3. Connect Selection Logic (NEW)
        self.thread.select_detected.connect(self.handle_selection)

        # --- NEW CONNECTION ---
        self.thread.disconnect_detected.connect(self.handle_disconnect)
        
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def init_ui(self):
        # Main Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- LEFT PANEL: Contact List ---
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 30, 20, 30)

        # Header / Search Status
        self.header_label = QLabel("CONTACTS")
        self.header_label.setObjectName("HeaderLabel")
        left_layout.addWidget(self.header_label)

        # The "Search Bar" visualizing the gesture input
        self.search_display = QLabel("Input: _") 
        self.search_display.setObjectName("SearchDisplay")
        left_layout.addWidget(self.search_display)

        # The Scrollable List
        self.contact_list = QListWidget()
        self.contact_list.addItems(self.all_contacts)
        self.contact_list.setObjectName("ContactList")
        left_layout.addWidget(self.contact_list)

        # --- RIGHT PANEL: Gesture Guide (T9 Keypad) ---
        # This helps the driver know which number to gesture [cite: 31]
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        
        guide_label = QLabel("GESTURE GUIDE")
        guide_label.setAlignment(Qt.AlignCenter)
        guide_label.setObjectName("GuideTitle")
        right_layout.addWidget(guide_label)

        # Grid for Keys
        grid_container = QWidget()
        keypad_grid = QGridLayout(grid_container)
        keypad_grid.setSpacing(15)

        # Generate Keypad Buttons (Visual Only)
        row, col = 0, 0
        for key in range(1, 10):
            letters = self.t9_map[key]
            
            # Create a "Key" Frame
            key_frame = QFrame()
            key_frame.setObjectName("KeyFrame")
            k_layout = QVBoxLayout(key_frame)
            
            num_lbl = QLabel(str(key))
            num_lbl.setObjectName("KeyNum")
            num_lbl.setAlignment(Qt.AlignCenter)
            
            char_lbl = QLabel(letters)
            char_lbl.setObjectName("KeyChars")
            char_lbl.setAlignment(Qt.AlignCenter)
            
            k_layout.addWidget(num_lbl)
            k_layout.addWidget(char_lbl)
            
            keypad_grid.addWidget(key_frame, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1

        right_layout.addWidget(grid_container)
        
        # Add panels to main layout (60% List, 40% Keypad)
        main_layout.addWidget(left_panel, 60)
        main_layout.addWidget(right_panel, 40)

    def apply_styles(self):
        # Modern Automotive CSS
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212; 
            }
            #LeftPanel {
                background-color: #1E1E1E;
                border-right: 2px solid #333;
            }
            #RightPanel {
                background-color: #121212;
            }
            #HeaderLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 2px;
                margin-bottom: 10px;
            }
            #SearchDisplay {
                color: #00E5FF; /* Cyan Accent */
                font-size: 18px;
                background-color: #2C2C2C;
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            #ContactList {
                background-color: transparent;
                border: none;
                color: #DDDDDD;
                font-size: 20px;
            }
            #ContactList::item {
                padding: 15px;
                border-bottom: 1px solid #333;
            }
            #ContactList::item:selected {
                background-color: #00E5FF;
                color: #000000;
                border-radius: 5px;
            }
            /* Keypad Styles */
            #GuideTitle {
                color: #888;
                font-size: 14px;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            #KeyFrame {
                background-color: #252525;
                border: 2px solid #333;
                border-radius: 10px;
                min-width: 80px;
                min-height: 80px;
            }
            #KeyNum {
                color: #FFF;
                font-size: 28px;
                font-weight: bold;
            }
            #KeyChars {
                color: #888;
                font-size: 12px;
                font-weight: bold;
            }
        """)

    # --- SIMULATION LOGIC (To be connected to Gesture Engine) ---
    def update_filter(self, digit_sequence):
        """
        Receives a string of digits (e.g., '552') and filters the list.
        This fulfills the 'Interpretation' milestone.
        """
        self.search_display.setText(f"Input: {digit_sequence}")
        
        # Logic: Simple filtering for demo (Expandable to real T9 logic)
        # Here we just show contacts that match the first letter of the T9 mapping
        if not digit_sequence:
            self.contact_list.clear()
            self.contact_list.addItems(self.all_contacts)
            return

        first_digit = int(digit_sequence[0])
        possible_chars = self.t9_map.get(first_digit, "")
        
        filtered = [c for c in self.all_contacts if c[0].upper() in possible_chars]
        
        self.contact_list.clear()
        self.contact_list.addItems(filtered)
        
        # Highlight the first result ("Highlighting of indexed letters" [cite: 29])
        if self.contact_list.count() > 0:
            self.contact_list.setCurrentRow(0)

    # --- NEW: SCROLLING HANDLER ---
    def handle_scroll(self, direction):
        """
        Moves the list selection up or down based on finger motion.
        """
        current_row = self.contact_list.currentRow()
        count = self.contact_list.count()
        
        if direction == "DOWN":
            new_row = min(current_row + 1, count - 1)
        elif direction == "UP":
            new_row = max(current_row - 1, 0)
        else:
            return
            
        self.contact_list.setCurrentRow(new_row)
        # Ensure the selected item is visible (auto-scroll)
        self.contact_list.scrollToItem(self.contact_list.currentItem())

    # --- NEW: SELECTION HANDLER ---
    def handle_selection(self):
        """
        Triggered by Pinch. Simulates clicking the selected contact.
        """
        current_item = self.contact_list.currentItem()
        if current_item:
            contact_name = current_item.text()
            self.search_display.setText(f"Calling: {contact_name}...")
            # Visual feedback: Turn green briefly or flash
            self.contact_list.setStyleSheet("#ContactList::item:selected { background-color: #00FF00; color: black; }")
            
            # Reset style after 1 second
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self.apply_styles())

    def handle_disconnect(self):
        # 1. Clear Data
        self.current_filter = ""
        self.search_display.setText("Input: _")
        
        # 2. Reset List
        self.contact_list.clear()
        self.contact_list.addItems(self.all_contacts)
        self.contact_list.scrollToTop()
        
        # 3. Visual Feedback
        print("UI: Switching to Main Menu")
        self.header_label.setText("MAIN MENU")
        self.search_display.setText("Call Disconnected")
        
        # Flash Red
        self.setStyleSheet("QMainWindow { background-color: #440000; }") 
        
        from PyQt5.QtCore import QTimer
        def restore():
            self.header_label.setText("CONTACTS")
            self.search_display.setText("Input: _")
            # Restore original dark theme
            self.setStyleSheet("""
                QMainWindow { background-color: #121212; }
                #LeftPanel { background-color: #1E1E1E; border-right: 2px solid #333; }
                #RightPanel { background-color: #121212; }
                /* ... rest of your styles ... */
            """)
            # Note: For cleaner code, put your full stylesheet in a self.style_string variable
            # and re-apply it here: self.setStyleSheet(self.style_string)
            
        QTimer.singleShot(1500, restore)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernContactUI()
    window.show()
    
    # Simulate the "Electrifex" Example [cite: 26, 27]
    # Simulate user gesturing '3' (D,E,F) after 2 seconds
    from PyQt5.QtCore import QTimer
    QTimer.singleShot(2000, lambda: window.update_filter("3")) 
    
    sys.exit(app.exec_())