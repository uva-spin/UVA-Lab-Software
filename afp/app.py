import numpy as np
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QDoubleSpinBox, QGroupBox, QGridLayout,
                             QPushButton, QCheckBox, QSpinBox, QFrame, QToolBar, QAction, QStatusBar, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from commands import Controller
from RsInstrument import RsInstrument


class MainWindow(QMainWindow):
    def __init__(self, controller: Controller):
        super().__init__()
        self.setWindowTitle("ssRF/AFP Control Panel")
        self.setWindowIcon(QIcon('./assets/program.png'))      
        self.setGeometry(100, 100, 800, 600)
        self.controller = controller
        
        ### menu bar

        file_menu = self.menuBar().addMenu("&File")
        edit_menu = self.menuBar().addMenu("&Edit")
        help_menu = self.menuBar().addMenu("&Help")

        file_menu.addAction("Open", lambda: print("Open"))

        undo_action = QAction(QIcon('./assets/undo.jpg'), "Undo", self)
        redo_action = QAction(QIcon('./assets/redo.png'), "Redo", self)
        undo_action.setShortcut("Ctrl+Z")

        redo_action.setShortcut("Ctrl+Y")
        undo_action.triggered.connect(lambda: print("Undo"))
        redo_action.triggered.connect(lambda: print("Redo"))

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        ### toolbar, below menu bar

        toolbar = QToolBar("Toolbar")
        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)
        self.addToolBar(toolbar)

        ### status bar at bottom

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

        ### main content area
        self.setup_ui()
        
        ### timer to update values periodically
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display_values)
        self.update_timer.start(1000)  # Update every second
        
        # Initial update
        self.update_display_values()
        
        self.show()

    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Top layout for RF Status (right corner)
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # Push RF Status to the right

        # Turn on/off RF button
        self.turn_on_off_rf_button = QPushButton("Turn On RF")
        self.turn_on_off_rf_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        self.turn_on_off_rf_button.clicked.connect(lambda: self.controller.activate_rf())
        top_layout.addWidget(self.turn_on_off_rf_button)
        
        # RF Status indicator
        self.rf_status = 'OFF'
        self.rf_status_label = QLabel(f"RF Status: {self.rf_status}")
        self.rf_status_label.setAlignment(Qt.AlignCenter)
        self.rf_status_label.setStyleSheet("""
            QLabel {
                background-color: red;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                min-width: 100px;
            }
        """)
        top_layout.addWidget(self.rf_status_label)
        main_layout.addLayout(top_layout)
        
        # Control parameters group
        control_group = QGroupBox("Controller Parameters")
        control_layout = QGridLayout()
        control_group.setLayout(control_layout)
        
        # Create input fields for each parameter
        row = 0
        
        # Start Frequency
        control_layout.addWidget(QLabel("Start Frequency (MHz):"), row, 0)
        self.start_freq_input = QDoubleSpinBox()
        self.start_freq_input.setRange(0, 10000)
        self.start_freq_input.setDecimals(3)
        self.start_freq_input.editingFinished.connect(lambda: self.update_parameter('start_freq', self.start_freq_input.value()))
        control_layout.addWidget(self.start_freq_input, row, 1)
        row += 1
        
        # Stop Frequency
        control_layout.addWidget(QLabel("Stop Frequency (MHz):"), row, 0)
        self.stop_freq_input = QDoubleSpinBox()
        self.stop_freq_input.setRange(0, 10000)
        self.stop_freq_input.setDecimals(3)
        self.stop_freq_input.editingFinished.connect(lambda: self.update_parameter('stop_freq', self.stop_freq_input.value()))
        control_layout.addWidget(self.stop_freq_input, row, 1)
        row += 1
        
        # Spacing
        control_layout.addWidget(QLabel("Spacing:"), row, 0)
        self.spacing_input = QLineEdit()
        self.spacing_input.returnPressed.connect(lambda: self.update_parameter('spacing', self.spacing_input.text()))
        control_layout.addWidget(self.spacing_input, row, 1)
        row += 1
        
        # Power
        control_layout.addWidget(QLabel("Power (dBm):"), row, 0)
        self.power_input = QDoubleSpinBox()
        self.power_input.setRange(-100, 100)
        self.power_input.setDecimals(1)
        self.power_input.editingFinished.connect(lambda: self.update_parameter('power', self.power_input.value()))
        control_layout.addWidget(self.power_input, row, 1)
        row += 1
        
        # Mode
        control_layout.addWidget(QLabel("Mode:"), row, 0)
        self.mode_input = QLineEdit()
        self.mode_input.returnPressed.connect(lambda: self.update_parameter('mode', self.mode_input.text()))
        control_layout.addWidget(self.mode_input, row, 1)
        row += 1
        
        # Sweep Points
        control_layout.addWidget(QLabel("Sweep Points:"), row, 0)
        self.sweep_points_input = QSpinBox()
        self.sweep_points_input.setRange(1, 100000)
        self.sweep_points_input.editingFinished.connect(lambda: self.update_parameter('sweep_points', self.sweep_points_input.value()))
        control_layout.addWidget(self.sweep_points_input, row, 1)
        row += 1
        
        # Sweep Dwell
        control_layout.addWidget(QLabel("Sweep Dwell (ms):"), row, 0)
        self.sweep_dwell_input = QDoubleSpinBox()
        self.sweep_dwell_input.setRange(0, 1000000)
        self.sweep_dwell_input.setDecimals(3)
        self.sweep_dwell_input.editingFinished.connect(lambda: self.update_parameter('sweep_dwell', self.sweep_dwell_input.value()))
        control_layout.addWidget(self.sweep_dwell_input, row, 1)
        row += 1
        
        main_layout.addWidget(control_group)
        main_layout.addStretch()

    def update_parameter(self, param_name, value):
        """Update a parameter in the controller when user presses Enter or finishes editing"""
        try:
            if param_name == 'start_freq':
                self.controller.set_start_freq(value)
            elif param_name == 'stop_freq':
                self.controller.set_stop_freq(value)
            elif param_name == 'spacing':
                self.controller.set_spacing(value)
            elif param_name == 'power':
                self.controller.set_power(value)
            elif param_name == 'mode':
                self.controller.set_mode(value)
            elif param_name == 'sweep_points':
                self.controller.set_sweep_points(int(value))
            elif param_name == 'sweep_dwell':
                self.controller.set_sweep_dwell(value)
            
            self.statusBar().showMessage(f"Updated {param_name} to {value}", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"Error updating {param_name}: {str(e)}", 3000)

    def update_display_values(self):
        """Update all displayed values from the controller"""
        try:
            # Update RF Status
            rf_status = self.controller.get_rf_status()
            if rf_status:
                self.rf_status = 'ON'
                self.rf_status_label.setText(f"RF Status: {self.rf_status}")
                self.rf_status_label.setStyleSheet("""
                    QLabel {
                        background-color: green;
                        color: white;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 5px;
                        min-width: 100px;
                    }
                """)
                self.turn_on_off_rf_button.setText("Turn Off RF")
            else:
                self.rf_status = 'OFF'
                self.rf_status_label.setText(f"RF Status: {self.rf_status}")
                self.rf_status_label.setStyleSheet("""
                    QLabel {
                        background-color: red;
                        color: white;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 5px;
                        min-width: 100px;
                    }
                """)
                self.turn_on_off_rf_button.setText("Turn On RF")
            # Update all parameter displays (only if not currently being edited)
            if not self.start_freq_input.hasFocus():
                start_freq = self.controller.get_start_freq()
                self.start_freq_input.setValue(start_freq)
            
            if not self.stop_freq_input.hasFocus():
                stop_freq = self.controller.get_stop_freq()
                self.stop_freq_input.setValue(stop_freq)
            
            if not self.spacing_input.hasFocus():
                spacing = self.controller.get_sweep_spacing()
                self.spacing_input.setText(spacing)
            
            if not self.power_input.hasFocus():
                power = self.controller.get_power()
                self.power_input.setValue(power)
            
            if not self.mode_input.hasFocus():
                mode = self.controller.get_mode()
                self.mode_input.setText(mode)
            
            if not self.sweep_points_input.hasFocus():
                sweep_points = self.controller.get_sweep_points()
                self.sweep_points_input.setValue(sweep_points)
            
            if not self.sweep_dwell_input.hasFocus():
                sweep_dwell = self.controller.get_sweep_dwell()
                self.sweep_dwell_input.setValue(sweep_dwell)
                
        except Exception as e:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(Controller(RsInstrument('USB0::0x0AAD::0x0048::101548::INSTR', True, True, options='TerminationCharacter = \r\n, Simulate=True')))
    sys.exit(app.exec())
    