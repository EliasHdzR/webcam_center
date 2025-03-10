"""
Migracion del codigo del enlace siguiente a PyQt6
https://medium.com/@ilias.info.tel/display-opencv-camera-on-a-pyqt-app-4465398546f7

"""

from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtWidgets import QGridLayout, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QImage, QPixmap
import subprocess, re
from CameraThread import CameraThread
from components.WebCamLabel import WebCamLabel

class MainApp(QWidget):
    """
    Clase que representa la ventana principal de la aplicación.
    """

    def __init__(self):
        super().__init__()
        self.cameras = self.getUsbCameras()
        self.camera_threads = []
        self.labels = []
        self.buttons = []
        self.init_ui()
        self.show()

    def init_ui(self):
        self.showMaximized()
        self.setWindowTitle("WebCam Center")

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

            thread = CameraThread(i)
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
        """
        Función que obtiene las cámaras conectadas a través de USB. Checa los dispositivos conectados a través de lsusb
        y que contengan las palabras 'camera', 'webcam' o 'video' en su nombre.
        :return:
        """

        device_re = re.compile(
            b"Bus\\s+(?P<bus>\\d+)\\s+Device\\s+(?P<device>\\d+).+ID\\s(?P<id>\\w+:\\w+)\\s(?P<tag>.+)$", re.I
        )
        df = subprocess.check_output("lsusb")
        devices, cameras = [], []

        for i in df.split(b'\n'):
            if i:
                info = device_re.match(i)
                if info:
                    dinfo = info.groupdict()
                    dinfo['device'] = f"/dev/bus/usb/{dinfo.pop('bus')}/{dinfo.pop('device')}"
                    devices.append(dinfo)

        for device in devices:
            tag = device.get('tag').decode('utf-8').lower()
            if 'camera' in tag or 'webcam' in tag or 'video' in tag:
                cameras.append(device)

        print(cameras)
        return list(range(len(cameras)))