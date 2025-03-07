"""
Migracion del codigo del enlace siguiente a PyQt6
https://medium.com/@ilias.info.tel/display-opencv-camera-on-a-pyqt-app-4465398546f7

"""
from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QLabel, QVBoxLayout, QPushButton, QApplication
from PyQt6.QtGui import QImage, QPixmap
import sys, cv2, imutils, subprocess, re


class CameraThread(QThread):
    frame_signal = Signal(int, QImage)

    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index*2)

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = self.cvimage_to_label(frame)
            self.frame_signal.emit(self.camera_index, frame)

    def cvimage_to_label(self, image):
        image = imutils.resize(image, width=640)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_RGB888)
        return image

class WebCamLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedSize(640, 480)
        self.setScaledContents(True)
        self.setStyleSheet("border: 1px solid black;")


class MainApp(QWidget):

    def __init__(self):
        self.cameras = getUsbCameras()
        self.camera_threads = []
        self.labels = []
        super().__init__()
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setFixedSize(800, 640)
        self.setWindowTitle("WebCam Center")


        open_btn = QPushButton("Open The Camera")
        open_btn.clicked.connect(self.open_camera)

        vbox = QVBoxLayout()
        vbox.addWidget(open_btn)
        hbox = QHBoxLayout()

        for i, cam in enumerate(self.cameras):
            #x labels para x camaras
            label = WebCamLabel()
            self.labels.append(label)
            hbox.addWidget(label)

            #x threads para x camaras
            thread = CameraThread(i)
            thread.frame_signal.connect(self.setImage)
            self.camera_threads.append(thread)

        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def open_camera(self):
        for thread in self.camera_threads:
            thread.start()
            print(thread.isRunning())

    @Slot(int, QImage)
    def setImage(self, index, image):
        if 0 <= index < len(self.labels):
            self.labels[index].setPixmap(QPixmap.fromImage(image))

def getUsbCameras():
    device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    cameras = []

    for i in df.split(b'\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)

    for device in devices:
        tag = device.get('tag').decode('utf-8').lower()
        if 'camera' in tag or 'webcam' in tag or 'video' in tag:
            cameras.append(device)

    print(cameras)
    return list(range(len(cameras)))

if __name__ == "__main__":
    app = QApplication([])
    main_window = MainApp()
    sys.exit(app.exec())