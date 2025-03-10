from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QImage
import cv2, imutils

class CameraThread(QThread):
    """
    Clase que representa un hilo para capturar video de una cámara.
    """

    frame_signal = Signal(int, QImage)

    def __init__(self, camera_index):
        """
        Constructor de la clase.
        :param camera_index: Entero que representa el índice de la cámara a capturar.
        """

        super().__init__()
        self.camera_index = camera_index
        self.cap = None
        self.running = False

    def run(self):
        """
        Funcion que se ejecuta al iniciar el hilo con start. Captura la imagen de la cámara y la envía a la señal
        frame_signal. Si se cierra la cámara o el hilo, se envía una imagen vacía hasta que se vuelva a abrir la cámara.
        """

        self.cap = cv2.VideoCapture(self.camera_index * 2)
        self.running = True

        while self.cap.isOpened() and self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = self.cvimage_to_label(frame)
            self.frame_signal.emit(self.camera_index, frame)

        empty_image = QImage(600, 480, QImage.Format.Format_RGB888)
        empty_image.fill(0)
        self.frame_signal.emit(self.camera_index, empty_image)

        if self.cap is not None:
            self.cap.release()

    def stop(self):
        """
        Función que detiene la captura de video de la cámara.
        :return:
        """
        self.running = False
        if self.cap is not None:
            self.cap.release()


    def cvimage_to_label(self, image):
        """
        Función que convierte una imagen de OpenCV a QImage.
        :param image: CV2Image a convertir.
        :return: QImage convertida.
        """
        image = imutils.resize(image, width=600)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_RGB888)
        return image