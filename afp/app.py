import numpy as np
import sys
import os
from pathlib import Path

# Add the current directory to Python path to ensure imports work
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QDoubleSpinBox, QGroupBox, QGridLayout,
                             QPushButton, QCheckBox, QSpinBox, QFrame, QToolBar, QAction, QStatusBar, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from commands import Controller
from RsInstrument import RsInstrument
from MainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(Controller(RsInstrument('USB0::0x0AAD::0x0048::101548::INSTR', True, True, options='TerminationCharacter = \r\n, Simulate=True'), ni_daq_device="Dev1/ao0"))
    sys.exit(app.exec())
    