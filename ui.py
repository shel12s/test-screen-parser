import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QEvent
from PyQt6.QtGui import QFont, QColor, QPalette

class OverlayController(QObject):
    update_text_signal = pyqtSignal(str)

class OverlayWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.controller.update_text_signal.connect(self.update_text)
        
        # Initial flags (hidden initially, no AlwaysOnTop yet)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.layout = QVBoxLayout()
        self.label = QLabel("")
        self.label.setFont(QFont("Arial", 6, QFont.Weight.Bold)) 
        self.label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 200); padding: 4px; border-radius: 3px;")
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.resize(200, 50)
        self.position_bottom_right()
        # Do not show initially

    def position_bottom_right(self):
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        x = geometry.width() - self.width() - 20
        y = geometry.height() - self.height() - 20
        self.move(x, y)

    def update_text(self, text):
        self.label.setText(text)
        self.label.adjustSize()
        self.adjustSize()
        self.position_bottom_right()
        
        # Force window to top and show
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.show()
        self.raise_()
        self.activateWindow()

    def event(self, event):
        # If window loses focus (user clicked elsewhere), remove AlwaysOnTop
        if event.type() == QEvent.Type.WindowDeactivate:
            # Remove the TopMost flag so other windows can cover it
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show() # Re-apply flags
        return super().event(event)

def run_overlay(controller):
    app = QApplication(sys.argv)
    window = OverlayWindow(controller)
    # window.show() # Don't show initially
    sys.exit(app.exec())
