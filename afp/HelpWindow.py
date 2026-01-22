from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QTextBrowser, QPushButton
from PyQt5.QtGui import QFont
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


class HelpWindow(QDialog):
    """Help window with descriptions of all components for new users."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - ssRF/AFP Control Panel")
        self.setMinimumSize(700, 550)
        self.setModal(False)
        
        # Apply styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['card']};
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
                background-color: {COLORS['card']};
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['primary_light']};
                color: white;
            }}
            QTextBrowser {{
                background-color: {COLORS['card']};
                border: none;
                font-family: 'Segoe UI';
                font-size: 13px;
                line-height: 1.6;
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 8px;
                border: none;
                font-family: 'Segoe UI';
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
        """)
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Help & Documentation")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['dark']};")
        layout.addWidget(title)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Getting Started tab
        getting_started = QTextBrowser()
        getting_started.setOpenExternalLinks(True)
        getting_started.setHtml(self._get_getting_started_content())
        tabs.addTab(getting_started, "Getting Started")
        
        # Controller Parameters tab
        params_help = QTextBrowser()
        params_help.setHtml(self._get_parameters_content())
        tabs.addTab(params_help, "Controller Parameters")
        
        # Device & RF Control tab
        device_help = QTextBrowser()
        device_help.setHtml(self._get_device_rf_content())
        tabs.addTab(device_help, "Device & RF Control")
        
        # Modulation tab
        mod_help = QTextBrowser()
        mod_help.setHtml(self._get_modulation_content())
        tabs.addTab(mod_help, "Modulation")
        
        # Troubleshooting tab
        troubleshoot_help = QTextBrowser()
        troubleshoot_help.setHtml(self._get_troubleshooting_content())
        tabs.addTab(troubleshoot_help, "Troubleshooting")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setFixedWidth(120)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
    
    def _get_style_header(self):
        """Return common HTML styling for help content."""
        return f"""
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.7; color: {COLORS['dark']}; }}
            h2 {{ color: {COLORS['primary']}; border-bottom: 2px solid {COLORS['primary_light']}; padding-bottom: 8px; }}
            h3 {{ color: {COLORS['dark_light']}; margin-top: 20px; }}
            .param-name {{ 
                background-color: {COLORS['gray_lighter']}; 
                padding: 3px 8px; 
                border-radius: 4px; 
                font-weight: bold;
                color: {COLORS['dark']};
            }}
            .tip {{ 
                background-color: #e8f6ff; 
                border-left: 4px solid {COLORS['primary']}; 
                padding: 12px 15px; 
                margin: 15px 0;
                border-radius: 0 8px 8px 0;
            }}
            .warning {{ 
                background-color: #fff8e6; 
                border-left: 4px solid {COLORS['warning']}; 
                padding: 12px 15px; 
                margin: 15px 0;
                border-radius: 0 8px 8px 0;
            }}
            .danger {{ 
                background-color: #ffe8e6; 
                border-left: 4px solid {COLORS['danger']}; 
                padding: 12px 15px; 
                margin: 15px 0;
                border-radius: 0 8px 8px 0;
            }}
            ul {{ margin-left: 20px; }}
            li {{ margin-bottom: 8px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            th, td {{ border: 1px solid {COLORS['border']}; padding: 10px; text-align: left; }}
            th {{ background-color: {COLORS['gray_lighter']}; }}
        </style>
        """
    
    def _get_getting_started_content(self):
        return self._get_style_header() + """
        <h2>Welcome to ssRF/AFP Control Panel</h2>
        <p>This application allows you to control RF signal generators for semi-saturated RF and 
        Adiabatic Fast Passage (AFP) experiments. Follow these steps to get started:</p>
        
        <h3>Quick Start Guide</h3>
        <ol>
            <li><strong>Connect your device:</strong> Use the Device Selection panel to scan for 
            and connect to your RF signal generator.</li>
            <li><strong>Configure parameters:</strong> Set your desired frequency, power, and 
            sweep settings in the Controller Parameters panel.</li>
            <li><strong>Enable RF output:</strong> Click the "Turn On RF" button to start 
            generating the signal.</li>
            <li><strong>Apply modulation (optional):</strong> Enable FM or AM modulation if 
            needed for your experiment.</li>
        </ol>
        
        <div class="tip">
            <strong>Tip:</strong> The application automatically reads current device settings 
            every second. Values update in real-time unless you're actively editing a field.
        </div>
        
        <h3>Interface Overview</h3>
        <table>
            <tr>
                <th>Panel</th>
                <th>Purpose</th>
            </tr>
            <tr>
                <td><strong>Left Panel</strong></td>
                <td>Controller Parameters - Set frequency, power, and sweep settings</td>
            </tr>
            <tr>
                <td><strong>Right Panel (Top)</strong></td>
                <td>Device Selection - Connect to your signal generator</td>
            </tr>
            <tr>
                <td><strong>Right Panel (Middle)</strong></td>
                <td>RF Output Control - Turn RF signal on/off</td>
            </tr>
            <tr>
                <td><strong>Right Panel (Bottom)</strong></td>
                <td>Modulation - Configure FM and AM modulation</td>
            </tr>
        </table>
        
        <div class="warning">
            <strong>Note:</strong> Always verify your settings before enabling RF output, 
            especially power levels, to avoid equipment damage.
        </div>
        """
    
    def _get_parameters_content(self):
        return self._get_style_header() + """
        <h2>Controller Parameters</h2>
        <p>These parameters control the fundamental characteristics of the RF signal output.</p>
        
        <h3><span class="param-name">Center Frequency</span></h3>
        <p>The center frequency for sweep operations, specified in <strong>MHz</strong>.</p>
        <ul>
            <li>In CW mode: This value is not used</li>
            <li>In Sweep mode: The sweep is centered at this frequency</li>
            <li>The actual sweep range extends from (Center - Width/2) to (Center + Width/2)</li>
            <li>Range: 0 - 10,000 MHz (device dependent)</li>
        </ul>
        
        <h3><span class="param-name">Frequency Width</span></h3>
        <p>The total frequency width (bandwidth) for sweep operations, specified in <strong>MHz</strong>.</p>
        <ul>
            <li>In CW mode: This value is not used</li>
            <li>In Sweep mode: The sweep spans this width around the center frequency</li>
            <li>Start frequency = Center Frequency - Frequency Width / 2</li>
            <li>Stop frequency = Center Frequency + Frequency Width / 2</li>
            <li>Range: 0 - 10,000 MHz (device dependent)</li>
        </ul>
        
        <h3><span class="param-name">Spacing</span></h3>
        <p>Determines how frequency steps are distributed across the sweep range.</p>
        <ul>
            <li><strong>LINear:</strong> Equal frequency steps between points</li>
            <li><strong>LOGarithmic:</strong> Logarithmically spaced frequency steps</li>
        </ul>
        
        <h3><span class="param-name">Power</span></h3>
        <p>The output power level in <strong>dBm</strong> (decibels relative to 1 milliwatt).</p>
        <ul>
            <li>Range: -100 to +100 dBm (device dependent)</li>
            <li>Higher values = stronger signal output</li>
            <li>Typical lab values: -20 to +3 dBm</li>
        </ul>
        <div class="danger">
            <strong>Caution:</strong> High power levels can damage sensitive equipment or 
            cause RF interference. Always start with lower power and increase gradually.
        </div>
        
        <h3><span class="param-name">Mode</span></h3>
        <p>Selects the operating mode of the signal generator.</p>
        <ul>
            <li><strong>CW (Continuous Wave):</strong> Outputs a single, fixed frequency</li>
            <li><strong>Sweep:</strong> Automatically sweeps across the frequency width centered at the center frequency</li>
        </ul>
        
        <h3><span class="param-name">Sweep Points</span></h3>
        <p>Number of discrete frequency steps in a sweep operation.</p>
        <ul>
            <li>More points = smoother frequency transition, slower sweep</li>
            <li>Fewer points = faster sweep, larger frequency jumps</li>
            <li>Range: 1 - 500 points</li>
        </ul>
        
        <h3><span class="param-name">Sweep Dwell</span></h3>
        <p>Time spent at each frequency point during a sweep, in <strong>milliseconds</strong>.</p>
        <ul>
            <li>Total sweep time = Sweep Points x Dwell Time</li>
            <li>Longer dwell = more time for system response at each frequency</li>
        </ul>
        
        <div class="tip">
            <strong>Tip for AFP:</strong> For Adiabatic Fast Passage, typical settings involve 
            a sweep through the resonance frequency with appropriate dwell times to maintain 
            adiabatic conditions.
        </div>
        """
    
    def _get_device_rf_content(self):
        return self._get_style_header() + """
        <h2>Device Selection</h2>
        <p>Connect to and manage your RF signal generator hardware.</p>
        
        <h3>Scanning for Devices</h3>
        <ol>
            <li>Click the <strong>"Scan"</strong> button to search for connected instruments</li>
            <li>The application queries all VISA-compatible devices using *IDN? command</li>
            <li>Compatible devices appear in the dropdown with their identification string</li>
        </ol>
        
        <div class="tip">
            <strong>Tip:</strong> Ensure your device is powered on and properly connected 
            (USB, GPIB, or Ethernet) before scanning.
        </div>
        
        <h3>Connecting to a Device</h3>
        <ol>
            <li>Select your device from the dropdown menu</li>
            <li>Click <strong>"Connect"</strong></li>
            <li>The status indicator will show "Connected" when successful</li>
        </ol>
        
        <h3>Connection Status</h3>
        <table>
            <tr>
                <th>Status</th>
                <th>Meaning</th>
            </tr>
            <tr>
                <td style="color: #e74c3c;">● Not connected</td>
                <td>No device is currently connected</td>
            </tr>
            <tr>
                <td style="color: #27ae60;">● Connected</td>
                <td>Successfully connected to a device</td>
            </tr>
            <tr>
                <td style="color: #e74c3c;">● Connection failed</td>
                <td>Unable to establish connection - check device</td>
            </tr>
        </table>
        
        <hr>
        
        <h2>RF Output Control</h2>
        <p>Control the RF signal output from your device.</p>
        
        <h3>Turn On/Off RF Button</h3>
        <p>Toggles the RF output on or off. The button text changes to reflect the current action.</p>
        
        <h3>RF Status Indicator</h3>
        <table>
            <tr>
                <th>Color</th>
                <th>Status</th>
                <th>Meaning</th>
            </tr>
            <tr>
                <td style="background-color: #e74c3c; color: white; text-align: center;">Red</td>
                <td>RF: OFF</td>
                <td>No signal is being output</td>
            </tr>
            <tr>
                <td style="background-color: #27ae60; color: white; text-align: center;">Green</td>
                <td>RF: ON</td>
                <td>Signal is actively being output</td>
            </tr>
        </table>
        
        <div class="warning">
            <strong>Safety Note:</strong> Always be aware of the RF status. Unintended RF 
            output can interfere with other equipment or experiments.
        </div>
        """
    
    def _get_modulation_content(self):
        return self._get_style_header() + """
        <h2>Modulation</h2>
        <p>Apply frequency or amplitude modulation to your RF signal for advanced experiments.</p>
        
        <h3>Frequency Modulation (FM)</h3>
        <p>Varies the instantaneous frequency of the carrier signal.</p>
        
        <table>
            <tr>
                <th>Parameter</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><strong>Enable Checkbox</strong></td>
                <td>Turn FM on or off. Parameters are disabled when FM is off.</td>
            </tr>
            <tr>
                <td><strong>Deviation (kHz)</strong></td>
                <td>Maximum frequency shift from the carrier frequency. 
                Higher deviation = wider frequency swing.</td>
            </tr>
            <tr>
                <td><strong>Frequency (Hz)</strong></td>
                <td>Rate at which the frequency is modulated (modulation frequency). 
                This is how fast the frequency oscillates around the carrier.</td>
            </tr>
            <tr>
                <td><strong>Source</strong></td>
                <td><strong>INT:</strong> Use internal modulation generator<br>
                <strong>EXT:</strong> Use external modulation input</td>
            </tr>
        </table>
        
        <div class="tip">
            <strong>Example:</strong> With a 100 MHz carrier, 10 kHz deviation, and 1 kHz 
            modulation frequency, the output frequency will swing between 99.99 MHz and 
            100.01 MHz, completing 1000 cycles per second.
        </div>
        
        <hr>
        
        <h3>Amplitude Modulation (AM)</h3>
        <p>Varies the amplitude (power) of the carrier signal.</p>
        
        <table>
            <tr>
                <th>Parameter</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><strong>Enable Checkbox</strong></td>
                <td>Turn AM on or off. Parameters are disabled when AM is off.</td>
            </tr>
            <tr>
                <td><strong>Depth (%)</strong></td>
                <td>Percentage of amplitude variation. 
                100% = amplitude varies from 0 to 2x nominal.
                50% = amplitude varies from 0.5x to 1.5x nominal.</td>
            </tr>
            <tr>
                <td><strong>Frequency (Hz)</strong></td>
                <td>Rate at which the amplitude is modulated.</td>
            </tr>
            <tr>
                <td><strong>Source</strong></td>
                <td><strong>INT:</strong> Use internal modulation generator<br>
                <strong>EXT:</strong> Use external modulation input</td>
            </tr>
        </table>
        
        <div class="warning">
            <strong>Note:</strong> FM and AM can be enabled simultaneously for complex 
            modulation schemes, but ensure your device supports this combination.
        </div>
        """
    
    def _get_troubleshooting_content(self):
        return self._get_style_header() + """
        <h2>Troubleshooting</h2>
        <p>Common issues and their solutions.</p>
        
        <h3>No Devices Found</h3>
        <ul>
            <li>Ensure the device is powered on</li>
            <li>Check USB/GPIB/Ethernet cable connections</li>
            <li>Verify VISA drivers are installed (NI-VISA or R&S VISA)</li>
            <li>Try disconnecting and reconnecting the device</li>
            <li>Restart the application after reconnecting</li>
        </ul>
        
        <h3>Connection Failed</h3>
        <ul>
            <li>Another application may be using the device - close other control software</li>
            <li>The device may be in local mode - press "Remote" on the device front panel</li>
            <li>Check if the device responds to manual SCPI commands</li>
        </ul>
        
        <h3>Parameters Not Updating</h3>
        <ul>
            <li>Verify the device is still connected (check status indicator)</li>
            <li>Some parameters may be locked depending on device mode</li>
            <li>Check the status bar for error messages</li>
        </ul>
        
        <h3>RF Won't Turn On</h3>
        <ul>
            <li>Check for interlock or safety conditions on the device</li>
            <li>Verify output power is within device limits</li>
            <li>Some devices require specific frequency settings before enabling output</li>
        </ul>
        
        <h3>Sweep Not Working</h3>
        <ul>
            <li>Ensure Mode is set to "Sweep" not "CW"</li>
            <li>Verify Frequency Width is greater than zero</li>
            <li>Check that sweep points and dwell time are set appropriately</li>
        </ul>
        
        <div class="tip">
            <strong>Getting More Help:</strong> Check the device manufacturer's documentation 
            for device-specific limitations and SCPI command references.
        </div>
        
        <h3>Keyboard Shortcuts</h3>
        <table>
            <tr>
                <th>Shortcut</th>
                <th>Action</th>
            </tr>
            <tr>
                <td>Ctrl+Z</td>
                <td>Undo</td>
            </tr>
            <tr>
                <td>Ctrl+Y</td>
                <td>Redo</td>
            </tr>
            <tr>
                <td>F1</td>
                <td>Open this Help window</td>
            </tr>
        </table>
        """