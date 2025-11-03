"""
Connection status window for NanoVNA devices.
"""
import os
import sys
import logging
import numpy as np
import skrf as rf
from PySide6.QtCore import QTimer, QThread, Qt, QSettings
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton,
    QHBoxLayout, QProgressBar, QFrame, QGridLayout, QGroupBox, QComboBox,
    QGraphicsScene, QGraphicsView, QSizePolicy, QSlider, QLabel
)
from PySide6.QtGui import QIcon, QTextCursor, QFont, QPen

from ..workers.device_worker import DeviceWorker
from .log_handler import GuiLogHandler

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

try:
    from NanoVNA_UTN_Toolkit.ui.welcome_windows import NanoVNAWelcome
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

class NanoVNAStatusApp(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "ui","graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        # QWidget
        background_color = settings.value("Dark_Light/QWidget/background-color", "#3a3a3a")

        # Qframe
        qframe_color = settings.value("Dark_Light/Qframe/background-color", "white")

        # QTabWidget pane
        tabwidget_pane_bg = settings.value("Dark_Light/QTabWidget_pane/background-color", "#3b3b3b")

        # QTabBar
        tabbar_bg = settings.value("Dark_Light/QTabBar/background-color", "#2b2b2b")
        tabbar_color = settings.value("Dark_Light/QTabBar/color", "white")
        tabbar_padding = settings.value("Dark_Light/QTabBar/padding", "5px 12px")
        tabbar_border = settings.value("Dark_Light/QTabBar/border", "none")
        tabbar_border_tl_radius = settings.value("Dark_Light/QTabBar/border-top-left-radius", "6px")
        tabbar_border_tr_radius = settings.value("Dark_Light/QTabBar/border-top-right-radius", "6px")

        # QTabBar selected
        tabbar_selected_bg = settings.value("Dark_Light/QTabBar_selected/background-color", "#4d4d4d")
        tabbar_selected_color = settings.value("Dark_Light/QTabBar/color", "white")

        # QSpinBox
        spinbox_bg = settings.value("Dark_Light/QSpinBox/background-color", "#3b3b3b")
        spinbox_color = settings.value("Dark_Light/QSpinBox/color", "white")
        spinbox_border = settings.value("Dark_Light/QSpinBox/border", "1px solid white")
        spinbox_border_radius = settings.value("Dark_Light/QSpinBox/border-radius", "8px")

        # QGroupBox title
        groupbox_title_color = settings.value("Dark_Light/QGroupBox_title/color", "white")

        # QLabel
        label_color = settings.value("Dark_Light/QLabel/color", "white")

        # QLineEdit
        lineedit_bg = settings.value("Dark_Light/QLineEdit/background-color", "#3b3b3b")
        lineedit_color = settings.value("Dark_Light/QLineEdit/color", "white")
        lineedit_border = settings.value("Dark_Light/QLineEdit/border", "1px solid white")
        lineedit_border_radius = settings.value("Dark_Light/QLineEdit/border-radius", "6px")
        lineedit_padding = settings.value("Dark_Light/QLineEdit/padding", "4px")
        lineedit_focus_bg = settings.value("Dark_Light/QLineEdit_focus/background-color", "#454545")
        lineedit_focus_border = settings.value("Dark_Light/QLineEdit_focus/border", "1px solid #4d90fe")

        # QPushButton
        pushbutton_bg = settings.value("Dark_Light/QPushButton/background-color", "#3b3b3b")
        pushbutton_color = settings.value("Dark_Light/QPushButton/color", "white")
        pushbutton_border = settings.value("Dark_Light/QPushButton/border", "1px solid white")
        pushbutton_border_radius = settings.value("Dark_Light/QPushButton/border-radius", "6px")
        pushbutton_padding = settings.value("Dark_Light/QPushButton/padding", "4px 10px")
        pushbutton_hover_bg = settings.value("Dark_Light/QPushButton_hover/background-color", "#4d4d4d")
        pushbutton_pressed_bg = settings.value("Dark_Light/QPushButton_pressed/background-color", "#5c5c5c")
        pushbutton_disabled_bg = settings.value("Dark_Light/QPushButton_disabled/background-color", "#2a2a2a")
        pushbutton_disabled_color = settings.value("Dark_Light/QPushButton_disabled/color", "#666666")
        pushbutton_disabled_border = settings.value("Dark_Light/QPushButton_disabled/border", "1px solid #444444")

        # QMenu
        menu_bg = settings.value("Dark_Light/QMenu/background", "#3a3a3a")
        menu_color = settings.value("Dark_Light/QMenu/color", "white")
        menu_border = settings.value("Dark_Light/QMenu/border", "1px solid #3b3b3b")
        menu_item_selected_bg = settings.value("Dark_Light/QMenu::item:selected/background-color", "#4d4d4d")

        # QMenuBar
        menu_item_color = settings.value("Dark_Light/QMenu_item_selected/background-color", "4d4d4d")
        menubar_bg = settings.value("Dark_Light/QMenuBar/background-color", "#3a3a3a")
        menubar_color = settings.value("Dark_Light/QMenuBar/color", "white")
        menubar_item_bg = settings.value("Dark_Light/QMenuBar_item/background", "transparent")
        menubar_item_color = settings.value("Dark_Light/QMenuBar_item/color", "white")
        menubar_item_padding = settings.value("Dark_Light/QMenuBar_item/padding", "4px 10px")
        menubar_item_selected_bg = settings.value("Dark_Light/QMenuBar_item_selected/background-color", "#4d4d4d")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
            }}
            QTabWidget::pane {{
                background-color: {tabwidget_pane_bg}; 
            }}
            QTabBar::tab {{
                background-color: {tabbar_bg}; 
                color: {tabbar_color};
                padding: {tabbar_padding};
                border: {tabbar_border}; 
                border-top-left-radius: {tabbar_border_tl_radius};
                border-top-right-radius: {tabbar_border_tr_radius};
            }}
            QTabBar::tab:selected {{
                background-color: {tabbar_selected_bg};  
                color: {tabbar_selected_color};
            }}
            QSpinBox {{
                background-color: {spinbox_bg};
                color: {spinbox_color};
                border: {spinbox_border};
                border-radius: {spinbox_border_radius};
            }}
            QGroupBox:title {{
                color: {groupbox_title_color};  
            }}
            QLabel {{
                color: {label_color};  
            }}
            QTextEdit {{
                color: {label_color};  
            }}
            QFrame{{
                border-radius: 5px;
            }}
            QLineEdit {{
                background-color: {lineedit_bg};
                color: {lineedit_color};
                border: {lineedit_border};
                border-radius: {lineedit_border_radius};
                padding: {lineedit_padding};
            }}
            QLineEdit:focus {{
                background-color: {lineedit_focus_bg};
                border: {lineedit_focus_border};
            }}
            QPushButton {{
                background-color: {pushbutton_bg};
                color: {pushbutton_color};
                border: {pushbutton_border};
                border-radius: {pushbutton_border_radius};
                padding: {pushbutton_padding};
            }}
            QPushButton:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {pushbutton_pressed_bg};
            }}
            QPushButton:disabled {{
                background-color: {pushbutton_disabled_bg};
                color: {pushbutton_disabled_color};
                border: {pushbutton_disabled_border};
            }}
            QMenuBar {{
                background-color: {menubar_bg};
                color: {menubar_color};
            }}
            QMenuBar::item {{
                background: {menubar_item_bg};
                color: {menubar_item_color};
                padding: {menubar_item_padding};
            }}
            QMenuBar::item:selected {{
                background: {menubar_item_selected_bg};
            }}
            QMenu {{
                background-color: {menu_bg};
                color: {menu_color};
                border: {menu_border};
            }}
            QMenu::item:selected {{
                background-color: {menu_item_color};
            }}
        """)

        self.vna = None
        self.is_checking = False
        self.worker = None
        self.worker_thread = None
        
        self.init_ui(qframe_color=qframe_color)
        self.setup_hardware_logging()
        
        # Start initial device check
        QTimer.singleShot(1000, self.start_device_check)
        
        # Log initial message
        self.log_message("Application started. Preparing device detection...")
    
    def init_ui(self, qframe_color):
        """Initialize the user interface."""
        # Try to set application icon
        icon_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'icon.ico'),
            'icon.ico'
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break
        else:
            logger = logging.getLogger(__name__)
            logger.warning("icon.ico not found in expected locations")
            
        self.setWindowTitle("NanoVNA UTN Toolkit - Connection Window")
        self.setGeometry(100, 100, 900, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Status section
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_frame.setFrameStyle(QFrame.Shape.Box)

        status_frame.setStyleSheet(f"""
            QFrame#statusFrame {{
                border: 1px solid {qframe_color};
            }}
        """)

        status_layout = QVBoxLayout(status_frame)
        
        # Connection status label
        self.status_label = QLabel("Status: Starting...")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: orange; padding: 10px;")
        status_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        status_layout.addWidget(self.progress_bar)
        
        # Current operation label
        self.operation_label = QLabel("Preparing system...")
        self.operation_label.setStyleSheet("font-size: 12px; padding: 5px;")
        status_layout.addWidget(self.operation_label)
        
        layout.addWidget(status_frame)
        
        # Device information section
        self.device_group = QGroupBox("Device Information")
        
        device_layout = QGridLayout(self.device_group)
        
        # Create labels for device information
        self.board_label = QLabel("Board:")
        self.board_value = QLabel("Not detected")
        self.version_label = QLabel("Version:")
        self.version_value = QLabel("Unknown")
        self.build_time_label = QLabel("Build Time:")
        self.build_time_value = QLabel("Unknown")
        self.arch_label = QLabel("Architecture:")
        self.arch_value = QLabel("Unknown")
        self.platform_label = QLabel("Platform:")
        self.platform_value = QLabel("Unknown")
        
        # Extended device information
        self.serial_label = QLabel("Serial Number:")
        self.serial_value = QLabel("Not available")
        self.device_type_label = QLabel("Device Type:")
        self.device_type_value = QLabel("Unknown")
        
        # Parameters section
        self.params_label = QLabel("Parameters:")
        self.params_value = QLabel("Not available")
        
        # Features section
        self.features_label = QLabel("Features:")
        self.features_value = QLabel("Not available")
        
        # Style the labels
        label_style = "font-weight: bold;"
        value_style = "padding-left: 10px;"
        
        for label in [self.board_label, self.version_label, self.build_time_label, 
                     self.arch_label, self.platform_label, self.serial_label, 
                     self.device_type_label, self.params_label, self.features_label]:
            label.setStyleSheet(label_style)
        
        for value in [self.board_value, self.version_value, self.build_time_value,
                     self.arch_value, self.platform_value, self.serial_value,
                     self.device_type_value, self.params_value, self.features_value]:
            value.setStyleSheet(value_style)
        
        # Add to grid layout
        device_layout.addWidget(self.board_label, 0, 0)
        device_layout.addWidget(self.board_value, 0, 1)
        device_layout.addWidget(self.version_label, 1, 0)
        device_layout.addWidget(self.version_value, 1, 1)
        device_layout.addWidget(self.device_type_label, 2, 0)
        device_layout.addWidget(self.device_type_value, 2, 1)
        device_layout.addWidget(self.serial_label, 3, 0)
        device_layout.addWidget(self.serial_value, 3, 1)
        device_layout.addWidget(self.platform_label, 4, 0)
        device_layout.addWidget(self.platform_value, 4, 1)
        device_layout.addWidget(self.arch_label, 5, 0)
        device_layout.addWidget(self.arch_value, 5, 1)
        device_layout.addWidget(self.build_time_label, 6, 0)
        device_layout.addWidget(self.build_time_value, 6, 1)
        device_layout.addWidget(self.params_label, 7, 0)
        device_layout.addWidget(self.params_value, 7, 1)
        device_layout.addWidget(self.features_label, 8, 0)
        device_layout.addWidget(self.features_value, 8, 1)
        
        layout.addWidget(self.device_group)
        
        # Console output section
        console_label = QLabel("LOGS:")
        console_label.setStyleSheet("font-weight: bold; margin-top: 10px; font-size: 14px;")
        layout.addWidget(console_label)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Courier", 9))
        self.console.setMaximumHeight(200)
        self.console.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {qframe_color};
            }}
        """)
        layout.addWidget(self.console)
        
        # Buttons section
        button_layout = QHBoxLayout()
        
        # Layout horizontal para los primeros botones
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.manual_refresh)
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setStyleSheet("padding: 8px 16px; font-size: 12px;")
        button_layout.addWidget(self.refresh_btn)

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.manual_disconnect)
        self.disconnect_btn.setEnabled(False)  # Initially disabled
        self.disconnect_btn.setStyleSheet("padding: 8px 16px; font-size: 12px;")
        button_layout.addWidget(self.disconnect_btn)

        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.console.clear)
        clear_btn.setStyleSheet("padding: 8px 16px; font-size: 12px;")
        button_layout.addWidget(clear_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_detection)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("padding: 8px 16px; font-size: 12px;")
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

        self.smith_btn = QPushButton("Open Welcome Window")
        self.smith_btn.clicked.connect(self.open_welcome_window)
        self.stop_btn.setEnabled(False)
        self.smith_btn.setStyleSheet("padding: 12px; font-size: 14px;")
        layout.addWidget(self.smith_btn)

        # Show window
        self.show()
    
    def setup_hardware_logging(self):
        """Setup custom logging handler to capture important hardware logs."""
        handler = GuiLogHandler(self)
        handler.setLevel(logging.DEBUG)
        
        # Add handler to VNA logger
        vna_logger = logging.getLogger('NanoVNA_UTN_Toolkit.Hardware.VNA')
        vna_logger.addHandler(handler)
    
    def update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)
    
    def update_operation_status(self, status):
        """Update operation status label."""
        self.operation_label.setText(status)
    
    def update_device_info(self, device_info):
        """Update device information display."""
        self.board_value.setText(device_info.get('board', 'Unknown'))
        self.version_value.setText(device_info.get('version', 'Unknown'))
        self.build_time_value.setText(device_info.get('build_time', 'Unknown'))
        self.arch_value.setText(device_info.get('architecture', 'Unknown'))
        self.platform_value.setText(device_info.get('platform', 'Unknown'))
        
        # Extended device information
        self.serial_value.setText(device_info.get('serial_number', 'Not available'))
        self.device_type_value.setText(device_info.get('device_type', 'Unknown'))
        
        # Handle parameters
        params = device_info.get('parameters', {})
        if params:
            param_labels = {
                'p': 'Points',
                'IF': 'IF Frequency',
                'ADC': 'ADC Rate',
                'Lcd': 'LCD Resolution'
            }
            
            param_text = ""
            for key, value in params.items():
                label = param_labels.get(key, key)
                param_text += f"• {label}: {value}\n"
            self.params_value.setText(param_text.strip())
        else:
            self.params_value.setText("Not available")
        
        # Handle features
        features = device_info.get('features', [])
        if features:
            # Show only the most relevant features for the UI
            important_features = []
            for feature in features:
                if any(keyword in feature.lower() for keyword in ['customizable', 'screenshot', 'sn', 'bandwidth', 'average', 'power']):
                    important_features.append(feature)
            
            if important_features:
                features_text = "• " + "\n• ".join(important_features[:5])  # Limit to 5 most important
                if len(features) > 5:
                    features_text += f"\n• ... and {len(features) - 5} more"
                self.features_value.setText(features_text)
            else:
                self.features_value.setText(f"{len(features)} features available")
        else:
            self.features_value.setText("Not available")
    
    def clear_device_info(self):
        """Clear the device information display."""
        self.board_value.setText("Not detected")
        self.version_value.setText("Unknown")
        self.build_time_value.setText("Unknown")
        self.arch_value.setText("Unknown")
        self.platform_value.setText("Unknown")
        self.serial_value.setText("Not available")
        self.device_type_value.setText("Unknown")
        self.params_value.setText("Not available")
        self.features_value.setText("Not available")
    
    def log_message(self, message):
        """Add a message to the console output."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.console.append(formatted_message)
        # Move cursor to end
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.console.setTextCursor(cursor)
        logging.getLogger(__name__).info(message)
    
    def start_device_check(self):
        """Start device detection in a separate thread."""
        if self.is_checking:
            self.log_message("Device search is already running")
            return
            
        self.is_checking = True
        self.refresh_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Clear previous device info
        self.clear_device_info()
        
        # Clean up previous thread if exists (non-blocking)
        if self.worker_thread and self.worker_thread.isRunning():
            self.log_message("Stopping previous search...")
            if self.worker:
                self.worker.stop()
            # Use non-blocking cleanup with signal connection
            self.worker_thread.finished.connect(self._start_new_detection)
            self.worker_thread.quit()
            return  # Exit here, _start_new_detection will be called when thread finishes
        
        # Start new detection immediately if no previous thread
        self._start_new_detection()
    
    def _start_new_detection(self):
        """Internal method to start new detection after cleanup."""
        # Disconnect the signal to prevent multiple connections
        if self.worker_thread:
            try:
                self.worker_thread.finished.disconnect(self._start_new_detection)
            except RuntimeError:
                pass  # Signal was not connected, ignore error
        
        # Create worker thread
        self.worker_thread = QThread()
        self.worker = DeviceWorker()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.status_update.connect(self.update_operation_status)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.device_found.connect(self.on_device_found)
        self.worker.device_error.connect(self.on_device_error)
        self.worker.finished.connect(self.on_detection_finished)
        
        # Connect thread signals
        self.worker_thread.started.connect(self.worker.detect_devices)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # Start the thread
        self.worker_thread.start()
        self.log_message("Starting device search in background...")
    
    def stop_detection(self):
        """Stop the current detection process."""
        if self.worker:
            self.worker.stop()
            self.log_message("Stopping device search...")

    def open_welcome_window(self):
        """Open the welcome window."""
        # Log device transfer to welcome window
        if self.vna:
            device_type = type(self.vna).__name__
            self.log_message(f"[connection_window.open_welcome_window] Device {device_type} available - passing to welcome window")
            self.welcome_windows = NanoVNAWelcome(vna_device=self.vna)
        else:
            self.log_message("[connection_window.open_welcome_window] No device connected - using placeholder mode")
            self.welcome_windows = NanoVNAWelcome()
            
        self.welcome_windows.show()
        self.close() 

    def manual_refresh(self):
        """Manual refresh button handler."""
        self.log_message("Manual refresh requested")
        self.start_device_check()
    
    def manual_disconnect(self):
        """Manual disconnect button handler."""
        if self.vna:
            try:
                if hasattr(self.vna, 'disconnect'):
                    self.vna.disconnect()
                self.log_message("Device disconnected manually")
            except Exception as e:
                self.log_message(f"Error disconnecting: {str(e)}")
            finally:
                self.vna = None
                self.status_label.setText("Status: Disconnected")
                self.status_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold; padding: 10px;")
                self.clear_device_info()
                self.disconnect_btn.setEnabled(False)
    
    def on_device_found(self, vna, device_info):
        """Handle successful device detection."""
        self.vna = vna
        self.status_label.setText("Status: Connected")
        self.status_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold; padding: 10px;")
        
        # Update device information display
        self.update_device_info(device_info)
        
        # Enable disconnect button
        self.disconnect_btn.setEnabled(True)
        
        # Enhanced logging for device detection
        board = device_info.get('board', 'Unknown')
        version = device_info.get('version', 'Unknown')
        device_type = type(vna).__name__ if vna else 'Unknown'
        
        self.log_message(f"[connection_window.on_device_found] Device connected: {board} (Type: {device_type})")
        self.log_message(f"Device Details - Version: {version}")
        
        # Log device capabilities if available
        if hasattr(vna, 'sweep_points_min') and hasattr(vna, 'sweep_points_max'):
            self.log_message(f"Sweep Points Range: {vna.sweep_points_min} - {vna.sweep_points_max}")
        
        # Log device attributes for debugging
        self.log_message(f"Device Object: {device_type}")
        self.log_message(f"Device Attributes: {[attr for attr in dir(vna) if not attr.startswith('_')][:10]}...")
        
        self.log_message("Connection successful - Automatic search paused")
        
        # Log full device info if available
        if device_info.get('full_text'):
            self.log_message("Complete device information:")
            for line in device_info['full_text'].split('\n'):
                if line.strip():
                    self.log_message(f"   {line.strip()}")
    
    def on_device_error(self, error_msg):
        """Handle device detection errors."""
        self.status_label.setText("Status: Disconnected")
        self.status_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold; padding: 10px;")
        self.clear_device_info()
        self.log_message(f"{error_msg}")
        
        # Disable disconnect button
        self.disconnect_btn.setEnabled(False)
        
        # Clean up VNA connection
        if self.vna:
            try:
                if hasattr(self.vna, 'disconnect'):
                    self.vna.disconnect()
            except:
                pass
            self.vna = None  # Clear the VNA reference so periodic checks can resume
    
    def on_detection_finished(self):
        """Handle detection process completion."""
        self.is_checking = False
        self.refresh_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        
        # Clean up thread properly
        if self.worker_thread:
            # Ensure thread completes and is cleaned up
            if self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait(2000)  # Wait up to 2 seconds
            self.worker_thread = None
        
        # Clear worker reference
        if self.worker:
            self.worker = None
    
    def closeEvent(self, event):
        """Handle application close event."""
        logger = logging.getLogger(__name__)
        logger.info("Application closing - cleaning up resources...")
        
        # Stop worker if running
        if self.worker:
            logger.debug("Stopping worker...")
            self.worker.stop()
        
        # Clean up VNA connection
        if self.vna:
            logger.debug("Disconnecting VNA...")
            try:
                if hasattr(self.vna, 'disconnect'):
                    self.vna.disconnect()
                elif hasattr(self.vna, 'close'):
                    self.vna.close()
            except Exception as e:
                logger.debug(f"Error disconnecting VNA: {e}")
        
        # Wait for thread to finish properly
        if self.worker_thread and self.worker_thread.isRunning():
            logger.debug("Waiting for worker thread to finish...")
            self.worker_thread.quit()
            if not self.worker_thread.wait(5000):  # Wait up to 5 seconds
                logger.warning("Thread did not finish gracefully, forcing termination")
                self.worker_thread.terminate()
                self.worker_thread.wait(1000)  # Wait 1 more second after terminate
        
        logger.info("Application cleanup completed")
        event.accept()
