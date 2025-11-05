"""
Welcome setup window for NanoVNA devices.
"""
import os
import sys
import logging
import numpy as np
import skrf as rf

# Suppress verbose matplotlib logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
logging.getLogger('matplotlib.pyplot').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

from PySide6.QtCore import QTimer, QThread, Qt, QSettings, QPropertyAnimation, QPoint
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QHBoxLayout, QGroupBox, QComboBox, QToolButton, QMenu, QFrame,
    QFileDialog, 
)
from PySide6.QtGui import QIcon, QColor

try:
    from NanoVNA_UTN_Toolkit.ui.graphics_window import NanoVNAGraphics
except ImportError as e:
    logging.error("Failed to import NanoVNAGraphics: %s", e)
    NanoVNAGraphics = None

from ..workers.device_worker import DeviceWorker
from .log_handler import GuiLogHandler

try:
    from NanoVNA_UTN_Toolkit.ui.wizard_windows import CalibrationWizard
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

# Import calibration data storage
try:
    from NanoVNA_UTN_Toolkit.calibration.calibration_manager import OSMCalibrationManager
    from NanoVNA_UTN_Toolkit.calibration.calibration_manager import THRUCalibrationManager
except ImportError as e:
    logging.error("Failed to import OSMCalibrationManager: %s", e)
    logging.error("Failed to import THRUCalibrationManager: %s", e)
    OSMCalibrationManager = None
    THRUCalibrationManager = None

from datetime import datetime

class NanoVNAWelcome(QMainWindow):
    def __init__(self, s11=None, freqs=None, vna_device=None):
        super().__init__()

        # Load configuration for UI colors and styles
        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "ui", "graphics_windows", "ini", "config.ini")
        settings = QSettings(ruta_ini, QSettings.IniFormat)

        # Read colors for different widgets
        background_color = settings.value("Dark_Light/QWidget/background-color", "#3a3a3a")
        tabwidget_pane_bg = settings.value("Dark_Light/QTabWidget_pane/background-color", "#3b3b3b")
        tabbar_bg = settings.value("Dark_Light/QTabBar/background-color", "#2b2b2b")
        tabbar_color = settings.value("Dark_Light/QTabBar/color", "white")
        tabbar_padding = settings.value("Dark_Light/QTabBar/padding", "5px 12px")
        tabbar_border = settings.value("Dark_Light/QTabBar/border", "none")
        tabbar_border_tl_radius = settings.value("Dark_Light/QTabBar/border-top-left-radius", "6px")
        tabbar_border_tr_radius = settings.value("Dark_Light/QTabBar/border-top-right-radius", "6px")
        tabbar_selected_bg = settings.value("Dark_Light/QTabBar_selected/background-color", "#4d4d4d")
        tabbar_selected_color = settings.value("Dark_Light/QTabBar/color", "white")
        spinbox_bg = settings.value("Dark_Light/QSpinBox/background-color", "#3b3b3b")
        spinbox_color = settings.value("Dark_Light/QSpinBox/color", "white")
        spinbox_border = settings.value("Dark_Light/QSpinBox/border", "1px solid white")
        spinbox_border_radius = settings.value("Dark_Light/QSpinBox/border-radius", "8px")
        groupbox_title_color = settings.value("Dark_Light/QGroupBox_title/color", "white")
        label_color = settings.value("Dark_Light/QLabel/color", "white")
        lineedit_bg = settings.value("Dark_Light/QLineEdit/background-color", "#3b3b3b")
        lineedit_color = settings.value("Dark_Light/QLineEdit/color", "white")
        lineedit_border = settings.value("Dark_Light/QLineEdit/border", "1px solid white")
        lineedit_border_radius = settings.value("Dark_Light/QLineEdit/border-radius", "6px")
        lineedit_padding = settings.value("Dark_Light/QLineEdit/padding", "4px")
        lineedit_focus_bg = settings.value("Dark_Light/QLineEdit_focus/background-color", "#454545")
        lineedit_focus_border = settings.value("Dark_Light/QLineEdit_focus/border", "1px solid #4d90fe")
        pushbutton_bg = settings.value("Dark_Light/QPushButton/background-color", "#3b3b3b")
        pushbutton_color = settings.value("Dark_Light/QPushButton/color", "white")
        pushbutton_border = settings.value("Dark_Light/QPushButton/border", "2px solid white")
        pushbutton_border_radius = settings.value("Dark_Light/QPushButton/border-radius", "6px")
        pushbutton_padding = settings.value("Dark_Light/QPushButton/padding", "4px 10px")
        pushbutton_hover_bg = settings.value("Dark_Light/QPushButton_hover/background-color", "#4d4d4d")
        pushbutton_pressed_bg = settings.value("Dark_Light/QPushButton_pressed/background-color", "#5c5c5c")
        menu_bg = settings.value("Dark_Light/QMenu/background", "#3a3a3a")
        menu_color = settings.value("Dark_Light/QMenu/color", "white")
        menu_border = settings.value("Dark_Light/QMenu/border", "1px solid #3b3b3b")
        menubar_bg = settings.value("Dark_Light/QMenuBar/background-color", "#3a3a3a")
        menubar_color = settings.value("Dark_Light/QMenuBar/color", "white")
        menubar_item_bg = settings.value("Dark_Light/QMenuBar_item/background", "transparent")
        menubar_item_color = settings.value("Dark_Light/QMenuBar_item/color", "white")
        menubar_item_padding = settings.value("Dark_Light/QMenuBar_item/padding", "4px 10px")
        menubar_item_selected_bg = settings.value("Dark_Light/QMenuBar_item_selected/background-color", "#4d4d4d")

        # QCombo

        color_text_QCombo = settings.value("Dark_Light/QComboBox/color", "white")

        self.pushbutton_bg = pushbutton_bg
        self.pushbutton_color = pushbutton_color
        self.pushbutton_border_radius = pushbutton_border_radius
        self.pushbutton_padding = pushbutton_padding
        self.pushbutton_hover_bg = pushbutton_hover_bg
        self.pushbutton_pressed_bg = pushbutton_pressed_bg

        # === Apply stylesheet to unify QPushButton and QToolButton appearance ===
        self.setStyleSheet(f"""
            /* --- QToolButton styled like QPushButton --- */
            QToolButton {{
                background-color: {pushbutton_bg};
                color: {pushbutton_color};
                border: {pushbutton_border};
                border-radius: {pushbutton_border_radius};
                font-size: 16px;
                font-weight: bold;
                padding: {pushbutton_padding};
                margin: 0px;
            }}
            QToolButton:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QToolButton:pressed {{
                background-color: {pushbutton_pressed_bg};
            }}
            QToolButton::menu-indicator {{
                image: none;
            }}
            /* --- Other widgets --- */
            QWidget {{ background-color: {background_color}; }}
            QTabWidget::pane {{ background-color: {tabwidget_pane_bg}; }}
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
            QGroupBox:title {{ color: {groupbox_title_color}; }}
            QLabel {{ color: {label_color}; }}
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
            QPushButton:hover {{ background-color: {pushbutton_hover_bg}; }}
            QPushButton:pressed {{ background-color: {pushbutton_pressed_bg}; }}
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
            QComboBox {{
                color: black;                 
                background-color: white;
                border: 1px solid #5f5f5f;
                border-radius: 5px;
                padding-left: 5px;            
            }}
            QComboBox QAbstractItemView {{
                color: black;
                background-color: white;             
                selection-background-color: lightgray; 
                selection-color: black;
            }}
            QComboBox:focus {{
                background-color: white;
            }}
            QComboBox::placeholder {{
                color: lightgray;
            }}
        """)

        # === Store VNA device reference ===
        self.vna_device = vna_device
        logging.info("[welcome_windows.__init__] Initializing welcome window")

        # === Set application icon ===
        icon_paths = [
            os.path.join(os.path.dirname(__file__), 'icon.ico'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'icon.ico'),
            'icon.ico'
        ]
        for icon_path in icon_paths:
            icon_path = os.path.abspath(icon_path)
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break

        if OSMCalibrationManager:
            self.osm_calibration = OSMCalibrationManager()
            if vna_device and hasattr(vna_device, 'name'):
                self.osm_calibration.device_name = vna_device.name
            logging.info("[CalibrationWizard] OSM calibration manager initialized")
        else:
            self.osm_calibration = None
            logging.warning("[CalibrationWizard] OSMCalibrationManager not available")
        
        if THRUCalibrationManager:
            self.thru_calibration = THRUCalibrationManager()
            if vna_device and hasattr(vna_device, 'name'):
                self.thru_calibration.device_name = vna_device.name
            logging.info("[CalibrationWizard] THRU calibration manager initialized")
        else:
            self.thru_calibration = None
            logging.warning("[CalibrationWizard] THRUCalibrationManager not available")

        self.setWindowTitle("NanoVNA UTN Toolkit - Welcome Window")
        self.setGeometry(100, 100, 1000, 500)

        # === Central widget and main layout ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === Create main content area ===
        self._create_calibration_group(main_layout)
        self._create_measurements_group(main_layout)
        
        main_layout.addStretch()

    def _create_calibration_group(self, parent_layout):
        """
        Create the calibration wizard group box with description.
        Provides information about VNA calibration importance and wizard access.
        """
        logging.info("[welcome_windows._create_calibration_group] Creating calibration group")
        
        calibration_group = QGroupBox("Calibration Wizard")
        calibration_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        calibration_layout = QVBoxLayout(calibration_group)
        calibration_layout.setSpacing(15)

        # Calibration description
        description_text = (
            "Calibration is essential for accurate VNA measurements. It removes systematic errors "
            "from cables, connectors, and the VNA itself by measuring known reference standards. "
            "The Calibration Wizard guides you through this process step-by-step, ensuring your "
            "measurements are precise and reliable."
        )
        
        description_label = QLabel(description_text)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-weight: normal; font-size: 14px; color: #cccccc; padding: 10px;")
        calibration_layout.addWidget(description_label)

        # Calibration wizard button
        self.calibration_wizard_button = QPushButton("Open Calibration Wizard")
        self.calibration_wizard_button.clicked.connect(self.open_calibration_wizard)
        self.calibration_wizard_button.setFixedHeight(50)
        self.calibration_wizard_button.setStyleSheet("font-size: 16px; margin: 10px;")
        calibration_layout.addWidget(self.calibration_wizard_button, alignment=Qt.AlignCenter)

        parent_layout.addWidget(calibration_group)
        logging.info("[welcome_windows._create_calibration_group] Calibration group created successfully")

    def _create_measurements_group(self, parent_layout):
        """
        Create the measurements group box with calibration kit selector and navigation buttons.
        Contains kit selection, graphics navigation, and calibration import functionality.
        """
        logging.info("[welcome_windows._create_measurements_group] Creating measurements group")
        
        measurements_group = QGroupBox("Measurements")
        measurements_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        measurements_layout = QVBoxLayout(measurements_group)
        measurements_layout.setSpacing(15)

        # Create calibration kit selector
        self._create_calibration_kit_selector(measurements_layout)
        
        # Create action buttons
        self._create_action_buttons(measurements_layout)

        parent_layout.addWidget(measurements_group)
        logging.info("[welcome_windows._create_measurements_group] Measurements group created successfully")

    def _create_calibration_kit_selector(self, parent_layout):
        """
        Create the calibration kit selector dropdown with available kits.
        Displays available calibration kits in a dropdown with None as default.
        """
        logging.info("[welcome_windows._create_calibration_kit_selector] Creating kit selector dropdown")

        # Add label for calibration kit selector
        kit_selector_label = QLabel("Calibration Kit Selection:")
        kit_selector_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        parent_layout.addWidget(kit_selector_label)

        # Load calibration kits first
        self._load_calibration_kits()

        # Create dropdown for kit selection
        self.kit_dropdown = QComboBox()
        self.kit_dropdown.setFixedHeight(40)
        self.kit_dropdown.setMinimumWidth(400)  # Set minimum width for better appearance
        self.kit_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #3b3b3b;
                color: white;
                border: 2px solid white;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                min-width: 400px;
            }
            QComboBox:hover {
                background-color: #4d4d4d;
            }
            QComboBox::drop-down {
                width: 0px;
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #3b3b3b;
                color: white;
                selection-background-color: #4d4d4d;
                selection-color: white;
                border: 1px solid white;
            }
        """)

        # Add None as default option
        self.kit_dropdown.addItem("None")
        
        # Add available calibration kits
        for kit_name in self.kit_names:
            self.kit_dropdown.addItem(kit_name)

        # Set current selection based on existing calibration
        self._set_current_kit_selection()

        # Connect selection change handler
        self.kit_dropdown.currentTextChanged.connect(self._on_kit_selection_changed)

        # Add dropdown to parent layout
        parent_layout.addWidget(self.kit_dropdown, alignment=Qt.AlignmentFlag.AlignLeft)

        # Display current selection info
        self.kit_info_label = QLabel("")
        self.kit_info_label.setStyleSheet("font-size: 12px; color: #cccccc; margin-top: 10px; margin-left: 0px; padding: 5px;")
        self.kit_info_label.setWordWrap(True)
        self.kit_info_label.setMinimumWidth(400)  # Ensure minimum width for better text display
        parent_layout.addWidget(self.kit_info_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Initialize selected_kit_name based on current dropdown selection
        current_text = self.kit_dropdown.currentText()
        if current_text.startswith("None"):
            self.selected_kit_name = None
        else:
            self.selected_kit_name = current_text

        self._update_kit_info_display()
        
        logging.info(f"[welcome_windows._create_calibration_kit_selector] Kit dropdown created with {len(self.kit_names)} kits available")

    def _set_current_kit_selection(self):
        """
        Set the current kit selection in the dropdown based on saved calibration.
        Updates dropdown to show currently active calibration kit.
        """
        calibration_name = self._get_current_calibration_name()
        
        if "_" in str(calibration_name):
            calibration_name_split = str(calibration_name).rsplit("_", 1)[0]
        else:
            calibration_name_split = str(calibration_name)

        # Find matching kit in dropdown
        if calibration_name_split in self.kit_names:
            kit_index = self.kit_names.index(calibration_name_split) + 1  # +1 because "None" is at index 0
            self.kit_dropdown.setCurrentIndex(kit_index)
            logging.info(f"[welcome_windows._set_current_kit_selection] Set dropdown to kit: {calibration_name_split}")
        else:
            # Set to "None" if no matching kit found
            self.kit_dropdown.setCurrentIndex(0)
            logging.info("[welcome_windows._set_current_kit_selection] Set dropdown to None - no matching kit found")

    def _on_kit_selection_changed(self, selected_text):
        """
        Handle calibration kit selection change from dropdown.
        Updates display and saves selection for graphics window navigation.
        """
        logging.info(f"[welcome_windows._on_kit_selection_changed] Kit selection changed to: {selected_text}")
        
        if selected_text.startswith("None"):
            self.selected_kit_name = None
            logging.info("[welcome_windows._on_kit_selection_changed] No kit selected")
        else:
            self.selected_kit_name = selected_text
            logging.info(f"[welcome_windows._on_kit_selection_changed] Selected kit: {selected_text}")
        
        self._update_kit_info_display()

    def _update_kit_info_display(self):
        """
        Update the information display below the kit selector.
        Shows details about the currently selected calibration kit.
        """
        if hasattr(self, 'selected_kit_name') and self.selected_kit_name:
            # Find kit details
            if self.selected_kit_name in self.kit_names:
                kit_index = self.kit_names.index(self.selected_kit_name)
                kit_id = self.kit_ids[kit_index] if kit_index < len(self.kit_ids) else "Unknown"
                
                # Get additional kit information if available
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
                settings = QSettings(config_path, QSettings.Format.IniFormat)
                
                kit_method = settings.value(f"Kit_{kit_id}/method", "Unknown")
                kit_datetime = settings.value(f"Kit_{kit_id}/DateTime_Kits", "Unknown")
                
                info_text = f"Selected Kit: {self.selected_kit_name}\nMethod: {kit_method}\nCreated: {kit_datetime}"
                self.kit_info_label.setText(info_text)
                logging.info(f"[welcome_windows._update_kit_info_display] Updated info for kit: {self.selected_kit_name}")
            else:
                self.kit_info_label.setText(f"Selected Kit: {self.selected_kit_name}\n(Kit details not found)")
        else:
            self.kit_info_label.setText("No calibration kit selected")
            logging.info("[welcome_windows._update_kit_info_display] Cleared kit info - no selection")

    def _create_action_buttons(self, parent_layout):
        """
        Create action buttons for graphics navigation and calibration import.
        Provides access to measurement graphics and external calibration import.
        """
        logging.info("[welcome_windows._create_action_buttons] Creating action buttons")

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Graphics button
        self.graphics_button = QPushButton("Open Graphics Window")
        self.graphics_button.clicked.connect(self.graphics_clicked)
        self.graphics_button.setFixedHeight(50)
        self.graphics_button.setStyleSheet("font-size: 16px; margin: 10px;")
        button_layout.addWidget(self.graphics_button)

        # Import calibration button
        self.import_button = QPushButton("Import Calibration")
        self.import_button.clicked.connect(self.import_calibration)
        self.import_button.setFixedHeight(50)
        self.import_button.setStyleSheet("font-size: 16px; margin: 10px;")
        button_layout.addWidget(self.import_button)

        parent_layout.addLayout(button_layout)
        logging.info("[welcome_windows._create_action_buttons] Action buttons created successfully")

    def _load_calibration_kits(self):
        """
        Load available calibration kits from configuration.
        Reads kit information from calibration config file.
        """
        logging.info("[welcome_windows._load_calibration_kits] Loading calibration kits")
        
        # Use new calibration structure
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
        settings_calibration = QSettings(config_path, QSettings.Format.IniFormat)
        kit_groups = [g for g in settings_calibration.childGroups() if g.startswith("Kit_")]

        # --- Get kit names and IDs ---
        self.kit_names = [settings_calibration.value(f"{g}/kit_name", "") for g in kit_groups]
        self.kit_ids = [int(settings_calibration.value(f"{g}/id", 0)) for g in kit_groups]
        
        logging.info(f"[welcome_windows._load_calibration_kits] Loaded {len(self.kit_names)} calibration kits")

    def _get_current_calibration_name(self):
        """
        Get the currently selected calibration name from settings.
        Returns the active calibration name or default value.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
        settings_calibration = QSettings(config_path, QSettings.Format.IniFormat)
        
        # --- Get current calibration ---
        calibration_name = settings_calibration.value("Calibration/Name", "No Calibration")
        logging.info(f"[welcome_windows._get_current_calibration_name] Current calibration: {calibration_name}")

        if "_" in calibration_name:
            calibration_name_split = calibration_name.rsplit("_", 1)[0]
        else:
            calibration_name_split = calibration_name

        matched_id = 0
        self.current_index = -1  

        if calibration_name_split in self.kit_names:
            self.current_index = self.kit_names.index(calibration_name_split)
            matched_id = self.kit_ids[self.current_index]
            logging.info(f"[welcome_windows._get_current_calibration_name] Found matching kit at index {self.current_index}")
        else:
            logging.warning(f"[welcome_windows._get_current_calibration_name] No matching kit found for {calibration_name_split}")

        return calibration_name

    def import_calibration(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
        import os

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Calibration Files",
            "",
            "Touchstone Files (*.s1p *.s2p);;All Files (*)"
        )

        if not files:
            QMessageBox.warning(self, "No Files Selected", "Please select the 4 calibration files.")
            return

        required_names = ["open", "short", "load", "match", "thru"]
        filenames = [os.path.basename(f).lower() for f in files]
        found = {name: any(name in f for f in filenames) for name in required_names}
        has_load_or_match = found["load"] or found["match"]

        missing = []
        if not found["open"]:
            missing.append("open")
        if not found["short"]:
            missing.append("short")
        if not has_load_or_match:
            missing.append("load or match")
        if not found["thru"]:
            missing.append("thru")

        if missing:
            QMessageBox.warning(self, "Missing Files", f"The following calibration files are missing: {', '.join(missing)}")
            return

        if len(files) != 4:
            QMessageBox.warning(self, "Invalid Selection", "You must select exactly 4 calibration files.")
            return

        QMessageBox.information(self, "Success", "All calibration files selected successfully!")
        print("Selected calibration files:")
        for f in files:
            print(f)

        # "Select Method"
        dialog = QDialog(self)
        dialog.setWindowTitle("NanoVNA UTN Toolkit - Select Calibration Method")

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)  

        label = QLabel("Select Method", dialog)
        main_layout.addWidget(label)

        self.select_method = QComboBox()
        self.select_method.setEditable(False)

        # Placeholder
        self.select_method.addItem("Select Method")
        item = self.select_method.model().item(0)
        item.setEnabled(False)
        placeholder_color = QColor(120, 120, 120)
        item.setForeground(placeholder_color)

        methods = [
            "OSM (Open - Short - Match)",
            "Normalization",
            "1-Port+N",
            "Enhanced-Response"
        ]
        self.select_method.addItems(methods)

        main_layout.addWidget(self.select_method)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10) 

        cancel_button = QPushButton("Cancel", dialog)
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        calibrate_button = QPushButton("Calibrate", dialog)
        calibrate_button.clicked.connect(lambda: self.start_calibration(files, self.select_method.currentText(), dialog))
        button_layout.addWidget(calibrate_button)

        main_layout.addLayout(button_layout)

        dialog.exec()

    def start_calibration(self, files, selected_method, dialog):
        print(f"Starting calibration with method: {selected_method}")
        for f in files:
            print(f)
        dialog.accept()

        self.save_calibration_dialog(selected_method, files)

    def save_calibration_dialog(self, selected_method, files):
        from PySide6.QtWidgets import QMessageBox
        """Shows a dialog to save the calibration without advancing to graphics window"""
        if not self.osm_calibration:
            return

        if not self.thru_calibration:
            return

        # Check which measurements are available
        osm_status = self.osm_calibration.is_complete_true()
        thru_status = self.thru_calibration.is_complete_true()
             
        # Dialog to enter calibration name
        from PySide6.QtWidgets import QInputDialog

        if selected_method == "OSM (Open - Short - Match)":
            prefix = "OSM"
        elif selected_method == "Normalization":
            prefix = "Normalization"
        elif selected_method == "1-Port+N":
            prefix = "1PortN"
        elif selected_method == "Enhanced-Response":
            prefix = "Enhanced Response"

        name, ok = QInputDialog.getText(
            self, 
            'Save Calibration', 
            f'Enter calibration name:',
            text=f'{prefix}_Calibration_{self.get_current_timestamp()}'
        )

        is_external_kit = True
        
        if ok and name:
            try:
                # Save calibration (it will save only the available measurements)
                success = self.osm_calibration.save_calibration_file(name, selected_method, is_external_kit, files)
                if success:
                    # Show success message
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Calibration '{name}' saved successfully!\n\nSaved measurements: \n\nFiles saved in:\n- Touchstone format\n- .cal format\n\nUse 'Finish' button to continue to graphics window."
                    )
                    
                    # Stay in wizard - do not advance to graphics window
                    logging.info(f"Calibration '{name}' saved successfully - staying in wizard")
                    
                else:
                    from PySide6.QtWidgets import QMessageBox
                    #QMessageBox.warning(self, "Error", "Failed to save calibration")

                success = self.thru_calibration.save_calibration_file(name, selected_method, is_external_kit, files, osm_instance=self.osm_calibration)
                if success:
                    # Show success message
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Calibration '{name}' saved successfully!\n\nSaved measurements: \n\nFiles saved in:\n- Touchstone format\n- .cal format\n\nUse 'Finish' button to continue to graphics window."
                    )
                    
                    # Stay in wizard - do not advance to graphics window
                    logging.info(f"Calibration '{name}' saved successfully - staying in wizard")
                    
                else:
                    from PySide6.QtWidgets import QMessageBox
                    #QMessageBox.warning(self, "Error", "Failed to save calibration")

                # --- Read current calibration method ---
                # Use new calibration structure
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
                settings_calibration = QSettings(config_path, QSettings.Format.IniFormat)

                """     # --- If a kit was previously saved in this session, show its name ---
                if getattr(self, 'last_saved_kit_id', None):
                    last_id = self.last_saved_kit_id
                    last_name = settings_calibration.value(f"Kit_{last_id}/kit_name", "")
                    if last_name:
                        name_input.setText(last_name)

                if name is None:
                    name = name_input.text().strip()
                if not name:
                    name_input.setPlaceholderText("Please enter a valid name...")
                    return
                """
                # --- Check if name already exists in any Kit ---
                existing_groups = settings_calibration.childGroups()
                for g in existing_groups:
                    if g.startswith("Kit_"):
                        existing_name = settings_calibration.value(f"{g}/kit_name", "")
                        if existing_name == name:
                            # Show warning message box if name exists
                            QMessageBox.warning(dialog, "Duplicate Name",
                                                f"The kit name '{name}' already exists.\nPlease choose another name.",
                                                QMessageBox.Ok)
                            return

                # --- Determine ID: use last saved if exists ---
                if getattr(self, 'last_saved_kit_id', None):
                    next_id = self.last_saved_kit_id
                else:
                    # First save -> calculate next available ID
                    kit_ids = [int(g.split("_")[1]) for g in existing_groups if g.startswith("Kit_") and g.split("_")[1].isdigit()]
                    next_id = max(kit_ids, default=0) + 1
                    self.last_saved_kit_id = next_id  # store ID for overwriting next time

                calibration_entry_name = f"Kit_{next_id}"
                full_calibration_name = f"{name}_{next_id}"

                current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # --- Save data ---
                settings_calibration.beginGroup(calibration_entry_name)
                settings_calibration.setValue("kit_name", name)
                settings_calibration.setValue("method", selected_method)
                settings_calibration.setValue("id", next_id)
                settings_calibration.setValue("DateTime_Kits", current_datetime)
                settings_calibration.endGroup()

                # --- Update active calibration reference ---
                settings_calibration.beginGroup("Calibration")
                settings_calibration.setValue("Name", full_calibration_name)
                settings_calibration.endGroup()
                settings_calibration.sync()

                settings_calibration.setValue("Calibration/Kits", True)
                settings_calibration.setValue("Calibration/NoCalibration", False)

                # Use new calibration structure
          
                if selected_method == "OSM (Open - Short - Match)":
                    parameter = "S11"
                elif selected_method == "Normalization":
                    parameter = "S21"
                else:
                    parameter = "S11, S21"

                settings_calibration.setValue("Calibration/Parameter", parameter)
                settings_calibration.sync()

                logging.info(f"[welcome_windows.open_save_calibration] Saved calibration {full_calibration_name}")

            except Exception as e:
                logging.error(f"[CalibrationWelcome] Error saving calibration: {e}")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Error saving calibration: {str(e)}")

    def get_current_timestamp(self):
        """Generate timestamp for filenames"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def open_calibration_wizard(self):

        # Use new calibration structure
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
        settings_calibration = QSettings(config_path, QSettings.IniFormat)

        settings_calibration.setValue("Calibration/Kits", False)
        settings_calibration.setValue("Calibration/NoCalibration", False)
        settings_calibration.sync()

        logging.info("[welcome_windows.open_calibration_wizard] Opening calibration wizard")
        if self.vna_device:
            self.welcome_windows = CalibrationWizard(self.vna_device, caller="welcome")
        else:
            self.welcome_windows = CalibrationWizard()
        self.welcome_windows.show()
        self.close()

    def graphics_clicked(self):
        """
        Navigate to graphics window with selected calibration kit.
        Applies the selected calibration kit before opening graphics.
        """
        logging.info("[welcome_windows.graphics_clicked] Opening graphics window")

        # Use new calibration structure
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
        settings_calibration = QSettings(config_path, QSettings.Format.IniFormat)

        # Get currently selected kit from dropdown
        current_selection = self.kit_dropdown.currentText()
        logging.info(f"[welcome_windows.graphics_clicked] Current dropdown selection: {current_selection}")

        # Check if a kit is selected in the dropdown (not "None")
        if current_selection and not current_selection.startswith("None"):
            # Apply the selected calibration kit
            self._apply_selected_kit_calibration(current_selection)
            logging.info(f"[welcome_windows.graphics_clicked] Applied selected kit: {current_selection}")
        else:
            # No calibration kit selected
            settings_calibration.setValue("Calibration/Kits", False)
            settings_calibration.setValue("Calibration/NoCalibration", True)
            settings_calibration.sync()
            logging.info("[welcome_windows.graphics_clicked] No calibration kit selected - proceeding without calibration")

        # Open graphics window
        if self.vna_device:
            graphics_window = NanoVNAGraphics(vna_device=self.vna_device)
        else:
            graphics_window = NanoVNAGraphics()
        graphics_window.show()
        self.close()

    def _apply_selected_kit_calibration(self, kit_name):
        """
        Apply the selected calibration kit settings.
        Updates configuration to use the specified kit for measurements.
        """
        logging.info(f"[welcome_windows._apply_selected_kit_calibration] Applying kit: {kit_name}")

        # Use new calibration structure
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
        settings_calibration = QSettings(config_path, QSettings.Format.IniFormat)

        # --- Get all kit names, IDs, and methods ---
        kit_groups = [g for g in settings_calibration.childGroups() if g.startswith("Kit_")]
        kit_names = [settings_calibration.value(f"{g}/kit_name", "") for g in kit_groups]
        kit_ids = [int(settings_calibration.value(f"{g}/id", 0)) for g in kit_groups]
        kit_methods = [settings_calibration.value(f"{g}/method", "") for g in kit_groups]
        kit_date_times = [settings_calibration.value(f"{g}/DateTime_Kits", "") for g in kit_groups]

        # --- Find the matching kit ---
        if kit_name in kit_names:
            idx = kit_names.index(kit_name)
            matched_id = kit_ids[idx]
            matched_method = kit_methods[idx]
            matched_date_time_kit = kit_date_times[idx]

            # --- Append ID to the kit_name ---
            kit_name_with_id = f"{kit_name}_{matched_id}"

            # --- Save updated values in [Calibration] ---
            settings_calibration.setValue("Calibration/Name", kit_name_with_id)
            settings_calibration.setValue("Calibration/id", matched_id)
            settings_calibration.setValue("Calibration/Method", matched_method)
            settings_calibration.setValue("Calibration/DateTime_Kits", matched_date_time_kit)

            if matched_method == "OSM (Open - Short - Match)":
                parameter = "S11"
            elif matched_method == "Normalization":
                parameter = "S21"
            else:
                parameter = "S11, S21"

            settings_calibration.setValue("Calibration/Parameter", parameter)
            settings_calibration.setValue("Calibration/Kits", True)
            settings_calibration.setValue("Calibration/NoCalibration", False)
            settings_calibration.sync()

            logging.info(f"[welcome_windows._apply_selected_kit_calibration] Applied calibration: {kit_name_with_id} (ID {matched_id}, Method {matched_method})")
        else:
            logging.warning(f"[welcome_windows._apply_selected_kit_calibration] No matching kit found for '{kit_name}'")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ventana = NanoVNAWelcome()
    ventana.show()
    sys.exit(app.exec())
