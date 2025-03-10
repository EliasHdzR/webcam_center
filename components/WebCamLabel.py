from PyQt6.QtWidgets import QLabel

class WebCamLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 450)
        self.setScaledContents(True)
        self.setStyleSheet("border: 1px solid black;")