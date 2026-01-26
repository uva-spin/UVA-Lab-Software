"""
Sequence Window for batch configuration execution
Allows loading JSON files with sequences of configurations to iterate through
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,
                             QMessageBox, QTextEdit, QTabWidget, QHeaderView, QProgressBar,
                             QGroupBox, QGridLayout, QDoubleSpinBox, QSpinBox, QComboBox,
                             QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from commands import Controller
import json
import time

# Color scheme constants (matching MainWindow)
COLORS = {
    'primary': '#3498db',
    'primary_dark': '#2980b9',
    'primary_light': '#5dade2',
    'success': '#27ae60',
    'success_dark': '#1e8449',
    'danger': '#e74c3c',
    'danger_dark': '#c0392b',
    'warning': '#f39c12',
    'dark': '#2c3e50',
    'dark_light': '#34495e',
    'gray': '#7f8c8d',
    'gray_light': '#bdc3c7',
    'gray_lighter': '#ecf0f1',
    'background': '#f5f7fa',
    'card': '#ffffff',
    'border': '#e1e8ed',
}


class SequenceExecutionThread(QThread):
    """Thread for executing sequence configurations without blocking UI"""
    progress_updated = pyqtSignal(int, int)  # current, total
    status_updated = pyqtSignal(str)  # status message
    finished = pyqtSignal()
    
    def __init__(self, controller: Controller, configurations: list):
        super().__init__()
        self.controller = controller
        self.configurations = configurations
        self.should_stop = False
    
    def stop_execution(self):
        """Stop the execution"""
        self.should_stop = True
    
    def run(self):
        """Execute the sequence of configurations"""
        total = len(self.configurations)
        
        for idx, config in enumerate(self.configurations):
            if self.should_stop:
                self.status_updated.emit("Execution stopped by user")
                break
            
            try:
                self.status_updated.emit(f"Executing configuration {idx + 1}/{total}...")
                self.progress_updated.emit(idx + 1, total)
                
                # Apply configuration
                if self.controller.instr is None:
                    self.status_updated.emit("Error: No device connected")
                    break
                
                if 'center_frequency' in config:
                    self.controller.set_center_freq(config['center_frequency'])
                
                if 'frequency_modulation' in config:
                    self.controller.set_fm_frequency(config['frequency_modulation'])
                    # Enable FM if frequency is set
                    if config['frequency_modulation'] > 0:
                        self.controller.set_fm_state(True)
                
                if 'power' in config:
                    self.controller.set_power(config['power'])
                
                if 'time_of_sweep' in config and 'num_sweeps' in config:
                    # Update external waveform if available
                    if hasattr(self.controller, 'waveform_generator') and self.controller.waveform_generator:
                        amplitude = config.get('amplitude', 2.0)
                        offset = config.get('offset', 0.0)
                        time_of_sweep = config['time_of_sweep']
                        num_sweeps = config['num_sweeps']
                        self.controller.start_external_waveform(time_of_sweep, num_sweeps, amplitude, offset)
                
                # Delay after each instruction
                delay = config.get('delay', 0.0)
                if delay > 0:
                    time.sleep(delay)
                
            except Exception as e:
                self.status_updated.emit(f"Error in configuration {idx + 1}: {str(e)}")
                # Continue with next configuration
        
        self.status_updated.emit("Sequence execution completed")
        self.finished.emit()


class SequenceWindow(QDialog):
    """Window for loading and executing batch configuration sequences"""
    
    def __init__(self, parent=None, controller: Controller = None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Sequence Configuration")
        self.setWindowIcon(parent.windowIcon() if parent else None)
        self.setMinimumSize(900, 700)
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        # Store loaded configurations
        self.loaded_configurations = []
        self.execution_thread = None
        
        # Apply styling
        self._apply_styles()
        
        # Setup UI
        self._setup_ui()
    
    def _apply_styles(self):
        """Apply styling to the window"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                background-color: {COLORS['card']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {COLORS['gray_lighter']};
                color: {COLORS['dark']};
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['primary_light']};
                color: white;
            }}
        """)
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Sequence Configuration")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['dark']};")
        layout.addWidget(title)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Page 1: Load JSON File
        page1 = self._create_load_page()
        tabs.addTab(page1, "Load Sequence")
        
        # Page 2: Manual Configuration
        page2 = self._create_manual_page()
        tabs.addTab(page2, "Manual Configuration")
        
        layout.addWidget(tabs)
    
    def _create_load_page(self):
        """Create the page for loading JSON files"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # File selection section
        file_group = QGroupBox("Load Sequence File")
        file_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                padding-bottom: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        file_layout = QVBoxLayout(file_group)
        file_layout.setContentsMargins(15, 15, 15, 15)
        file_layout.setSpacing(12)
        
        file_row = QHBoxLayout()
        file_row.setSpacing(12)
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet(f"color: {COLORS['gray']}; padding: 8px;")
        file_row.addWidget(self.file_path_label)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
        """)
        browse_btn.clicked.connect(self._browse_json_file)
        file_row.addWidget(browse_btn)
        
        file_layout.addLayout(file_row)
        layout.addWidget(file_group)
        
        # Configuration preview table
        preview_group = QGroupBox("Configuration Preview")
        preview_group.setStyleSheet(file_group.styleSheet())
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(15, 15, 15, 15)
        preview_layout.setSpacing(12)
        
        self.config_table = QTableWidget()
        self.config_table.setColumnCount(7)
        self.config_table.setHorizontalHeaderLabels([
            "Center Freq (MHz)", "FM Freq (Hz)", "Power (dBm)", 
            "Time of Sweep (s)", "Num Sweeps", "Num Steps", "Delay (s)"
        ])
        self.config_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.config_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background-color: {COLORS['card']};
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary_light']};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """)
        preview_layout.addWidget(self.config_table)
        layout.addWidget(preview_group)
        
        # Execution controls
        exec_group = QGroupBox("Execution Controls")
        exec_group.setStyleSheet(file_group.styleSheet())
        exec_layout = QVBoxLayout(exec_group)
        exec_layout.setContentsMargins(15, 15, 15, 15)
        exec_layout.setSpacing(15)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {COLORS['border']};
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['success']};
                border-radius: 3px;
            }}
        """)
        exec_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {COLORS['gray']}; padding: 8px;")
        exec_layout.addWidget(self.status_label)
        
        # Control buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        
        self.start_btn = QPushButton("Start Sequence")
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success_dark']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['gray_light']};
                color: {COLORS['gray']};
            }}
        """)
        self.start_btn.clicked.connect(self._start_sequence)
        self.start_btn.setEnabled(False)
        button_row.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger_dark']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['gray_light']};
                color: {COLORS['gray']};
            }}
        """)
        self.stop_btn.clicked.connect(self._stop_sequence)
        self.stop_btn.setEnabled(False)
        button_row.addWidget(self.stop_btn)
        
        button_row.addStretch()
        exec_layout.addLayout(button_row)
        
        layout.addWidget(exec_group)
        layout.addStretch()
        
        return page
    
    def _create_manual_page(self):
        """Create the page for manual configuration entry"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Manual entry form
        form_group = QGroupBox("Configuration Parameters")
        form_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                padding-bottom: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        form_layout = QGridLayout(form_group)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(18)
        form_layout.setVerticalSpacing(18)
        
        # Center Frequency
        form_layout.addWidget(QLabel("Center Frequency (MHz):"), 0, 0)
        self.manual_center_freq = QDoubleSpinBox()
        self.manual_center_freq.setRange(0, 1000)
        self.manual_center_freq.setDecimals(3)
        form_layout.addWidget(self.manual_center_freq, 0, 1)
        
        # Frequency Modulation
        form_layout.addWidget(QLabel("FM Frequency (Hz):"), 1, 0)
        self.manual_fm_freq = QDoubleSpinBox()
        self.manual_fm_freq.setRange(0, 1000000)
        self.manual_fm_freq.setDecimals(3)
        form_layout.addWidget(self.manual_fm_freq, 1, 1)
        
        # Power
        form_layout.addWidget(QLabel("Power (dBm):"), 2, 0)
        self.manual_power = QDoubleSpinBox()
        self.manual_power.setRange(-100, 100)
        self.manual_power.setDecimals(1)
        form_layout.addWidget(self.manual_power, 2, 1)
        
        # Waveform Type (default to triangular)
        form_layout.addWidget(QLabel("Waveform Type:"), 3, 0)
        self.manual_waveform_type = QComboBox()
        self.manual_waveform_type.addItems(["Triangular"])
        self.manual_waveform_type.setEnabled(False)  # Only triangular for now
        form_layout.addWidget(self.manual_waveform_type, 3, 1)
        
        # Number of Steps
        form_layout.addWidget(QLabel("Number of Steps:"), 4, 0)
        self.manual_num_steps = QSpinBox()
        self.manual_num_steps.setRange(2, 10000)
        self.manual_num_steps.setValue(100)
        form_layout.addWidget(self.manual_num_steps, 4, 1)
        
        # Number of Sweeps
        form_layout.addWidget(QLabel("Number of Sweeps:"), 5, 0)
        self.manual_num_sweeps = QSpinBox()
        self.manual_num_sweeps.setRange(1, 10000)
        self.manual_num_sweeps.setValue(1)
        form_layout.addWidget(self.manual_num_sweeps, 5, 1)
        
        # Time of Sweep
        form_layout.addWidget(QLabel("Time of Sweep (s):"), 6, 0)
        self.manual_time_of_sweep = QDoubleSpinBox()
        self.manual_time_of_sweep.setRange(0.001, 10000)
        self.manual_time_of_sweep.setDecimals(3)
        self.manual_time_of_sweep.setValue(1.0)
        form_layout.addWidget(self.manual_time_of_sweep, 6, 1)
        
        # Delay
        form_layout.addWidget(QLabel("Delay (s):"), 7, 0)
        self.manual_delay = QDoubleSpinBox()
        self.manual_delay.setRange(0, 3600)
        self.manual_delay.setDecimals(3)
        self.manual_delay.setValue(0.0)
        form_layout.addWidget(self.manual_delay, 7, 1)
        
        # Style inputs
        input_style = f"""
            QDoubleSpinBox, QSpinBox, QComboBox {{
                padding: 8px;
                border: 2px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['card']};
                min-height: 25px;
            }}
            QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QLabel {{
                padding: 4px 0px;
            }}
        """
        for widget in [self.manual_center_freq, self.manual_fm_freq, self.manual_power,
                      self.manual_waveform_type, self.manual_num_steps, self.manual_num_sweeps,
                      self.manual_time_of_sweep, self.manual_delay]:
            widget.setStyleSheet(input_style)
        
        # Wrap form group in scroll area
        form_scroll = QScrollArea()
        form_scroll.setWidget(form_group)
        form_scroll.setWidgetResizable(True)
        form_scroll.setMinimumHeight(250)
        form_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)
        layout.addWidget(form_scroll)
        
        # Add spacing before button
        layout.addSpacing(10)
        
        # Add to sequence button
        add_btn = QPushButton("Add to Sequence")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
        """)
        add_btn.clicked.connect(self._add_manual_config)
        layout.addWidget(add_btn)
        
        # Manual sequence table
        manual_table_group = QGroupBox("Manual Sequence")
        manual_table_group.setStyleSheet(form_group.styleSheet())
        manual_table_layout = QVBoxLayout(manual_table_group)
        manual_table_layout.setContentsMargins(15, 15, 15, 15)
        manual_table_layout.setSpacing(12)
        
        self.manual_config_table = QTableWidget()
        self.manual_config_table.setColumnCount(7)
        self.manual_config_table.setHorizontalHeaderLabels([
            "Center Freq (MHz)", "FM Freq (Hz)", "Power (dBm)", 
            "Time of Sweep (s)", "Num Sweeps", "Num Steps", "Delay (s)"
        ])
        self.manual_config_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.manual_config_table.setStyleSheet(self.config_table.styleSheet())
        manual_table_layout.addWidget(self.manual_config_table)
        
        # Clear button
        clear_btn = QPushButton("Clear Sequence")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger_dark']};
            }}
        """)
        clear_btn.clicked.connect(self._clear_manual_sequence)
        manual_table_layout.addWidget(clear_btn)
        
        layout.addWidget(manual_table_group)
        
        # Execution controls for manual page
        manual_exec_group = QGroupBox("Execution Controls")
        manual_exec_group.setStyleSheet(form_group.styleSheet())
        manual_exec_layout = QVBoxLayout(manual_exec_group)
        manual_exec_layout.setContentsMargins(15, 15, 15, 15)
        manual_exec_layout.setSpacing(15)
        
        self.manual_progress_bar = QProgressBar()
        self.manual_progress_bar.setStyleSheet(self.progress_bar.styleSheet())
        manual_exec_layout.addWidget(self.manual_progress_bar)
        
        self.manual_status_label = QLabel("Ready")
        self.manual_status_label.setStyleSheet(f"color: {COLORS['gray']}; padding: 8px;")
        manual_exec_layout.addWidget(self.manual_status_label)
        
        manual_button_row = QHBoxLayout()
        manual_button_row.setSpacing(12)
        
        self.manual_start_btn = QPushButton("Start Sequence")
        self.manual_start_btn.setStyleSheet(self.start_btn.styleSheet())
        self.manual_start_btn.clicked.connect(self._start_manual_sequence)
        self.manual_start_btn.setEnabled(False)
        manual_button_row.addWidget(self.manual_start_btn)
        
        self.manual_stop_btn = QPushButton("Stop")
        self.manual_stop_btn.setStyleSheet(self.stop_btn.styleSheet())
        self.manual_stop_btn.clicked.connect(self._stop_sequence)
        self.manual_stop_btn.setEnabled(False)
        manual_button_row.addWidget(self.manual_stop_btn)
        
        manual_button_row.addStretch()
        manual_exec_layout.addLayout(manual_button_row)
        
        layout.addWidget(manual_exec_group)
        layout.addStretch()
        
        return page
    
    def _browse_json_file(self):
        """Browse for JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Sequence JSON File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self._load_json_file(file_path)
    
    def _load_json_file(self, file_path: str):
        """Load and parse JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Expect JSON format: {"configurations": [...]}
            if isinstance(data, dict) and 'configurations' in data:
                self.loaded_configurations = data['configurations']
            elif isinstance(data, list):
                # Also support direct list format
                self.loaded_configurations = data
            else:
                raise ValueError("Invalid JSON format. Expected object with 'configurations' array or direct array.")
            
            # Validate and display configurations
            self._update_config_table()
            self._update_manual_table()
            self.start_btn.setEnabled(len(self.loaded_configurations) > 0)
            self.manual_start_btn.setEnabled(len(self.loaded_configurations) > 0)
            
            QMessageBox.information(
                self,
                "File Loaded",
                f"Successfully loaded {len(self.loaded_configurations)} configuration(s)."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading File",
                f"Failed to load JSON file:\n{str(e)}"
            )
            self.loaded_configurations = []
            self._update_config_table()
            self._update_manual_table()
            self.start_btn.setEnabled(False)
            self.manual_start_btn.setEnabled(False)
    
    def _update_config_table(self):
        """Update the configuration preview table"""
        self.config_table.setRowCount(len(self.loaded_configurations))
        
        for row, config in enumerate(self.loaded_configurations):
            # Center Frequency
            center_freq = config.get('center_frequency', 0.0)
            self.config_table.setItem(row, 0, QTableWidgetItem(f"{center_freq:.3f}"))
            
            # FM Frequency
            fm_freq = config.get('frequency_modulation', 0.0)
            self.config_table.setItem(row, 1, QTableWidgetItem(f"{fm_freq:.3f}"))
            
            # Power
            power = config.get('power', 0.0)
            self.config_table.setItem(row, 2, QTableWidgetItem(f"{power:.1f}"))
            
            # Time of Sweep
            time_of_sweep = config.get('time_of_sweep', 0.0)
            self.config_table.setItem(row, 3, QTableWidgetItem(f"{time_of_sweep:.3f}"))
            
            # Number of Sweeps
            num_sweeps = config.get('num_sweeps', 1)
            self.config_table.setItem(row, 4, QTableWidgetItem(str(num_sweeps)))
            
            # Number of Steps
            num_steps = config.get('num_steps', 0)
            self.config_table.setItem(row, 5, QTableWidgetItem(str(num_steps)))
            
            # Delay
            delay = config.get('delay', 0.0)
            self.config_table.setItem(row, 6, QTableWidgetItem(f"{delay:.3f}"))
    
    def _update_manual_table(self):
        """Update the manual configuration table"""
        self.manual_config_table.setRowCount(len(self.loaded_configurations))
        
        for row, config in enumerate(self.loaded_configurations):
            # Center Frequency
            center_freq = config.get('center_frequency', 0.0)
            self.manual_config_table.setItem(row, 0, QTableWidgetItem(f"{center_freq:.3f}"))
            
            # FM Frequency
            fm_freq = config.get('frequency_modulation', 0.0)
            self.manual_config_table.setItem(row, 1, QTableWidgetItem(f"{fm_freq:.3f}"))
            
            # Power
            power = config.get('power', 0.0)
            self.manual_config_table.setItem(row, 2, QTableWidgetItem(f"{power:.1f}"))
            
            # Time of Sweep
            time_of_sweep = config.get('time_of_sweep', 0.0)
            self.manual_config_table.setItem(row, 3, QTableWidgetItem(f"{time_of_sweep:.3f}"))
            
            # Number of Sweeps
            num_sweeps = config.get('num_sweeps', 1)
            self.manual_config_table.setItem(row, 4, QTableWidgetItem(str(num_sweeps)))
            
            # Number of Steps
            num_steps = config.get('num_steps', 0)
            self.manual_config_table.setItem(row, 5, QTableWidgetItem(str(num_steps)))
            
            # Delay
            delay = config.get('delay', 0.0)
            self.manual_config_table.setItem(row, 6, QTableWidgetItem(f"{delay:.3f}"))
    
    def _clear_manual_sequence(self):
        """Clear the manual sequence"""
        reply = QMessageBox.question(
            self,
            "Clear Sequence",
            "Are you sure you want to clear all configurations?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.loaded_configurations = []
            self._update_config_table()
            self._update_manual_table()
            self.start_btn.setEnabled(False)
            self.manual_start_btn.setEnabled(False)
    
    def _start_manual_sequence(self):
        """Start executing the manual sequence"""
        if not self.controller or self.controller.instr is None:
            QMessageBox.warning(
                self,
                "No Device Connected",
                "Please connect to a device before starting the sequence."
            )
            return
        
        if len(self.loaded_configurations) == 0:
            QMessageBox.warning(
                self,
                "No Configurations",
                "Please add configurations to the sequence."
            )
            return
        
        # Create and start execution thread (shared with load page)
        self.execution_thread = SequenceExecutionThread(
            self.controller,
            self.loaded_configurations
        )
        # Connect to both pages' progress/status updates
        self.execution_thread.progress_updated.connect(self._update_progress)
        self.execution_thread.progress_updated.connect(self._update_manual_progress)
        self.execution_thread.status_updated.connect(self._update_status)
        self.execution_thread.status_updated.connect(self._update_manual_status)
        self.execution_thread.finished.connect(self._sequence_finished)
        self.execution_thread.finished.connect(self._manual_sequence_finished)
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.manual_start_btn.setEnabled(False)
        self.manual_stop_btn.setEnabled(True)
        self.progress_bar.setMaximum(len(self.loaded_configurations))
        self.progress_bar.setValue(0)
        self.manual_progress_bar.setMaximum(len(self.loaded_configurations))
        self.manual_progress_bar.setValue(0)
        
        self.execution_thread.start()
    
    def _update_manual_progress(self, current: int, total: int):
        """Update manual progress bar"""
        self.manual_progress_bar.setMaximum(total)
        self.manual_progress_bar.setValue(current)
    
    def _update_manual_status(self, message: str):
        """Update manual status label"""
        self.manual_status_label.setText(message)
    
    def _manual_sequence_finished(self):
        """Handle manual sequence completion"""
        self.manual_start_btn.setEnabled(True)
        self.manual_stop_btn.setEnabled(False)
        if self.execution_thread:
            self.execution_thread = None
    
    def _add_manual_config(self):
        """Add manually entered configuration to sequence"""
        config = {
            'center_frequency': self.manual_center_freq.value(),
            'frequency_modulation': self.manual_fm_freq.value(),
            'power': self.manual_power.value(),
            'waveform_type': self.manual_waveform_type.currentText().lower(),
            'num_steps': self.manual_num_steps.value(),
            'num_sweeps': self.manual_num_sweeps.value(),
            'time_of_sweep': self.manual_time_of_sweep.value(),
            'delay': self.manual_delay.value()
        }
        
        self.loaded_configurations.append(config)
        self._update_config_table()
        self._update_manual_table()
        self.start_btn.setEnabled(True)
        self.manual_start_btn.setEnabled(True)
        
        # Clear form for next entry
        self.manual_center_freq.setValue(0.0)
        self.manual_fm_freq.setValue(0.0)
        self.manual_power.setValue(0.0)
        self.manual_num_steps.setValue(100)
        self.manual_num_sweeps.setValue(1)
        self.manual_time_of_sweep.setValue(1.0)
        self.manual_delay.setValue(0.0)
    
    def _start_sequence(self):
        """Start executing the sequence from loaded file"""
        if not self.controller or self.controller.instr is None:
            QMessageBox.warning(
                self,
                "No Device Connected",
                "Please connect to a device before starting the sequence."
            )
            return
        
        if len(self.loaded_configurations) == 0:
            QMessageBox.warning(
                self,
                "No Configurations",
                "Please load a sequence file or add manual configurations."
            )
            return
        
        # Create and start execution thread (shared with manual page)
        self.execution_thread = SequenceExecutionThread(
            self.controller,
            self.loaded_configurations
        )
        # Connect to both pages' progress/status updates
        self.execution_thread.progress_updated.connect(self._update_progress)
        self.execution_thread.progress_updated.connect(self._update_manual_progress)
        self.execution_thread.status_updated.connect(self._update_status)
        self.execution_thread.status_updated.connect(self._update_manual_status)
        self.execution_thread.finished.connect(self._sequence_finished)
        self.execution_thread.finished.connect(self._manual_sequence_finished)
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.manual_start_btn.setEnabled(False)
        self.manual_stop_btn.setEnabled(True)
        self.progress_bar.setMaximum(len(self.loaded_configurations))
        self.progress_bar.setValue(0)
        self.manual_progress_bar.setMaximum(len(self.loaded_configurations))
        self.manual_progress_bar.setValue(0)
        
        self.execution_thread.start()
    
    def _stop_sequence(self):
        """Stop the sequence execution"""
        if self.execution_thread and self.execution_thread.isRunning():
            self.execution_thread.stop_execution()
            self.execution_thread.wait()
            self._sequence_finished()
            self._manual_sequence_finished()
            if self.execution_thread:
                self.execution_thread = None
    
    def _update_progress(self, current: int, total: int):
        """Update progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
    
    def _update_status(self, message: str):
        """Update status label"""
        self.status_label.setText(message)
    
    def _sequence_finished(self):
        """Handle sequence completion"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if self.execution_thread:
            self.execution_thread = None
