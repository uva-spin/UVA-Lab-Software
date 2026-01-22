from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QDoubleSpinBox, QGroupBox, QGridLayout,
                             QPushButton, QCheckBox, QSpinBox, QFrame, QToolBar, QAction, QStatusBar, QLineEdit,
                             QScrollArea, QComboBox, QMessageBox, QGraphicsDropShadowEffect, QDialog, QTextBrowser,
                             QTabWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QLinearGradient
from commands import Controller
from RsInstrument import RsInstrument
from ConfigurationWindow import ConfigurationWindow
from HelpWindow import HelpWindow
import json
import os

# Color scheme constants
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



class MainWindow(QMainWindow):
    def __init__(self, controller: Controller):
        super().__init__()
        self.setWindowTitle("ssRF/AFP Control Panel")
        self.setWindowIcon(QIcon('./assets/program.png'))      
        self.setGeometry(100, 100, 950, 700)
        self.controller = controller
        
        # Load target configurations from JSON file
        self.target_configs = self._load_target_configs()
        
        # Apply global stylesheet
        self._apply_global_styles()
        
        ### menu bar

        file_menu = self.menuBar().addMenu("&File")
        edit_menu = self.menuBar().addMenu("&Edit")
        help_menu = self.menuBar().addMenu("&Help")

        file_menu.addAction("Open", lambda: print("Open"))
        file_menu.addAction("Configurations...", self.open_configuration_window)

        undo_action = QAction(QIcon('./assets/undo.jpg'), "Undo", self)
        redo_action = QAction(QIcon('./assets/redo.png'), "Redo", self)
        undo_action.setShortcut("Ctrl+Z")

        redo_action.setShortcut("Ctrl+Y")
        undo_action.triggered.connect(lambda: print("Undo"))
        redo_action.triggered.connect(lambda: print("Redo"))

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        
        # Help menu actions
        help_action = QAction("Help Contents", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.open_help_window)
        help_menu.addAction(help_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        ### toolbar, below menu bar

        toolbar = QToolBar("Toolbar")
        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)
        self.addToolBar(toolbar)

        ### status bar at bottom

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
    
    def _apply_global_styles(self):
        """Apply a modern global stylesheet to the application"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QMenuBar {{
                background-color: {COLORS['dark']};
                color: white;
                padding: 5px;
                font-size: 12px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {COLORS['dark_light']};
            }}
            QMenu {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 25px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['primary_light']};
                color: white;
            }}
            QToolBar {{
                background-color: {COLORS['dark_light']};
                border: none;
                spacing: 5px;
                padding: 5px;
            }}
            QToolBar QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }}
            QToolBar QToolButton:hover {{
                background-color: {COLORS['primary']};
            }}
            QStatusBar {{
                background-color: {COLORS['dark']};
                color: {COLORS['gray_lighter']};
                font-size: 11px;
                padding: 5px;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['gray_lighter']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['gray_light']};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['gray']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        ### main content area
        self.setup_ui()
        
        ### timer to update values periodically
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display_values)
        self.update_timer.start(1000)  # Update every second
        
        # Initial update
        self.update_display_values()
        
        self.show()
        
        # Window references
        self.config_window = None
        self.help_window = None

    def _load_target_configs(self):
        """Load target configurations from JSON file"""
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, 'configs', 'target_configs.json')
            
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('targets', {})
        except Exception as e:
            print(f"Error loading target configs: {e}")
            return {}

    def open_configuration_window(self):
        """Open the Configurations window."""
        if self.config_window is None or not self.config_window.isVisible():
            self.config_window = ConfigurationWindow()
            self.config_window.show()
        else:
            self.config_window.raise_()
            self.config_window.activateWindow()

    def open_help_window(self):
        """Open the Help window."""
        if self.help_window is None or not self.help_window.isVisible():
            self.help_window = HelpWindow(self)
            self.help_window.show()
        else:
            self.help_window.raise_()
            self.help_window.activateWindow()

    def show_about_dialog(self):
        """Show the About dialog."""
        about_text = f"""
        <h2 style="color: {COLORS['primary']};">ssRF/AFP Control Panel</h2>
        <p><strong>Version:</strong> 1.0.0</p>
        <p>A control application for RF signal generators used in 
        semi-saturated RF and Adiabatic Fast Passage (AFP) experiments.</p>
        <hr>
        <p><strong>Features:</strong></p>
        <ul>
            <li>Device discovery and connection via VISA</li>
            <li>Frequency sweep control</li>
            <li>Power level management</li>
            <li>FM and AM modulation support</li>
            <li>Real-time parameter monitoring</li>
        </ul>
        <hr>
        <p style="color: {COLORS['gray']};">
        Built with PyQt5 and RsInstrument<br>
        University of Virginia - Physics Lab
        </p>
        """
        QMessageBox.about(self, "About ssRF/AFP Control Panel", about_text)

    def _add_shadow(self, widget, blur=15, offset=3, color=QColor(0, 0, 0, 40)):
        """Add a subtle drop shadow to a widget"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setXOffset(offset)
        shadow.setYOffset(offset)
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)
        return shadow

    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {COLORS['background']};")
        self.setCentralWidget(central_widget)
        
        # Main layout - horizontal split between left panel and right content
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)
        
        # === LEFT PANEL: Controller Parameters (takes entire left side) ===
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame#leftPanel {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        left_panel.setObjectName("leftPanel")
        self._add_shadow(left_panel)
        
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(20, 20, 20, 20)
        left_panel_layout.setSpacing(12)
        
        # Title for parameters section with icon-like decoration
        params_header = QHBoxLayout()
        params_icon = QLabel("◉")
        params_icon.setStyleSheet(f"color: {COLORS['primary']}; font-size: 18px; background: transparent;")
        params_header.addWidget(params_icon)
        
        params_title = QLabel("Controller Parameters")
        params_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        params_title.setStyleSheet(f"color: {COLORS['dark']}; background: transparent;")
        params_header.addWidget(params_title)
        params_header.addStretch()
        left_panel_layout.addLayout(params_header)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
        left_panel_layout.addWidget(separator)
        
        # Target Selection Dropdown
        target_card = QFrame()
        target_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary_light']};
                border: 2px solid {COLORS['primary']};
                border-radius: 10px;
            }}
        """)
        target_card_layout = QHBoxLayout(target_card)
        target_card_layout.setContentsMargins(15, 12, 15, 12)
        target_card_layout.setSpacing(15)
        
        # Target label with icon
        target_icon = QLabel("🎯")
        target_icon.setStyleSheet("font-size: 16px; background: transparent;")
        target_card_layout.addWidget(target_icon)
        
        target_label = QLabel("Targets")
        target_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        target_label.setStyleSheet(f"color: white; border: none; background: transparent;")
        target_label.setMinimumWidth(80)
        target_card_layout.addWidget(target_label)
        
        self.target_dropdown = QComboBox()
        self.target_dropdown.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                font-family: 'Segoe UI';
                min-width: 150px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['primary_light']};
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
                background-color: {COLORS['card']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['dark']};
                margin-right: 10px;
            }}
        """)
        
        # Populate the targets dropdown
        self.target_dropdown.addItem("-- Select Target --")
        for target_name in self.target_configs.keys():
            self.target_dropdown.addItem(target_name.upper(), target_name)
        
        self.target_dropdown.currentIndexChanged.connect(self.load_target_settings)
        target_card_layout.addWidget(self.target_dropdown)
        target_card_layout.addStretch()
        
        left_panel_layout.addWidget(target_card)
        
        # Small spacer before parameters
        left_panel_layout.addSpacing(5)
        
        # Create styled parameter cards stacked vertically (no scroll)
        # Center Frequency Card
        self.center_freq_input = self._create_parameter_card(
            left_panel_layout,
            "Center Frequency", "MHz", 
            QDoubleSpinBox, 0, 300, 3
        )
        self.center_freq_input.editingFinished.connect(lambda: self.update_parameter('center_freq', self.center_freq_input.value()))
        
        # Frequency Width Card
        self.freq_width_input = self._create_parameter_card(
            left_panel_layout,
            "Frequency Width", "MHz",
            QDoubleSpinBox, 0, 300, 3
        )
        self.freq_width_input.editingFinished.connect(lambda: self.update_parameter('freq_width', self.freq_width_input.value()))
        
        # Spacing Card
        self.spacing_input = self._create_parameter_card(
            left_panel_layout,
            "Spacing", "",
            QComboBox, ["LINear", "LOGarithmic"], None, None
        )
        self.spacing_input.currentTextChanged.connect(lambda: self.update_parameter('spacing', self.spacing_input.currentText()))
        
        # Power Card
        self.power_input = self._create_parameter_card(
            left_panel_layout,
            "Power", "dBm",
            QDoubleSpinBox, -100, 100, 1
        )
        self.power_input.editingFinished.connect(lambda: self.update_parameter('power', self.power_input.value()))
        
        # Mode Card
        self.mode_input = self._create_parameter_card(
            left_panel_layout,
            "Mode", "",
            QComboBox, ["CW", "Sweep"], None, None
        )
        self.mode_input.currentTextChanged.connect(lambda: self.update_parameter('mode', self.mode_input.currentText()))
        
        # Sweep Points Card
        self.sweep_points_input = self._create_parameter_card(
            left_panel_layout,
            "Sweep Points", "",
            QSpinBox, 1, 100000, None
        )
        self.sweep_points_input.editingFinished.connect(lambda: self.update_parameter('sweep_points', self.sweep_points_input.value()))
        
        # Sweep Dwell Card
        self.sweep_dwell_input = self._create_parameter_card(
            left_panel_layout,
            "Sweep Dwell", "ms",
            QDoubleSpinBox, 0, 1000000, 3
        )
        self.sweep_dwell_input.editingFinished.connect(lambda: self.update_parameter('sweep_dwell', self.sweep_dwell_input.value()))
        
        left_panel_layout.addStretch()  # Push cards to top
        
        # Add left panel to main layout (stretch factor 1 to take available space)
        main_layout.addWidget(left_panel, stretch=1)
        
        # === RIGHT PANEL: RF Status and other controls ===
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame#rightPanel {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        right_panel.setObjectName("rightPanel")
        self._add_shadow(right_panel)
        
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(20, 20, 20, 20)
        right_panel_layout.setSpacing(15)
        
        # Device Selection Section
        device_section = QFrame()
        device_section.setObjectName("deviceSection")
        device_section.setStyleSheet(f"""
            QFrame#deviceSection {{
                background-color: {COLORS['gray_lighter']};
                border: none;
                border-radius: 10px;
            }}
        """)
        device_section_layout = QVBoxLayout(device_section)
        device_section_layout.setContentsMargins(15, 15, 15, 15)
        device_section_layout.setSpacing(10)
        
        # Device section title with icon
        device_header = QHBoxLayout()
        device_icon = QLabel("🔌")
        device_icon.setStyleSheet("font-size: 16px; background: transparent;")
        device_header.addWidget(device_icon)
        
        device_title = QLabel("Device Selection")
        device_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        device_title.setStyleSheet(f"color: {COLORS['dark']}; background: transparent;")
        device_header.addWidget(device_title)
        device_header.addStretch()
        device_section_layout.addLayout(device_header)
        
        # Device dropdown and refresh button in horizontal layout
        device_row_layout = QHBoxLayout()
        
        self.device_dropdown = QComboBox()
        self.device_dropdown.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11px;
                font-family: 'Segoe UI';
                min-width: 200px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['primary_light']};
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['dark']};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                selection-background-color: {COLORS['primary_light']};
                selection-color: white;
            }}
        """)
        self.device_dropdown.addItem("No devices found")
        device_row_layout.addWidget(self.device_dropdown, stretch=1)
        
        # Refresh button
        self.refresh_devices_button = QPushButton("⟳ Scan")
        self.refresh_devices_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                font-weight: bold;
                font-family: 'Segoe UI';
                padding: 8px 18px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['dark']};
            }}
        """)
        self.refresh_devices_button.clicked.connect(self.scan_for_devices)
        device_row_layout.addWidget(self.refresh_devices_button)
        
        device_section_layout.addLayout(device_row_layout)
        
        # Connect button
        self.connect_device_button = QPushButton("⚡ Connect")
        self.connect_device_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                font-weight: bold;
                font-family: 'Segoe UI';
                padding: 10px;
                border-radius: 8px;
                border: none;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success_dark']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['dark']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['gray_light']};
                color: {COLORS['gray']};
            }}
        """)
        self.connect_device_button.clicked.connect(self.connect_to_selected_device)
        device_section_layout.addWidget(self.connect_device_button)
        
        # Connection status label
        self.connection_status_label = QLabel("● Not connected")
        self.connection_status_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 11px; font-family: 'Segoe UI'; background: transparent;")
        self.connection_status_label.setAlignment(Qt.AlignCenter)
        device_section_layout.addWidget(self.connection_status_label)
        
        right_panel_layout.addWidget(device_section)
        
        # Store available devices info (resource_string -> idn_string mapping)
        self.available_devices = {}
        
        # RF Controls Section
        rf_section = QFrame()
        rf_section.setObjectName("rfSection")
        rf_section.setStyleSheet(f"""
            QFrame#rfSection {{
                background-color: {COLORS['gray_lighter']};
                border: none;
                border-radius: 10px;
            }}
        """)
        rf_section_layout = QVBoxLayout(rf_section)
        rf_section_layout.setContentsMargins(15, 15, 15, 15)
        rf_section_layout.setSpacing(12)
        
        # RF section title
        rf_header = QHBoxLayout()
        rf_icon = QLabel("📡")
        rf_icon.setStyleSheet("font-size: 16px; background: transparent;")
        rf_header.addWidget(rf_icon)
        
        rf_title = QLabel("RF Output Control")
        rf_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        rf_title.setStyleSheet(f"color: {COLORS['dark']}; background: transparent;")
        rf_header.addWidget(rf_title)
        rf_header.addStretch()
        rf_section_layout.addLayout(rf_header)
        
        # RF Controls row
        rf_controls_layout = QHBoxLayout()
        rf_controls_layout.setSpacing(10)
        
        # Turn on/off RF button
        self.turn_on_off_rf_button = QPushButton("⏻ Turn On RF")
        self.turn_on_off_rf_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['dark']};
                font-weight: bold;
                font-family: 'Segoe UI';
                padding: 12px 20px;
                border-radius: 8px;
                border: 2px solid {COLORS['border']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
                color: white;
                border-color: {COLORS['primary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_dark']};
            }}
        """)
        self.turn_on_off_rf_button.clicked.connect(lambda: self.controller.activate_rf())
        rf_controls_layout.addWidget(self.turn_on_off_rf_button)
        
        # RF Status indicator
        self.rf_status = 'OFF'
        self.rf_status_label = QLabel(f"● RF: {self.rf_status}")
        self.rf_status_label.setAlignment(Qt.AlignCenter)
        self.rf_status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['danger']};
                color: white;
                font-weight: bold;
                font-family: 'Segoe UI';
                padding: 12px 20px;
                border-radius: 8px;
                min-width: 100px;
                font-size: 13px;
            }}
        """)
        rf_controls_layout.addWidget(self.rf_status_label)
        
        rf_section_layout.addLayout(rf_controls_layout)
        right_panel_layout.addWidget(rf_section)
        
        # === MODULATION SECTION ===
        modulation_section = QFrame()
        modulation_section.setObjectName("modulationSection")
        modulation_section.setStyleSheet(f"""
            QFrame#modulationSection {{
                background-color: {COLORS['gray_lighter']};
                border: none;
                border-radius: 10px;
            }}
        """)
        modulation_section_layout = QVBoxLayout(modulation_section)
        modulation_section_layout.setContentsMargins(15, 15, 15, 15)
        modulation_section_layout.setSpacing(12)
        
        # Modulation section title with icon
        mod_header = QHBoxLayout()
        mod_icon = QLabel("〰")
        mod_icon.setStyleSheet("font-size: 16px; background: transparent;")
        mod_header.addWidget(mod_icon)
        
        mod_title = QLabel("Modulation")
        mod_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        mod_title.setStyleSheet(f"color: {COLORS['dark']}; background: transparent;")
        mod_header.addWidget(mod_title)
        mod_header.addStretch()
        modulation_section_layout.addLayout(mod_header)
        
        # --- Frequency Modulation (FM) ---
        fm_group = QFrame()
        fm_group.setObjectName("fmGroup")
        fm_group.setStyleSheet(f"""
            QFrame#fmGroup {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QFrame#fmGroup:hover {{
                border-color: {COLORS['primary_light']};
            }}
        """)
        fm_group_layout = QVBoxLayout(fm_group)
        fm_group_layout.setContentsMargins(12, 12, 12, 12)
        fm_group_layout.setSpacing(8)
        
        # FM Enable checkbox
        self.fm_enable_checkbox = QCheckBox("Frequency Modulation (FM)")
        self.fm_enable_checkbox.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.fm_enable_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['dark']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {COLORS['gray_light']};
                background-color: {COLORS['card']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLORS['primary']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
        """)
        self.fm_enable_checkbox.stateChanged.connect(self.toggle_fm)
        fm_group_layout.addWidget(self.fm_enable_checkbox)
        
        # FM Parameters container
        self.fm_params_widget = QWidget()
        fm_params_layout = QGridLayout(self.fm_params_widget)
        fm_params_layout.setContentsMargins(5, 8, 5, 0)
        fm_params_layout.setSpacing(8)
        fm_params_layout.setColumnStretch(1, 1)
        
        # Common style for modulation input widgets
        mod_input_style = f"""
            QDoubleSpinBox, QSpinBox {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Segoe UI';
                font-size: 11px;
                min-width: 100px;
            }}
            QDoubleSpinBox:hover, QSpinBox:hover {{
                border-color: {COLORS['primary_light']};
            }}
            QDoubleSpinBox:focus, QSpinBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QDoubleSpinBox:disabled, QSpinBox:disabled {{
                background-color: {COLORS['gray_lighter']};
                color: {COLORS['gray']};
            }}
        """
        
        mod_combo_style = f"""
            QComboBox {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Segoe UI';
                font-size: 11px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['primary_light']};
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox:disabled {{
                background-color: {COLORS['gray_lighter']};
                color: {COLORS['gray']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {COLORS['dark']};
                margin-right: 8px;
            }}
        """
        
        mod_label_style = f"color: {COLORS['gray']}; font-family: 'Segoe UI'; font-size: 11px;"
        
        # FM Deviation
        fm_dev_label = QLabel("Deviation:")
        fm_dev_label.setStyleSheet(mod_label_style)
        fm_params_layout.addWidget(fm_dev_label, 0, 0)
        
        self.fm_deviation_input = QDoubleSpinBox()
        self.fm_deviation_input.setRange(0, 100000)
        self.fm_deviation_input.setDecimals(3)
        self.fm_deviation_input.setSuffix(" kHz")
        self.fm_deviation_input.setStyleSheet(mod_input_style)
        self.fm_deviation_input.editingFinished.connect(lambda: self.update_modulation_parameter('fm_deviation', self.fm_deviation_input.value()))
        fm_params_layout.addWidget(self.fm_deviation_input, 0, 1)
        
        # FM Frequency (modulation rate)
        fm_freq_label = QLabel("Frequency:")
        fm_freq_label.setStyleSheet(mod_label_style)
        fm_params_layout.addWidget(fm_freq_label, 1, 0)
        
        self.fm_frequency_input = QDoubleSpinBox()
        self.fm_frequency_input.setRange(0, 1000000)
        self.fm_frequency_input.setDecimals(3)
        self.fm_frequency_input.setSuffix(" Hz")
        self.fm_frequency_input.setStyleSheet(mod_input_style)
        self.fm_frequency_input.editingFinished.connect(lambda: self.update_modulation_parameter('fm_frequency', self.fm_frequency_input.value()))
        fm_params_layout.addWidget(self.fm_frequency_input, 1, 1)
        
        # FM Source
        fm_source_label = QLabel("Source:")
        fm_source_label.setStyleSheet(mod_label_style)
        fm_params_layout.addWidget(fm_source_label, 2, 0)
        
        self.fm_source_input = QComboBox()
        self.fm_source_input.addItems(["INT", "EXT"])
        self.fm_source_input.setStyleSheet(mod_combo_style)
        self.fm_source_input.currentTextChanged.connect(lambda: self.update_modulation_parameter('fm_source', self.fm_source_input.currentText()))
        fm_params_layout.addWidget(self.fm_source_input, 2, 1)
        
        fm_group_layout.addWidget(self.fm_params_widget)
        self.fm_params_widget.setEnabled(False)  # Initially disabled
        
        modulation_section_layout.addWidget(fm_group)
        
        # --- Amplitude Modulation (AM) ---
        am_group = QFrame()
        am_group.setObjectName("amGroup")
        am_group.setStyleSheet(f"""
            QFrame#amGroup {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QFrame#amGroup:hover {{
                border-color: {COLORS['warning']};
            }}
        """)
        am_group_layout = QVBoxLayout(am_group)
        am_group_layout.setContentsMargins(12, 12, 12, 12)
        am_group_layout.setSpacing(8)
        
        # AM Enable checkbox
        self.am_enable_checkbox = QCheckBox("Amplitude Modulation (AM)")
        self.am_enable_checkbox.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.am_enable_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['dark']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {COLORS['gray_light']};
                background-color: {COLORS['card']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLORS['warning']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['warning']};
                border-color: {COLORS['warning']};
            }}
        """)
        self.am_enable_checkbox.stateChanged.connect(self.toggle_am)
        am_group_layout.addWidget(self.am_enable_checkbox)
        
        # AM Parameters container
        self.am_params_widget = QWidget()
        am_params_layout = QGridLayout(self.am_params_widget)
        am_params_layout.setContentsMargins(5, 8, 5, 0)
        am_params_layout.setSpacing(8)
        am_params_layout.setColumnStretch(1, 1)
        
        # AM Depth
        am_depth_label = QLabel("Depth:")
        am_depth_label.setStyleSheet(mod_label_style)
        am_params_layout.addWidget(am_depth_label, 0, 0)
        
        self.am_depth_input = QDoubleSpinBox()
        self.am_depth_input.setRange(0, 100)
        self.am_depth_input.setDecimals(1)
        self.am_depth_input.setSuffix(" %")
        self.am_depth_input.setStyleSheet(mod_input_style)
        self.am_depth_input.editingFinished.connect(lambda: self.update_modulation_parameter('am_depth', self.am_depth_input.value()))
        am_params_layout.addWidget(self.am_depth_input, 0, 1)
        
        # AM Frequency (modulation rate)
        am_freq_label = QLabel("Frequency:")
        am_freq_label.setStyleSheet(mod_label_style)
        am_params_layout.addWidget(am_freq_label, 1, 0)
        
        self.am_frequency_input = QDoubleSpinBox()
        self.am_frequency_input.setRange(0, 1000000)
        self.am_frequency_input.setDecimals(3)
        self.am_frequency_input.setSuffix(" Hz")
        self.am_frequency_input.setStyleSheet(mod_input_style)
        self.am_frequency_input.editingFinished.connect(lambda: self.update_modulation_parameter('am_frequency', self.am_frequency_input.value()))
        am_params_layout.addWidget(self.am_frequency_input, 1, 1)
        
        # AM Source
        am_source_label = QLabel("Source:")
        am_source_label.setStyleSheet(mod_label_style)
        am_params_layout.addWidget(am_source_label, 2, 0)
        
        self.am_source_input = QComboBox()
        self.am_source_input.addItems(["INT", "EXT"])
        self.am_source_input.setStyleSheet(mod_combo_style)
        self.am_source_input.currentTextChanged.connect(lambda: self.update_modulation_parameter('am_source', self.am_source_input.currentText()))
        am_params_layout.addWidget(self.am_source_input, 2, 1)
        
        am_group_layout.addWidget(self.am_params_widget)
        self.am_params_widget.setEnabled(False)  # Initially disabled
        
        modulation_section_layout.addWidget(am_group)
        
        right_panel_layout.addWidget(modulation_section)
        
        right_panel_layout.addStretch()  # Push content to top
        
        # Add right panel to main layout (stretch factor 1 for equal sizing, adjust as needed)
        main_layout.addWidget(right_panel, stretch=1)

    def _create_parameter_card(self, layout, title, unit, input_type, min_val, max_val, decimals):
        """Create a compact styled parameter card with horizontal layout."""
        # Card frame
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['gray_lighter']};
                border: 2px solid transparent;
                border-radius: 10px;
            }}
            QFrame:hover {{
                border-color: {COLORS['primary_light']};
                background-color: {COLORS['card']};
            }}
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(15)
        
        # Title label on the left
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet(f"color: {COLORS['dark']}; border: none; background: transparent;")
        title_label.setMinimumWidth(130)
        card_layout.addWidget(title_label)
        
        # Create input widget based on type
        if input_type == QDoubleSpinBox:
            input_widget = QDoubleSpinBox()
            input_widget.setRange(min_val, max_val)
            input_widget.setDecimals(decimals)
            input_widget.setAlignment(Qt.AlignCenter)
        elif input_type == QSpinBox:
            input_widget = QSpinBox()
            input_widget.setRange(min_val, max_val)
            input_widget.setAlignment(Qt.AlignCenter)
        elif input_type == QComboBox:
            input_widget = QComboBox()
            # min_val is used to pass the list of options for QComboBox
            if min_val and isinstance(min_val, list):
                input_widget.addItems(min_val)
        else:  # QLineEdit
            input_widget = QLineEdit()
            input_widget.setAlignment(Qt.AlignCenter)
        
        input_widget.setStyleSheet(f"""
            QDoubleSpinBox, QSpinBox, QLineEdit, QComboBox {{
                background-color: {COLORS['card']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                font-family: 'Segoe UI';
                min-width: 120px;
            }}
            QDoubleSpinBox:hover, QSpinBox:hover, QLineEdit:hover, QComboBox:hover {{
                border-color: {COLORS['primary_light']};
            }}
            QDoubleSpinBox:focus, QSpinBox:focus, QLineEdit:focus, QComboBox:focus {{
                border-color: {COLORS['primary']};
                background-color: {COLORS['card']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['dark']};
                margin-right: 10px;
            }}
        """)
        card_layout.addWidget(input_widget)
        
        # Unit label (if applicable)
        if unit:
            unit_label = QLabel(unit)
            unit_label.setFont(QFont("Segoe UI", 11))
            unit_label.setStyleSheet(f"color: {COLORS['gray']}; border: none; background: transparent;")
            unit_label.setMinimumWidth(40)
            card_layout.addWidget(unit_label)
        else:
            # Add spacer for alignment when no unit
            card_layout.addSpacing(40)
        
        card_layout.addStretch()
        
        layout.addWidget(card)
        return input_widget

    def update_parameter(self, param_name, value):
        
        methods = {'center_freq': self.controller.set_center_freq, 
                   'freq_width': self.controller.set_freq_width,
                   'spacing': self.controller.set_spacing, 
                   'power': self.controller.set_power, 
                   'mode': self.controller.set_mode, 
                   'sweep_points': self.controller.set_sweep_points, 
                   'sweep_dwell': self.controller.set_sweep_dwell,
                   'fm_state': self.controller.set_fm_state,
                   'fm_deviation': self.controller.set_fm_deviation,
                   'fm_frequency': self.controller.set_fm_frequency,
                   'fm_source': self.controller.set_fm_source,
                   'am_state': self.controller.set_am_state,
                   'am_depth': self.controller.set_am_depth,
                   'am_frequency': self.controller.set_am_frequency,
                   'am_source': self.controller.set_am_source}
        try:
            methods[param_name](value)
            self.statusBar().showMessage(f"Updated {param_name} to {value}", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"Error updating {param_name}: {str(e)}", 3000)

    def load_target_settings(self, index):
        """Load default settings for the selected target"""
        if index <= 0:  # "-- Select Target --" or invalid
            return
        
        target_name = self.target_dropdown.currentData()
        if not target_name or target_name not in self.target_configs:
            return
        
        config = self.target_configs[target_name]
        
        try:
            for param_name, value in config.items():
                self.update_parameter(param_name, value)
            
            self.statusBar().showMessage(f"Loaded settings for target: {target_name.upper()}", 3000)
            
        except Exception as e:
            self.statusBar().showMessage(f"Error loading target settings: {str(e)}", 3000)

    def update_display_values(self):
        """Update all displayed values from the controller"""
        try:
            # Update RF Status
            rf_status = self.controller.get_rf_status()
            if rf_status:
                self.rf_status = 'ON'
                self.rf_status_label.setText(f"● RF: {self.rf_status}")
                self.rf_status_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {COLORS['success']};
                        color: white;
                        font-weight: bold;
                        font-family: 'Segoe UI';
                        padding: 12px 20px;
                        border-radius: 8px;
                        min-width: 100px;
                        font-size: 13px;
                    }}
                """)
                self.turn_on_off_rf_button.setText("⏻ Turn Off RF")
            else:
                self.rf_status = 'OFF'
                self.rf_status_label.setText(f"● RF: {self.rf_status}")
                self.rf_status_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {COLORS['danger']};
                        color: white;
                        font-weight: bold;
                        font-family: 'Segoe UI';
                        padding: 12px 20px;
                        border-radius: 8px;
                        min-width: 100px;
                        font-size: 13px;
                    }}
                """)
                self.turn_on_off_rf_button.setText("⏻ Turn On RF")


            if not self.center_freq_input.hasFocus():
                center_freq = self.controller.get_center_freq()
                self.center_freq_input.setValue(center_freq)
            
            if not self.freq_width_input.hasFocus():
                freq_width = self.controller.get_freq_width()
                self.freq_width_input.setValue(freq_width)
            
            if not self.spacing_input.hasFocus():
                spacing = self.controller.get_sweep_spacing()
                index = self.spacing_input.findText(spacing, Qt.MatchContains)
                if index >= 0:
                    self.spacing_input.setCurrentIndex(index)
            
            if not self.power_input.hasFocus():
                power = self.controller.get_power()
                self.power_input.setValue(power)
            
            if not self.mode_input.hasFocus():
                mode = self.controller.get_mode()
                index = self.mode_input.findText(mode)
                if index >= 0:
                    self.mode_input.setCurrentIndex(index)
            
            if not self.sweep_points_input.hasFocus():
                sweep_points = self.controller.get_sweep_points()
                self.sweep_points_input.setValue(sweep_points)
            
            if not self.sweep_dwell_input.hasFocus():
                sweep_dwell = self.controller.get_sweep_dwell()
                self.sweep_dwell_input.setValue(sweep_dwell)
                
        except Exception as e:
            pass

    def scan_for_devices(self):
        """Scan for available VISA devices and query their *IDN?"""
        self.statusBar().showMessage("Scanning for devices...")
        self.refresh_devices_button.setEnabled(False)
        self.device_dropdown.clear()
        self.available_devices = {}
        
        try:
            # List all available VISA resources
            resource_list = RsInstrument.list_resources('?*')
            
            if not resource_list:
                self.device_dropdown.addItem("No devices found")
                self.statusBar().showMessage("No devices found", 3000)
                return
            
            for resource in resource_list:
                try:
                    # Try to connect and query *IDN?
                    temp_instr = RsInstrument(resource, True, False, options='TerminationCharacter = \r\n')
                    temp_instr.visa_timeout = 2000  # Short timeout for scanning
                    idn = temp_instr.query_str('*IDN?').strip()
                    temp_instr.close()
                    
                    # Store the mapping and add to dropdown
                    self.available_devices[resource] = idn
                    # Show IDN in dropdown for user-friendly display
                    display_text = f"{idn} ({resource})"
                    self.device_dropdown.addItem(display_text, resource)
                    
                except Exception as e:
                    # Device didn't respond to *IDN?, skip it
                    continue
            
            if self.device_dropdown.count() == 0:
                self.device_dropdown.addItem("No compatible devices found")
                self.statusBar().showMessage("No compatible devices found", 3000)
            else:
                self.statusBar().showMessage(f"Found {self.device_dropdown.count()} device(s)", 3000)
                
        except Exception as e:
            self.device_dropdown.addItem("Error scanning devices")
            self.statusBar().showMessage(f"Error scanning: {str(e)}", 3000)
        finally:
            self.refresh_devices_button.setEnabled(True)

    def connect_to_selected_device(self):
        """Connect to the device selected in the dropdown"""
        # Get the resource string from the selected item's data
        resource = self.device_dropdown.currentData()
        
        if not resource:
            QMessageBox.warning(self, "No Device Selected", 
                              "Please scan for devices and select one from the dropdown.")
            return
        
        try:
            self.statusBar().showMessage(f"Connecting to {resource}...")
            self.connect_device_button.setEnabled(False)
            
            # Close existing connection if any
            try:
                self.controller.close()
            except:
                pass
            
            # Create new instrument connection
            new_instr = RsInstrument(resource, True, True, options='TerminationCharacter = \r\n')
            self.controller = Controller(new_instr)
            
            # Update connection status
            idn = self.available_devices.get(resource, "Unknown device")
            self.connection_status_label.setText(f"● Connected: {idn[:35]}...")
            self.connection_status_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 11px; font-family: 'Segoe UI'; background: transparent;")
            
            self.statusBar().showMessage(f"Connected to {idn}", 3000)
            
            # Update display values immediately
            self.update_display_values()
            
        except Exception as e:
            self.connection_status_label.setText("● Connection failed")
            self.connection_status_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 11px; font-family: 'Segoe UI'; background: transparent;")
            QMessageBox.critical(self, "Connection Error", 
                               f"Failed to connect to device:\n{str(e)}")
            self.statusBar().showMessage(f"Connection failed: {str(e)}", 3000)
        finally:
            self.connect_device_button.setEnabled(True)

    def toggle_fm(self, state):
        """Toggle Frequency Modulation on/off"""
        enabled = state == Qt.Checked
        self.fm_params_widget.setEnabled(enabled)
        try:
            self.controller.set_fm_state(enabled)
            status = "enabled" if enabled else "disabled"
            self.statusBar().showMessage(f"FM {status}", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"Error toggling FM: {str(e)}", 3000)

    def toggle_am(self, state):
        """Toggle Amplitude Modulation on/off"""
        enabled = state == Qt.Checked
        self.am_params_widget.setEnabled(enabled)
        try:
            self.controller.set_am_state(enabled)
            status = "enabled" if enabled else "disabled"
            self.statusBar().showMessage(f"AM {status}", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"Error toggling AM: {str(e)}", 3000)

    def update_modulation_parameter(self, param_name, value):
        """Update a modulation parameter in the controller"""
        try:
            if param_name == 'fm_deviation':
                self.controller.set_fm_deviation(value)
            elif param_name == 'fm_frequency':
                self.controller.set_fm_frequency(value)
            elif param_name == 'fm_source':
                self.controller.set_fm_source(value)
            elif param_name == 'am_depth':
                self.controller.set_am_depth(value)
            elif param_name == 'am_frequency':
                self.controller.set_am_frequency(value)
            elif param_name == 'am_source':
                self.controller.set_am_source(value)
            
            self.statusBar().showMessage(f"Updated {param_name} to {value}", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"Error updating {param_name}: {str(e)}", 3000)