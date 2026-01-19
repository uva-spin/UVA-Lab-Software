from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QDoubleSpinBox, QGroupBox, QGridLayout,
                             QPushButton, QCheckBox, QSpinBox, QFrame, QToolBar, QAction, QStatusBar, QLineEdit,
                             QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont
class ConfigurationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurations")
        self.setWindowIcon(QIcon('./assets/program.png'))
        self.setGeometry(100, 100, 800, 600)
        self.centralwidget = QWidget()
        self.centralwidget.setLayout(QVBoxLayout())
        self.setCentralWidget(self.centralwidget)
        self.show()