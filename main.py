import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLabel, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from gesture_thread import GestureThread

class ModernContactUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IVI Gesture Contact List")
        self.setGeometry(100, 100, 1024, 600)
        
        # --- DATA ---
        self.all_contacts = [
            "Aaron Smith", "Adam Driver", "Ben Affleck", "Brian O'Conner", 
            "Charlie Puth", "Chris Evans", "Daniel Craig", "David Beckham", 
            "Electrifex Support", "Elon Musk", "Frank Ocean", "George Clooney",
            "Harry Styles", "Henry Cavill", "Ian Somerhalder", "Jack Sparrow", 
            "Jason Statham", "Kevin Hart", "Liam Neeson", "Luke Skywalker",
            "Zendaya", "Zac Efron"
        ]
        
        self.input_buffer = "" 
        
        self.init_ui()
        
        # --- DEFINE STYLES ---
        # We define the COMPLETE style for both states so nothing gets lost
        self.style_normal = self.get_style_string(bg_color="#121212")
        self.style_disconnected = self.get_style_string(bg_color="#440000") # Dark Red
        
        self.setStyleSheet(self.style_normal)

        # --- GESTURE THREAD ---
        self.thread = GestureThread()
        self.thread.gesture_detected.connect(self.handle_digit_input)
        self.thread.scroll_detected.connect(self.handle_scroll)
        self.thread.select_detected.connect(self.handle_selection)
        self.thread.disconnect_detected.connect(self.handle_disconnect)
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- LEFT PANEL ---
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 30, 20, 30)

        self.header_label = QLabel("CONTACTS")
        self.header_label.setObjectName("HeaderLabel")
        left_layout.addWidget(self.header_label)

        self.search_display = QLabel("Input: _") 
        self.search_display.setObjectName("SearchDisplay")
        left_layout.addWidget(self.search_display)

        self.contact_list = QListWidget()
        self.contact_list.addItems(self.all_contacts)
        self.contact_list.setObjectName("ContactList")
        left_layout.addWidget(self.contact_list)

        # --- RIGHT PANEL (Restored Keypad) ---
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        
        guide_label = QLabel("GESTURE MAP")
        guide_label.setAlignment(Qt.AlignCenter)
        guide_label.setObjectName("GuideTitle")
        right_layout.addWidget(guide_label)

        # The Grid
        grid_container = QWidget()
        keypad_grid = QGridLayout(grid_container)
        keypad_grid.setSpacing(10)

        # Create Buttons 1-9
        row, col = 0, 0
        for key in range(1, 10):
            self.create_key_frame(keypad_grid, str(key), row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Add 0 Button at the bottom
        self.create_key_frame(keypad_grid, "0", row, 1)

        right_layout.addWidget(grid_container)

        # Helper Text
        helper = QLabel("0+1 = A   |   0+2 = B\n...\n2+6 = Z")
        helper.setAlignment(Qt.AlignCenter)
        helper.setStyleSheet("color: #888; font-size: 16px; margin-top: 10px;")
        right_layout.addWidget(helper)
        
        main_layout.addWidget(left_panel, 60)
        main_layout.addWidget(right_panel, 40)

    def create_key_frame(self, grid, text, r, c):
        """Helper to create the visual keys"""
        frame = QFrame()
        frame.setObjectName("KeyFrame")
        layout = QVBoxLayout(frame)
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: white; font-size: 24px; font-weight: bold; border: none;")
        layout.addWidget(lbl)
        grid.addWidget(frame, r, c)

    def get_style_string(self, bg_color):
        """Returns the full CSS string with a custom background color"""
        return f"""
            QMainWindow {{ background-color: {bg_color}; }}
            #LeftPanel {{ background-color: #1E1E1E; border-right: 2px solid #333; }}
            #RightPanel {{ background-color: {bg_color}; }}
            #HeaderLabel {{ color: #FFFFFF; font-size: 24px; font-weight: bold; }}
            #SearchDisplay {{ color: #00E5FF; font-size: 24px; background-color: #2C2C2C; padding: 10px; border-radius: 8px; }}
            
            #ContactList {{ background-color: transparent; border: none; color: #DDDDDD; font-size: 20px; }}
            #ContactList::item {{ padding: 15px; border-bottom: 1px solid #333; }}
            #ContactList::item:selected {{ background-color: #00E5FF; color: #000000; border-radius: 5px; }}
            
            #GuideTitle {{ color: #888; font-size: 20px; font-weight: bold; margin-bottom: 20px; }}
            
            #KeyFrame {{ 
                background-color: #252525; 
                border: 2px solid #333; 
                border-radius: 10px; 
                min-width: 60px; 
                min-height: 60px; 
            }}
        """

    # --- LOGIC ---
    def handle_digit_input(self, digit_str):
        self.input_buffer += digit_str
        self.search_display.setText(f"Input: {self.input_buffer}")
        
        if len(self.input_buffer) >= 2:
            try:
                val = int(self.input_buffer)
                if 1 <= val <= 26:
                    char = chr(val + 64) 
                    self.filter_list_by_char(char)
                else:
                    self.search_display.setText("Invalid (01-26)")
            except:
                pass
            self.input_buffer = ""

    def filter_list_by_char(self, char):
        self.search_display.setText(f"Filtering: {char}")
        filtered = [c for c in self.all_contacts if c.upper().startswith(char)]
        self.contact_list.clear()
        if filtered:
            self.contact_list.addItems(filtered)
            self.contact_list.setCurrentRow(0)
        else:
            self.contact_list.addItem("No Contact Found")

    def handle_scroll(self, direction):
        count = self.contact_list.count()
        if count == 0: return
        current_row = self.contact_list.currentRow()
        if current_row == -1: current_row = 0

        if direction == "DOWN":
            new_row = min(count - 1, current_row + 1)
        elif direction == "UP":
            new_row = max(0, current_row - 1)
        else:
            return
        self.contact_list.setCurrentRow(new_row)
        self.contact_list.scrollToItem(self.contact_list.currentItem())

    def handle_selection(self):
        current_item = self.contact_list.currentItem()
        if current_item:
            contact_name = current_item.text()
            self.search_display.setText(f"Calling: {contact_name}...")
            # Local style update for selection (Green)
            self.contact_list.setStyleSheet("#ContactList::item:selected { background-color: #00FF00; color: black; }")
            QTimer.singleShot(1000, lambda: self.setStyleSheet(self.style_normal))

    def handle_disconnect(self):
        # Reset Logic
        self.input_buffer = ""
        self.contact_list.clear()
        self.contact_list.addItems(self.all_contacts)
        self.header_label.setText("MAIN MENU")
        self.search_display.setText("Disconnected")
        
        # Apply the RED Theme (keeps layout intact)
        self.setStyleSheet(self.style_disconnected) 
        
        # Restore the NORMAL Theme after 1.5 seconds
        def restore():
            self.header_label.setText("CONTACTS")
            self.search_display.setText("Input: _")
            self.setStyleSheet(self.style_normal)
            
        QTimer.singleShot(1500, restore)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernContactUI()
    window.show()
    sys.exit(app.exec_())