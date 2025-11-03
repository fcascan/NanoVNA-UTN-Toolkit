"""
Sweep Options window for NanoVNA devices.
Allows configuration of frequency start/stop, segments, and displays calculated values.
"""
import os
import sys
import logging
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QGroupBox, QGridLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox, QFormLayout,
    QApplication, QMessageBox, QComboBox
)
from PySide6.QtGui import QIcon, QDoubleValidator, QFont


class SweepOptionsWindow(QMainWindow):
    def __init__(self, parent: "NanoVNAGraphics", vna_device=None):
        super().__init__(parent)

        self.last_start_value = 50   
        self.last_stop_value  = 1.5 

        self.main_window = parent

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

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
                padding: 4px;
                min-height: 20px;
            }}
            QSpinBox::up-button {{
                background-color: {spinbox_bg};
                border: {spinbox_border};
                border-radius: 3px;
                width: 18px;
                min-height: 12px;
            }}
            QSpinBox::down-button {{
                background-color: {spinbox_bg};
                border: {spinbox_border};
                border-radius: 3px;
                width: 18px;
                min-height: 12px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QSpinBox::up-button {{
                background-color: {spinbox_bg};
                border: {spinbox_border};
                border-radius: 3px;
                width: 18px;
                min-height: 12px;
            }}
            QSpinBox::down-button {{
                background-color: {spinbox_bg};
                border: {spinbox_border};
                border-radius: 3px;
                width: 18px;
                min-height: 12px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QSpinBox::up-arrow {{
                image: none;
                border-left: 2px solid transparent;
                border-right: 2px solid transparent;
                border-bottom: 3px solid {spinbox_color};
                width: 0px;
                height: 0px;
            }}
            QSpinBox::down-arrow {{
                image: none;
                border-left: 2px solid transparent;
                border-right: 2px solid transparent;
                border-top: 3px solid {spinbox_color};
                width: 0px;
                height: 0px;
            }}
            QDoubleSpinBox {{
                background-color: {spinbox_bg};
                color: {spinbox_color};
                border: {spinbox_border};
                border-radius: {spinbox_border_radius};
                padding: 4px;
                min-height: 20px;
            }}
            QDoubleSpinBox::up-button {{
                background-color: {spinbox_bg};
                border: {spinbox_border};
                border-radius: 3px;
                width: 18px;
                min-height: 12px;
            }}
            QDoubleSpinBox::down-button {{
                background-color: {spinbox_bg};
                border: {spinbox_border};
                border-radius: 3px;
                width: 18px;
                min-height: 12px;
            }}
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QDoubleSpinBox::up-arrow {{
                image: none;
                border-left: 2px solid transparent;
                border-right: 2px solid transparent;
                border-bottom: 3px solid {spinbox_color};
                width: 0px;
                height: 0px;
            }}
            QDoubleSpinBox::down-arrow {{
                image: none;
                border-left: 2px solid transparent;
                border-right: 2px solid transparent;
                border-top: 3px solid {spinbox_color};
                width: 0px;
                height: 0px;
            }}
            QComboBox {{
                background-color: {spinbox_bg};
                color: {spinbox_color};
                border: {spinbox_border};
                border-radius: {spinbox_border_radius};
                padding: 4px 8px;
                min-height: 20px;
                min-width: 60px;
            }}
            QComboBox::drop-down {{
                background-color: {spinbox_bg};
                border: none;
                border-left: 1px solid {spinbox_color};
                width: 20px;
                border-radius: 3px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 2px solid transparent;
                border-right: 2px solid transparent;
                border-top: 3px solid {spinbox_color};
                width: 0px;
                height: 0px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {spinbox_bg};
                color: {spinbox_color};
                border: {spinbox_border};
                selection-background-color: {pushbutton_hover_bg};
                selection-color: {spinbox_color};
            }}
            QComboBox:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QComboBox:focus {{
                border: 1px solid #4d90fe;
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
        
        # Store VNA device reference
        self.vna_device = vna_device
        
        # Log sweep options window initialization
        logging.info("[sweep_options_window.__init__] Initializing sweep options window")
        if vna_device:
            device_type = type(vna_device).__name__
            logging.info(f"[sweep_options_window.__init__] VNA device provided: {device_type}")
            if hasattr(vna_device, 'sweep_points_min') and hasattr(vna_device, 'sweep_points_max'):
                logging.info(f"[sweep_options_window.__init__] Device sweep limits: {vna_device.sweep_points_min} to {vna_device.sweep_points_max}")
            else:
                logging.warning(f"[sweep_options_window.__init__] Device {device_type} has no sweep_points_min/max attributes")
                logging.warning(f"[sweep_options_window.__init__] Available device attributes: {[attr for attr in dir(vna_device) if not attr.startswith('_')][:10]}...")
        else:
            logging.warning("[sweep_options_window.__init__] No VNA device provided - using default limits")
        
        # Path to config.ini
        actual_dir = os.path.dirname(os.path.dirname(__file__))
        self.config_dir = os.path.join(actual_dir, "sweep_window", "config")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_path = os.path.join(self.config_dir, "config.ini")
        
        self.settings = QSettings(self.config_path, QSettings.Format.IniFormat)
        
        # Load maximum frequency limit from config
        self.max_frequency_hz = self.load_max_frequency()
        
        # Get sweep points limits from VNA device
        self.sweep_points_min, self.sweep_points_max = self.get_sweep_points_limits()
        
        # Store original values for cancel functionality
        self.original_values = {}
        
        self.init_ui()
        self.load_settings()
        self.store_original_values()  # Store values after loading
        self.calculate_derived_values()
        
    def load_max_frequency(self):
        """Load maximum frequency limit from config.ini file."""
        default_max_freq = 6e9  # 6 GHz default
        max_freq_val = self.settings.value("Limits/MaxFrequencyHz", default_max_freq)
        try:
            return float(str(max_freq_val)) if max_freq_val is not None else default_max_freq
        except (ValueError, TypeError):
            return default_max_freq
            
    def get_sweep_points_limits(self):
        """Get sweep points min and max from VNA device or use defaults."""
        default_min = 11
        default_max = 1001
        
        logging.info("[sweep_options_window.get_sweep_points_limits] Getting sweep points limits")
        
        if self.vna_device:
            device_type = type(self.vna_device).__name__
            logging.info(f"[sweep_options_window.get_sweep_points_limits] Checking device {device_type} for limits")
            
            try:
                # Try to get limits from the connected VNA device
                if hasattr(self.vna_device, 'sweep_points_min'):
                    sweep_min = getattr(self.vna_device, 'sweep_points_min', default_min)
                    logging.info(f"[sweep_options_window.get_sweep_points_limits] Device min found: {sweep_min}")
                else:
                    sweep_min = default_min
                    logging.warning(f"[sweep_options_window.get_sweep_points_limits] Device has no sweep_points_min, using default: {default_min}")
                    
                if hasattr(self.vna_device, 'sweep_points_max'):
                    sweep_max = getattr(self.vna_device, 'sweep_points_max', default_max)
                    logging.info(f"[sweep_options_window.get_sweep_points_limits] Device max found: {sweep_max}")
                else:
                    sweep_max = default_max
                    logging.warning(f"[sweep_options_window.get_sweep_points_limits] Device has no sweep_points_max, using default: {default_max}")
                
                logging.info(f"[sweep_options_window.get_sweep_points_limits] Final device limits: {sweep_min} - {sweep_max}")
                return int(sweep_min), int(sweep_max)
            except (AttributeError, ValueError, TypeError) as e:
                logging.error(f"[sweep_options_window.get_sweep_points_limits] Error getting device limits: {e}")
        else:
            logging.warning("[sweep_options_window.get_sweep_points_limits] No VNA device available")
        
        # Fallback to defaults if no device or device doesn't have limits
        logging.info(f"[sweep_options_window.get_sweep_points_limits] Using default limits: {default_min} - {default_max}")
        return default_min, default_max

    from PySide6.QtWidgets import QToolTip

    def on_frequency_changed_range(self):
        start_val_hz = self.start_freq_edit.value() * self.unit_multiplier(self.start_freq_unit.currentText())
        stop_val_hz = self.stop_freq_edit.value() * self.unit_multiplier(self.stop_freq_unit.currentText())

        # Start Frequency check
        if not (50_000 <= start_val_hz <= 1_500_000_000):
            self.start_freq_edit.blockSignals(True)
            self.start_freq_edit.setValue(self.last_start_value)
            self.start_freq_edit.blockSignals(False)
            QToolTip.showText(
                self.start_freq_edit.mapToGlobal(self.start_freq_edit.rect().topRight()),
                "Start frequency must be between 50 kHz and 1.5 GHz"
            )
        else:
            self.last_start_value = self.start_freq_edit.value()

        # Stop Frequency check
        if not (50_000 <= stop_val_hz <= 1_500_000_000):
            self.stop_freq_edit.blockSignals(True)
            self.stop_freq_edit.setValue(self.last_stop_value)
            self.stop_freq_edit.blockSignals(False)
            QToolTip.showText(
                self.stop_freq_edit.mapToGlobal(self.stop_freq_edit.rect().topRight()),
                "Stop frequency must be between 50 kHz and 1.5 GHz"
            )
        else:
            self.last_stop_value = self.stop_freq_edit.value()

    def update_spinbox_range(self, spinbox, unit):
        """Actualiza el rango del spinbox según la unidad actual."""
        if unit == "Hz":
            spinbox.setRange(50_000, 1_500_000_000)
        elif unit == "kHz":
            spinbox.setRange(50, 1_500_000)
        elif unit == "MHz":
            spinbox.setRange(0.05, 1500)
        elif unit == "GHz":
            spinbox.setRange(0.00005, 1.5)

    def unit_multiplier(self, unit):
        return {"Hz": 1, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}[unit]

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("NanoVNA UTN Toolkit - Sweep Options")
        self.setGeometry(200, 200, 400, 300)
        
        # Set window icon
        icon_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'icon.ico'),
            os.path.join(os.path.dirname(__file__), 'icon.ico'),
            'icon.ico'
        ]
        for icon_path in icon_paths:
            icon_path = os.path.abspath(icon_path)
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Frequency Configuration Group
        freq_group = QGroupBox("Frequency Configuration")
        freq_layout = QFormLayout(freq_group)
        
        # Start Frequency with unit selector
        start_freq_layout = QHBoxLayout()
        self.start_freq_edit = QDoubleSpinBox()
        self.start_freq_edit.setRange(50, 1500000000) 
        self.start_freq_edit.setDecimals(3)
        self.start_freq_edit.valueChanged.connect(self.on_frequency_changed)
    
        self.start_freq_unit = QComboBox()
        self.start_freq_unit.addItems(["Hz", "kHz", "MHz", "GHz"])
        self.start_freq_unit.setCurrentText("kHz")
        self.start_freq_unit.currentTextChanged.connect(self.on_frequency_changed)

        self.start_freq_unit.currentTextChanged.connect(
            lambda unit: self.update_spinbox_range(self.start_freq_edit, unit)
        )

        self.update_spinbox_range(self.start_freq_edit, self.start_freq_unit.currentText())

        start_freq_layout.addWidget(self.start_freq_edit)
        start_freq_layout.addWidget(self.start_freq_unit)
        freq_layout.addRow("Start Frequency:", start_freq_layout)
        
        # Stop Frequency with unit selector and max frequency validation
        stop_freq_layout = QHBoxLayout()
        self.stop_freq_edit = QDoubleSpinBox()
        self.stop_freq_edit.setRange(50, 1500000000) 
        self.stop_freq_edit.setDecimals(3)
        self.stop_freq_edit.valueChanged.connect(self.on_frequency_changed)

        self.stop_freq_unit = QComboBox()
        self.stop_freq_unit.addItems(["Hz", "kHz", "MHz", "GHz"])
        self.stop_freq_unit.setCurrentText("GHz")
        self.stop_freq_unit.currentTextChanged.connect(self.on_frequency_changed)
        self.stop_freq_unit.currentTextChanged.connect(self.on_frequency_changed_range)

        self.stop_freq_unit.currentTextChanged.connect(
            lambda unit: self.update_spinbox_range(self.stop_freq_edit, unit)
        )

        self.update_spinbox_range(self.stop_freq_edit, self.stop_freq_unit.currentText())
        
        stop_freq_layout.addWidget(self.stop_freq_edit)
        stop_freq_layout.addWidget(self.stop_freq_unit)
        freq_layout.addRow("Stop Frequency:", stop_freq_layout)
        
        # Steps (now just called "Steps") with device limits
        steps_layout = QVBoxLayout()
        
        # Steps input with limits from device
        steps_input_layout = QHBoxLayout()
        self.segments_spinbox = QSpinBox()
        self.segments_spinbox.setRange(self.sweep_points_min, self.sweep_points_max)
        self.segments_spinbox.valueChanged.connect(self.on_segments_changed)
        self.segments_spinbox.setSuffix(" steps")
        steps_input_layout.addWidget(self.segments_spinbox)
        steps_layout.addLayout(steps_input_layout)
        
        # Device info label
        device_info_label = QLabel()
        if self.vna_device and hasattr(self.vna_device, 'name'):
            device_name = getattr(self.vna_device, 'name', 'Unknown Device')
            device_info_label.setText(f"Device: {device_name} (Min: {self.sweep_points_min}, Max: {self.sweep_points_max})")
        else:
            device_info_label.setText(f"No device detected (Default range: {self.sweep_points_min}-{self.sweep_points_max})")
        device_info_label.setStyleSheet("QLabel { font-size: 10px; font-style: italic; }")
        steps_layout.addWidget(device_info_label)
        
        freq_layout.addRow("Steps:", steps_layout)
        
        main_layout.addWidget(freq_group)
        
        # Calculated Values Group
        calc_group = QGroupBox("Calculated Values")
        calc_layout = QFormLayout(calc_group)
        
        # Center Frequency (read-only)
        self.center_freq_label = QLabel("0.000 MHz")
        self.center_freq_label.setStyleSheet("QLabel { font-weight: bold; }")
        calc_layout.addRow("Center Frequency:", self.center_freq_label)
        
        # Span (read-only)
        self.span_label = QLabel("0.000 MHz")
        self.span_label.setStyleSheet("QLabel { font-weight: bold; }")
        calc_layout.addRow("Span:", self.span_label)
        
        # Hz/step (read-only)
        self.hz_step_label = QLabel("0.000 Hz")
        self.hz_step_label.setStyleSheet("QLabel { font-weight: bold; }")
        calc_layout.addRow("Hz/step:", self.hz_step_label)
        
        main_layout.addWidget(calc_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_settings)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_changes)
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)
        
        main_layout.addLayout(button_layout)
        
    def frequency_to_hz(self, value, unit):
        """Convert frequency value to Hz based on unit."""
        multipliers = {
            "Hz": 1,
            "kHz": 1e3,
            "MHz": 1e6,
            "GHz": 1e9
        }
        return value * multipliers.get(unit, 1e6)  # Default to MHz if unknown
        
    def hz_to_frequency(self, hz_value, target_unit):
        """Convert Hz value to target unit."""
        multipliers = {
            "Hz": 1,
            "kHz": 1e3,
            "MHz": 1e6,
            "GHz": 1e9
        }
        return hz_value / multipliers.get(target_unit, 1e6)  # Default to MHz if unknown
        
    def load_settings(self):
        """Load settings from config.ini file."""
        # Default values (50 kHz to 1.5 GHz)
        default_start_hz = 50e3  # 50 kHz
        default_stop_hz = 1.5e9  # 1.5 GHz
        default_segments = 100
        
        # Load from settings (stored in Hz)
        start_freq_val = self.settings.value("Frequency/StartFreqHz", default_start_hz)
        stop_freq_val = self.settings.value("Frequency/StopFreqHz", default_stop_hz)
        segments_val = self.settings.value("Frequency/Segments", default_segments)
        
        # Load units
        start_unit = self.settings.value("Frequency/StartUnit", "kHz")
        stop_unit = self.settings.value("Frequency/StopUnit", "GHz")
        
        try:
            start_freq_hz = float(str(start_freq_val)) if start_freq_val is not None else default_start_hz
            stop_freq_hz = float(str(stop_freq_val)) if stop_freq_val is not None else default_stop_hz
            segments = int(str(segments_val)) if segments_val is not None else default_segments
        except (ValueError, TypeError):
            start_freq_hz = default_start_hz
            stop_freq_hz = default_stop_hz
            segments = default_segments
        
        # Set units first
        self.start_freq_unit.setCurrentText(str(start_unit))
        self.stop_freq_unit.setCurrentText(str(stop_unit))
        
        # Convert and set frequency values
        start_freq_display = self.hz_to_frequency(start_freq_hz, str(start_unit))
        stop_freq_display = self.hz_to_frequency(stop_freq_hz, str(stop_unit))
        
        self.start_freq_edit.setValue(start_freq_display)
        self.stop_freq_edit.setValue(stop_freq_display)
        self.segments_spinbox.setValue(segments)
        
    def save_settings(self):
        """Save current settings to config.ini file."""
        logging.info("[sweep_options_window.save_settings] Saving settings to config.ini")
        
        # Convert to Hz for storage
        start_freq_hz = self.frequency_to_hz(self.start_freq_edit.value(), self.start_freq_unit.currentText())
        stop_freq_hz = self.frequency_to_hz(self.stop_freq_edit.value(), self.stop_freq_unit.currentText())
        
        # Save frequencies in Hz and units separately
        self.settings.setValue("Frequency/StartFreqHz", start_freq_hz)
        self.settings.setValue("Frequency/StopFreqHz", stop_freq_hz)
        self.settings.setValue("Frequency/Segments", self.segments_spinbox.value())
        
        # Save units
        self.settings.setValue("Frequency/StartUnit", self.start_freq_unit.currentText())
        self.settings.setValue("Frequency/StopUnit", self.stop_freq_unit.currentText())
        
        self.settings.sync()
        logging.info("[sweep_options_window.save_settings] Settings saved successfully")
        
    def calculate_derived_values(self):
        """Calculate and update center frequency, span, and Hz/step."""
        # Get frequencies in Hz
        start_freq_hz = self.frequency_to_hz(self.start_freq_edit.value(), self.start_freq_unit.currentText())
        stop_freq_hz = self.frequency_to_hz(self.stop_freq_edit.value(), self.stop_freq_unit.currentText())
        segments = self.segments_spinbox.value()
        
        # Validate frequency range
        if start_freq_hz >= stop_freq_hz:
            self.center_freq_label.setText("Invalid Range")
            self.span_label.setText("Invalid Range")
            self.hz_step_label.setText("Invalid Range")
            return
            
        # Calculate center frequency
        center_freq_hz = (start_freq_hz + stop_freq_hz) / 2
        
        # Format center frequency with appropriate units
        if center_freq_hz >= 1e9:
            self.center_freq_label.setText(f"{center_freq_hz/1e9:.3f} GHz")
        elif center_freq_hz >= 1e6:
            self.center_freq_label.setText(f"{center_freq_hz/1e6:.3f} MHz")
        elif center_freq_hz >= 1e3:
            self.center_freq_label.setText(f"{center_freq_hz/1e3:.3f} kHz")
        else:
            self.center_freq_label.setText(f"{center_freq_hz:.3f} Hz")
        
        # Calculate span
        span_hz = stop_freq_hz - start_freq_hz
        
        # Format span with appropriate units
        if span_hz >= 1e9:
            self.span_label.setText(f"{span_hz/1e9:.3f} GHz")
        elif span_hz >= 1e6:
            self.span_label.setText(f"{span_hz/1e6:.3f} MHz")
        elif span_hz >= 1e3:
            self.span_label.setText(f"{span_hz/1e3:.3f} kHz")
        else:
            self.span_label.setText(f"{span_hz:.3f} Hz")
        
        # Calculate Hz/step
        if segments > 1:
            hz_per_step = span_hz / (segments - 1)
            
            # Format Hz/step with appropriate units
            if hz_per_step >= 1e6:
                self.hz_step_label.setText(f"{hz_per_step/1e6:.3f} MHz")
            elif hz_per_step >= 1e3:
                self.hz_step_label.setText(f"{hz_per_step/1e3:.3f} kHz")
            else:
                self.hz_step_label.setText(f"{hz_per_step:.3f} Hz")
        else:
            self.hz_step_label.setText("0.000 Hz")
            
    def on_frequency_changed(self):
        """Handle frequency changes."""
        self.calculate_derived_values()
        
    def on_segments_changed(self):
        """Handle segments changes."""
        self.calculate_derived_values()
        
    def apply_settings(self):
        """Apply and save current settings."""
        # Get frequencies in Hz for validation
        start_freq_hz = self.frequency_to_hz(self.start_freq_edit.value(), self.start_freq_unit.currentText())
        stop_freq_hz = self.frequency_to_hz(self.stop_freq_edit.value(), self.stop_freq_unit.currentText())
        
        # Validate inputs
        if start_freq_hz >= stop_freq_hz:
            QMessageBox.warning(
                self, 
                "Invalid Range", 
                "Start frequency must be less than stop frequency."
            )
            return
            
        # Validate maximum frequency limit
        if stop_freq_hz > self.max_frequency_hz:
            max_freq_ghz = self.max_frequency_hz / 1e9
            QMessageBox.warning(
                self, 
                "Frequency Limit Exceeded", 
                f"Stop frequency cannot exceed {max_freq_ghz:.1f} GHz.\n"
            )
            return
            
        # Validate steps range according to device limits
        steps_value = self.segments_spinbox.value()
        if steps_value < self.sweep_points_min or steps_value > self.sweep_points_max:
            device_name = getattr(self.vna_device, 'name', 'Current device') if self.vna_device else 'Current device'
            QMessageBox.warning(
                self, 
                "Invalid Steps", 
                f"Number of steps must be between {self.sweep_points_min} and {self.sweep_points_max} "
                f"for {device_name}."
            )
            return
            
        # Save settings
        self.save_settings()

        self.main_window.load_sweep_configuration()

        # Close window without confirmation message
        self.close()
        
    def reset_to_defaults(self):
        """Reset all values to default settings."""
        logging.info("[sweep_options_window.reset_to_defaults] Reset to defaults requested")
        
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all values to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logging.info("[sweep_options_window.reset_to_defaults] Resetting to default values")
            
            # Set default values (50 kHz to 1.5 GHz)
            self.start_freq_unit.setCurrentText("kHz")
            self.start_freq_edit.setValue(50.0)  # 50 kHz
            
            self.stop_freq_unit.setCurrentText("GHz")
            self.stop_freq_edit.setValue(1.5)  # 1.5 GHz
            
            self.segments_spinbox.setValue(101)
            
            # Recalculate derived values
            self.calculate_derived_values()
        else:
            logging.info("[sweep_options_window.reset_to_defaults] Reset to defaults cancelled")

    def store_original_values(self):
        """Store original values when window opens for cancel functionality."""
        self.original_values = {
            'start_freq': self.start_freq_edit.value(),
            'start_unit': self.start_freq_unit.currentText(),
            'stop_freq': self.stop_freq_edit.value(),
            'stop_unit': self.stop_freq_unit.currentText(),
            'segments': self.segments_spinbox.value()
        }

    def cancel_changes(self):
        """Cancel changes and restore original values."""
        if hasattr(self, 'original_values') and self.original_values:
            # Restore original values
            self.start_freq_edit.setValue(self.original_values['start_freq'])
            self.start_freq_unit.setCurrentText(self.original_values['start_unit'])
            self.stop_freq_edit.setValue(self.original_values['stop_freq'])
            self.stop_freq_unit.setCurrentText(self.original_values['stop_unit'])
            self.segments_spinbox.setValue(self.original_values['segments'])
            
            # Recalculate derived values with original settings
            self.calculate_derived_values()
        
        # Close window without saving
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Mock parent for testing
    class MockParent:
        def load_sweep_configuration(self):
            pass
    
    mock_parent = MockParent()
    window = SweepOptionsWindow(mock_parent)
    window.show()
    sys.exit(app.exec())
