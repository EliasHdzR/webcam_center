from PyQt6.QtWidgets import QLabel

class WebCamLabel(QLabel):
    """
    Clase que representa un QLabel para mostrar la imagen de una cámara.
    """

    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 430)
        self.setScaledContents(True)
        self.setStyleSheet("border: 1px solid black;")