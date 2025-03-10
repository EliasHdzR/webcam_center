import sys
from PyQt6.QtWidgets import QApplication
from UI import MainApp

if __name__ == "__main__":
    app = QApplication([])
    main_window = MainApp()
    sys.exit(app.exec())