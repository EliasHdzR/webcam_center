"""
Migracion del codigo del enlace siguiente a PyQt6
https://medium.com/@ilias.info.tel/display-opencv-camera-on-a-pyqt-app-4465398546f7

"""

from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtWidgets import QGridLayout, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QImage, QPixmap
import subprocess, re, glob
from CameraThread import CameraThread
from components.WebCamLabel import WebCamLabel

class MainApp(QWidget):
    """
    Clase que representa la ventana principal de la aplicación.
    """

    def __init__(self):
        super().__init__()
        self.cameras = self.getUsbCameras()
        print(self.cameras)
        self.camera_threads = []
        self.labels = []
        self.buttons = []
        self.init_ui()
        self.show()
        self.setWindowTitle("WebCam Center")

    def init_ui(self):
        # se maneja un grid de 2x2
        grid = QGridLayout()
        self.setLayout(grid)

        row = 0
        col = 0

        # se crea un botón, un WebCamLabel y un hilo para cada cámara
        for i, cam in enumerate(self.cameras):
            button = QPushButton(f"Abrir Cámara {i + 1}")
            button.clicked.connect(lambda state, x=i: self.btnEvent(x))
            self.buttons.append(button)

            vbox = QVBoxLayout()
            vbox.addWidget(button)

            label = WebCamLabel()
            self.labels.append(label)
            vbox.addWidget(label)

            grid.addLayout(vbox, row, col)

            thread = CameraThread(i, cam)
            thread.frame_signal.connect(self.setImage)
            self.camera_threads.append(thread)

            # aquí se modifica la posición en el grid
            col += 1
            if col > 1:
                col = 0
                row += 1

    def btnEvent(self, index):
        """
        Función que maneja el evento de presionar un botón para abrir o cerrar una cámara.
        :param index: Índice de la cámara a abrir o cerrar.
        :return:
        """

        button = self.buttons[index]
        if button.text() == f"Abrir Cámara {index + 1}":
            self.openCamera(index, button)
        else:
            self.closeCamera(index, button)

    def openCamera(self, index, button):
        """
        Función que abre una cámara y comienza a capturar video.
        :param index: Índice de la cámara a abrir.
        :param button: Botón que se presionó para abrir la cámara.
        :return:
        """

        thread = self.camera_threads[index]
        thread.start()
        button.setText(f"Cerrar Cámara {index + 1}")

    def closeCamera(self, index, button):
        """
        Función que cierra una cámara y deja de capturar video.
        :param index: Índice de la cámara a cerrar.
        :param button: Botón que se presionó para cerrar la cámara.
        :return:
        """

        thread = self.camera_threads[index]
        thread.stop()
        button.setText(f"Abrir Cámara {index + 1}")

    @Slot(int, QImage)
    def setImage(self, index, image):
        """
        Función que recibe una imagen de un hilo y la muestra en un WebCamLabel.
        :param index: Índice del WebCamLabel en el que se mostrará la imagen.
        :param image: Imagen a mostrar.
        :return:
        """

        if 0 <= index < len(self.labels):
            self.labels[index].setPixmap(QPixmap.fromImage(image))

    @staticmethod
    def getUsbCameras():
        """Lista los dispositivos de video disponibles en /dev/videoX"""
        usb_cameras = sorted(glob.glob('/dev/video*'))
        print(usb_cameras)
        usb_cameras = [cam for cam in usb_cameras if int(cam.replace('/dev/video', '')) % 2 == 0]
        return usb_cameras