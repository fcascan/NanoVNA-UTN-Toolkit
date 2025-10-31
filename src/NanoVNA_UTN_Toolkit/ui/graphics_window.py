"""
Graphic view window for NanoVNA devices with dual info panels and cursors.
"""
import os
import sys
import logging
import numpy as np
import skrf as rf

from skrf import Network

import matplotlib.pyplot as plt

plt.rcParams['mathtext.fontset'] = 'cm'  
plt.rcParams['text.usetex'] = False       
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['font.family'] = 'serif'    
plt.rcParams['mathtext.rm'] = 'serif'     

from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox

# Import exporters
from ..exporters.latex_exporter import LatexExporter
from ..exporters.touchstone_exporter import TouchstoneExporter

from matplotlib.backends.backend_pdf import PdfPages

from NanoVNA_UTN_Toolkit.ui.calibration.methods import Methods
from NanoVNA_UTN_Toolkit.ui.calibration.kits import KitsCalibrator

# Suppress verbose matplotlib logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
logging.getLogger('matplotlib.pyplot').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

from PySide6.QtCore import QTimer, QThread, Qt, QSettings
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget, QFileDialog,
    QPushButton, QHBoxLayout, QSizePolicy, QApplication, QGroupBox, QGridLayout,
    QMenu, QFileDialog, QMessageBox, QProgressBar, QDialog, QLineEdit
)
from PySide6.QtGui import QIcon, QPixmap, QColor
from .export import ExportDialog

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

try:
    from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_left_panel
    from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_right_panel
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

class NanoVNAGraphics(QMainWindow):
    def __init__(self, s11=None, s21=None, freqs=None, left_graph_type="Smith Diagram", left_s_param="S11", vna_device=None, dut=None):
        super().__init__()

        self.dut = dut

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "ui","graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.Format.IniFormat)

        # QWidget
        background_color = settings.value("Dark_Light/QWidget/background-color", "#3a3a3a")

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
            QMenu{{
                color_ {menubar_color};
                background-color_ {menu_item_color};
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
            QListWidget {{
                color: {label_color};
                background-color: transparent;
            }}

            QListView {{
                color: {label_color};
                background-color: transparent;
            }}

            QTreeView {{
                color: {label_color};
                background-color: transparent;
            }}
        """)

        # Store VNA device reference
        self.vna_device = vna_device
        
        # Log graphics window initialization
        logging.info("[graphics_window.__init__] Initializing graphics window")
        if vna_device:
            device_type = type(vna_device).__name__
            logging.info(f"[graphics_window.__init__] VNA device provided: {device_type}")
        else:
            logging.warning("[graphics_window.__init__] No VNA device provided")

        config = self._load_graph_configuration()

        self.left_graph_type  = config['graph_type_tab1']
        self.left_s_param     = config['s_param_tab1']
        self.right_graph_type = config['graph_type_tab2']
        self.right_s_param    = config['s_param_tab2']

        # --- Marker visibility flags ---
        self.show_graphic1_marker1 = True
        self.show_graphic2_marker1 = True

        self.show_graphic1_marker2 = False
        self.show_graphic2_marker2 = False

        # --- Menu ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        sweep_menu = menu_bar.addMenu("Sweep")
        calibration_menu = menu_bar.addMenu("Calibration")
        help_menu = menu_bar.addMenu("Help")

        import_touchstone_action = file_menu.addAction("Connection")
        import_touchstone_action.triggered.connect(lambda: self.open_connection_window())

        import_touchstone_action = file_menu.addAction("Import Touchstone Data (Calibration)")
        import_touchstone_action.triggered.connect(lambda: self.import_touchstone_data_calibration())

        import_touchstone_action = file_menu.addAction("Import Touchstone Data (DUT)")
        import_touchstone_action.triggered.connect(lambda: self.import_touchstone_data_dut())

        export_pdf_action =  file_menu.addAction("Export Latex PDF")
        export_pdf_action.triggered.connect(lambda: self.export_latex_pdf())

        export_touchstone_action = file_menu.addAction("Export Touchstone Data")
        export_touchstone_action.triggered.connect(lambda: self.export_touchstone_data())

        graphics_markers = edit_menu.addAction("Graphics/Markers")
        graphics_markers.triggered.connect(lambda: self.edit_graphics_markers())

#-------- Lock Markers ----------------------------------------------------------------------------#

        # config.ini
        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "ui", "graphics_windows", "ini", "config.ini")
        settings = QSettings(ruta_ini, QSettings.Format.IniFormat)

        self.markers_locked = settings.value("Markers/locked", False, type=bool)

        #self.lock_markers = edit_menu.addAction("Lock Markers ✓" if self.markers_locked else "Lock Markers")

        def toggle_markers_lock():
            self.markers_locked = not self.markers_locked
            lock_markers.setText("Lock Markers ✓" if self.markers_locked else "Lock Markers")
            settings.setValue("Markers/locked", self.markers_locked)

        #self.lock_markers.triggered.connect(toggle_markers_lock) 

#-------- Dark-light Mode ----------------------------------------------------------------------------#

        text_light_dark = settings.value("Dark_Light/text_light_dark", "text_light_dark")

        light_dark_mode = edit_menu.addAction(text_light_dark)

        self.is_dark_mode = settings.value("Dark_Light/is_dark_mode", False, type=bool)

        def toggle_menu_dark_mode():

            ui_dir = os.path.dirname(os.path.dirname(__file__))  
            ruta_ini = os.path.join(ui_dir, "ui","graphics_windows", "ini", "config.ini")

            settings = QSettings(ruta_ini, QSettings.Format.IniFormat)

            if self.is_dark_mode:
                light_dark_mode.setText("Light Mode 🔆")

                # --- QWidget ---
                settings.setValue("Dark_Light/QWidget/background-color", "#7f7f7f")

                # --- Qframe ---
                settings.setValue("Dark_Light/Qframe/background-color", "white")
                settings.setValue("Dark_Light/Qframe/color", "white")

                # --- QTabWidget pane ---
                settings.setValue("Dark_Light/QTabWidget_pane/background-color", "#6f6f6f")

                # --- QTabBar ---
                settings.setValue("Dark_Light/QTabBar/background-color", "#4d4d4d")
                settings.setValue("Dark_Light/QTabBar/color", "white")
                settings.setValue("Dark_Light/QTabBar/padding", "5px 12px")
                settings.setValue("Dark_Light/QTabBar/border", "none")
                settings.setValue("Dark_Light/QTabBar/border-top-left-radius", "6px")
                settings.setValue("Dark_Light/QTabBar/border-top-right-radius", "6px")

                # --- QTabBar selected ---
                settings.setValue("Dark_Light/QTabBar_selected/background-color", "#2b2b2b")
                settings.setValue("Dark_Light/QTabBar_selected/color", "white")

                # --- QSpinBox ---
                settings.setValue("Dark_Light/QSpinBox/color", "black")
                settings.setValue("Dark_Light/QSpinBox/background-color", "white")
                settings.setValue("Dark_Light/QSpinBox/border", "1px solid #5f5f5f")
                settings.setValue("Dark_Light/QSpinBox/border-radius", "8px")

                # --- QGroupBox title ---
                settings.setValue("Dark_Light/QGroupBox_title/color", "white")

                # --- QLabel ---
                settings.setValue("Dark_Light/QLabel/color", "white")

                # --- QLineEdit ---
                settings.setValue("Dark_Light/QLineEdit/background-color", "#6f6f6f")
                settings.setValue("Dark_Light/QLineEdit/color", "white")
                settings.setValue("Dark_Light/QLineEdit/border", "1px solid #5f5f5f")
                settings.setValue("Dark_Light/QLineEdit/border-radius", "6px")
                settings.setValue("Dark_Light/QLineEdit/padding", "4px")

                # --- QLineEdit focus ---
                settings.setValue("Dark_Light/QLineEdit_focus/background-color", "#5f5f5f")
                settings.setValue("Dark_Light/QLineEdit_focus/border", "1px solid #4d90fe")

                # --- QPushButton ---
                settings.setValue("Dark_Light/QPushButton/background-color", "#6f6f6f")
                settings.setValue("Dark_Light/QPushButton/color", "white")
                settings.setValue("Dark_Light/QPushButton/border", "1px solid #5f5f5f")
                settings.setValue("Dark_Light/QPushButton/border-radius", "6px")
                settings.setValue("Dark_Light/QPushButton/padding", "4px 10px")

                # --- QPushButton hover/pressed ---
                settings.setValue("Dark_Light/QPushButton_hover/background-color", "#4d4d4d")
                settings.setValue("Dark_Light/QPushButton_pressed/background-color", "#5c5c5c")

                # --- QPushButton disabled ---
                settings.setValue("Dark_Light/QPushButton_disabled/background-color", "#2a2a2a")
                settings.setValue("Dark_Light/QPushButton_disabled/color", "#666666")
                settings.setValue("Dark_Light/QPushButton_disabled/border", "1px solid #444444")

                # --- QMenu ---
                settings.setValue("Dark_Light/QMenu/background", "#7f7f7f")
                settings.setValue("Dark_Light/QMenu/color", "white")
                settings.setValue("Dark_Light/QMenu/border", "1px solid #6f6f6f")

                # --- QMenuBar ---
                settings.setValue("Dark_Light/QMenuBar/background-color", "#7f7f7f")
                settings.setValue("Dark_Light/QMenuBar/color", "white")

                # --- QMenuBar items ---
                settings.setValue("Dark_Light/QMenuBar_item/background", "transparent")
                settings.setValue("Dark_Light/QMenuBar_item/color", "white")
                settings.setValue("Dark_Light/QMenuBar_item/padding", "4px 10px")

                # --- QMenuBar selected item ---
                settings.setValue("Dark_Light/QMenuBar_item_selected/background-color", "#4d4d4d")

                # --- QMenu selected item ---
                settings.setValue("Dark_Light/QMenu_item_selected/background-color", "#4d4d4d")

                # --- QCombo ---

                color_text_QCombo = settings.value("Dark_Light/QComboBox/color", "white")

                self.setStyleSheet("""
                    QWidget {
                        background-color: #7f7f7f;
                    }
                    QTabWidget::pane {
                        background-color: #6f6f6f; 
                    }
                    QTabBar::tab {
                        background-color: #2b2b2b; 
                        color: white;
                        padding: 5px 12px;
                        border: none; 
                        border-top-left-radius: 6px;
                        border-top-right-radius: 6px;
                    }
                    QTabBar::tab:selected {
                        background-color: #4d4d4d;  
                        color: white;
                    }
                    QSpinBox {
                        background-color: #6f6f6f;
                        color: white;
                        border: 1px solid #5f5f5f;
                        border-radius: 8px;
                    }
                    QGroupBox:title {
                        color: white;  
                    }
                    QLabel {
                        color: white;  
                    }
                    QLineEdit {
                        background-color: #6f6f6f;
                        color: white;
                        border: 1px solid #5f5f5f;
                        border-radius: 6px;
                        padding: 4px;
                    }
                    QLineEdit:focus {
                        background-color: #5f5f5f;
                        border: 1px solid #4d90fe;
                    }

                    QPushButton {
                        background-color: #6f6f6f;
                        color: white;
                        border: 1px solid #5f5f5f;
                        border-radius: 6px;
                        padding: 4px 10px;
                    }
                    QPushButton:hover {
                        background-color: #4d4d4d;
                    }
                    QPushButton:pressed {
                        background-color: #5c5c5c;
                    }
                    QMenuBar {
                        background-color: #7f7f7f;
                        color: white;
                    }
                    QMenuBar::item {
                        background: transparent;
                        color: white;
                        padding: 4px 10px;
                    }
                    QMenuBar::item:selected {
                        background: #4d4d4d;
                    }
                    QMenu {
                        background-color: #7f7f7f;
                        color: white;
                        border: 1px solid #6f6f6f;
                    }
                    QMenu::item:selected {
                        background-color: #4d4d4d;
                    }
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

                self.is_dark_mode = False

                settings.setValue("Dark_Light/is_dark_mode", self.is_dark_mode)
                settings.setValue("Dark_Light/text_light_dark", "Light Mode 🔆")

            else:
                light_dark_mode.setText("Dark Mode 🌙")

                # --- QWidget ---
                settings.setValue("Dark_Light/QWidget/background-color", "#f0f0f0")

                # --- Qframe ---
                settings.setValue("Dark_Light/Qframe/background-color", "black")
                settings.setValue("Dark_Light/Qframe/color", "black")

                # --- QTabWidget pane ---
                settings.setValue("Dark_Light/QTabWidget_pane/background-color", "#e0e0e0")

                # --- QTabBar ---
                settings.setValue("Dark_Light/QTabBar/background-color", "#c8c8c8")
                settings.setValue("Dark_Light/QTabBar/color", "black")
                settings.setValue("Dark_Light/QTabBar/padding", "5px 12px")
                settings.setValue("Dark_Light/QTabBar/border", "none")
                settings.setValue("Dark_Light/QTabBar/border-top-left-radius", "6px")
                settings.setValue("Dark_Light/QTabBar/border-top-right-radius", "6px")

                # --- QTabBar selected ---
                settings.setValue("Dark_Light/QTabBar_selected/background-color", "#dcdcdc")
                settings.setValue("Dark_Light/QTabBar/color", "black")

                # --- QTabBar alternate background ---
                settings.setValue("Dark_Light/QTabBar/background-color", "#e0e0e0")

                # --- QSpinBox ---
                settings.setValue("Dark_Light/QSpinBox/color", "black")
                settings.setValue("Dark_Light/QSpinBox/border", "1px solid #b0b0b0")
                settings.setValue("Dark_Light/QSpinBox/border-radius", "8px")

                # --- QGroupBox title ---
                settings.setValue("Dark_Light/QGroupBox_title/color", "black")

                # --- QLabel ---
                settings.setValue("Dark_Light/QLabel/color", "black")

                # --- QLineEdit ---
                settings.setValue("Dark_Light/QLineEdit/background-color", "#ffffff")
                settings.setValue("Dark_Light/QLineEdit/color", "black")
                settings.setValue("Dark_Light/QLineEdit/border", "1px solid #b0b0b0")
                settings.setValue("Dark_Light/QLineEdit/border-radius", "6px")
                settings.setValue("Dark_Light/QLineEdit/padding", "4px")

                # --- QLineEdit focus ---
                settings.setValue("Dark_Light/QLineEdit_focus/background-color", "#f0f8ff")
                settings.setValue("Dark_Light/QLineEdit_focus/border", "1px solid #4d90fe")

                # --- QPushButton ---
                settings.setValue("Dark_Light/QPushButton/background-color", "#e0e0e0")
                settings.setValue("Dark_Light/QPushButton/color", "black")
                settings.setValue("Dark_Light/QPushButton/border", "1px solid #b0b0b0")
                settings.setValue("Dark_Light/QPushButton/border-radius", "6px")
                settings.setValue("Dark_Light/QPushButton/padding", "4px 10px")

                # --- QPushButton hover/pressed ---
                settings.setValue("Dark_Light/QPushButton_hover/background-color", "#d0d0d0")
                settings.setValue("Dark_Light/QPushButton_pressed/background-color", "#c0c0c0")

                # --- QPushButton disabled ---
                settings.setValue("Dark_Light/QPushButton_disabled/background-color", "#f5f5f5")
                settings.setValue("Dark_Light/QPushButton_disabled/color", "#a0a0a0")
                settings.setValue("Dark_Light/QPushButton_disabled/border", "1px solid #d0d0d0")

                # --- QMenu ---
                settings.setValue("Dark_Light/QMenu/background", "#f0f0f0")
                settings.setValue("Dark_Light/QMenu/color", "black")
                settings.setValue("Dark_Light/QMenu/border", "1px solid #b0b0b0")

                # --- QMenuBar ---
                settings.setValue("Dark_Light/QMenuBar/background-color", "#f0f0f0")
                settings.setValue("Dark_Light/QMenuBar/color", "black")

                # --- QMenuBar items ---
                settings.setValue("Dark_Light/QMenuBar_item/background", "transparent")
                settings.setValue("Dark_Light/QMenuBar_item/color", "black")
                settings.setValue("Dark_Light/QMenuBar_item/padding", "4px 10px")

                # --- QMenuBar selected item ---
                settings.setValue("Dark_Light/QMenuBar_item_selected/background-color", "#dcdcdc")

                # --- QMenu selected item ---
                settings.setValue("Dark_Light/QMenu_item_selected/background-color", "#dcdcdc")

                # --- QCombo ---
                settings.setValue("Dark_Light/QComboBox/color", "white")

                self.setStyleSheet("""
                    QWidget {
                        background-color: #f0f0f0;
                    }
                    QTabWidget::pane {
                        background-color: #e0e0e0; 
                    }
                    QTabBar::tab {
                        background-color: #dcdcdc;  
                        color: black;             
                        padding: 5px 12px;
                        border: none;
                        border-top-left-radius: 6px;
                        border-top-right-radius: 6px;
                    }
                    QTabBar::tab:selected {
                        background-color: #c8c8c8;  
                        color: black;
                    }
                    QSpinBox {
                        background-color: #ffffff;
                        color: black;
                        border: 1px solid #b0b0b0;
                        border-radius: 8px;
                    }
                    QGroupBox:title {
                        color: black; 
                    }
                    QLabel {
                        color: black;
                    }
                    QLineEdit {
                        background-color: #ffffff;
                        color: black;
                        border: 1px solid #b0b0b0;
                        border-radius: 6px;
                        padding: 4px;
                    }
                    QLineEdit:focus {
                        background-color: #f0f8ff;
                        border: 1px solid #4d90fe;
                    }
                    QPushButton {
                        background-color: #e0e0e0;
                        color: black;
                        border: 1px solid #b0b0b0;
                        border-radius: 6px;
                        padding: 4px 10px;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                    }
                    QPushButton:pressed {
                        background-color: #c0c0c0;
                    }
                    QMenuBar {
                        background-color: #f0f0f0;
                        color: black;
                    }
                    QMenuBar::item {
                        background: transparent;
                        color: black;
                        padding: 4px 10px;
                    }
                    QMenuBar::item:selected {
                        background: #dcdcdc;
                    }
                    QMenu {
                        background-color: #f0f0f0;
                        color: black;
                        border: 1px solid #b0b0b0;
                    }
                    QMenu::item:selected {
                        background-color: #dcdcdc;
                    }
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

                self.is_dark_mode = True

                settings.setValue("Dark_Light/is_dark_mode", self.is_dark_mode)  
                settings.setValue("Dark_Light/text_light_dark", "Dark Mode 🌙")

        light_dark_mode.triggered.connect(toggle_menu_dark_mode)

        choose_graphics = view_menu.addAction("Graphics")
        choose_graphics.triggered.connect(self.open_view)  

        sweep_options = sweep_menu.addAction("Options")
        sweep_options.triggered.connect(lambda: self.open_sweep_options())
 
        sweep_run = sweep_menu.addAction("Run Sweep")
        sweep_run.triggered.connect(lambda: self.run_sweep())

        calibrate_option = calibration_menu.addAction("Calibration Wizard")
        calibrate_option.triggered.connect(lambda: self.open_calibration_wizard())

        select_calibration = calibration_menu.addAction("Select Calibration (Kit)")
        select_calibration.triggered.connect(lambda: self.select_kit_dialog())

        sweep_load_calibration = calibration_menu.addAction("Save Calibration (Kit)")

        def handle_save_calibration(self):
            # Get path to calibration_config.ini
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
            
            settings = QSettings(config_path, QSettings.Format.IniFormat)
            settings.sync()

            # Read values from INI
            kits_ok = settings.value("Calibration/Kits", False, type=bool)
            no_calibration = settings.value("Calibration/NoCalibration", False, type=bool)

            # Check if calibration was performed from scratch
            if not kits_ok and not no_calibration:
                # Calibration was done from scratch → execute save
                self.save_kit_dialog()
            else:
                # Calibration was not done from scratch → show warning
                self.show_calibration_warning()

        # Connect the action to the handler
        sweep_load_calibration.triggered.connect(lambda: handle_save_calibration(self))

        delete_calibration = calibration_menu.addAction("Delete Calibration (Kit)")
        delete_calibration.triggered.connect(lambda: self.delete_kit_dialog())

        # --- Icon ---
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
        else:
            logger = logging.getLogger(__name__)
            logger.warning("icon.ico not found in expected locations")

        
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

        self.setWindowTitle("NanoVNA Graphics")
        self.setGeometry(100, 100, 1300, 700)

        # Auto-run sweep if device is available and connected
        if self.vna_device:
            device_type = type(self.vna_device).__name__
            is_connected = self.vna_device.connected()
            logging.info(f"[graphics_window.__init__] Device {device_type} connection status: {is_connected}")
            
            if not is_connected:
                logging.warning(f"[graphics_window.__init__] Device {device_type} not connected, attempting to reconnect...")
                try:
                    self.vna_device.connect()
                    is_connected = self.vna_device.connected()
                    logging.info(f"[graphics_window.__init__] Reconnection result: {is_connected}")
                except Exception as e:
                    logging.error(f"[graphics_window.__init__] Failed to reconnect device: {e}")
                    
            if is_connected:
                logging.info("[graphics_window.__init__] Device ready - scheduling auto-sweep")
                QTimer.singleShot(1000, self.run_sweep)  # Delay to allow UI to load
            else:
                logging.warning("[graphics_window.__init__] Device not available for auto-sweep")
        else:
            logging.warning("[graphics_window.__init__] No VNA device provided for auto-sweep")

        # --- Central widget ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout_vertical = QVBoxLayout(central_widget)
        self.main_layout_vertical.setContentsMargins(10, 10, 10, 10)
        self.main_layout_vertical.setSpacing(10)

        # --- Sweep Control Button ---
        sweep_control_layout = QHBoxLayout()
        
        # Reconnect button
        self.reconnect_button = QPushButton("Reconnect")
        self.reconnect_button.setMaximumWidth(100)
        self.reconnect_button.clicked.connect(self.reconnect_device)
        # No custom stylesheet - use standard button style like "Run Sweep"
        
        # Sweep button
        self.sweep_button = QPushButton("Run Sweep")
        self.sweep_button.setMaximumWidth(120)
        self.sweep_button.clicked.connect(self.run_sweep)
        
        self.sweep_info_label = QLabel("Sweep: 0.050 MHz - 1500.000 MHz, 101 points")
        self.sweep_info_label.setStyleSheet("font-size: 12px;")

        # Initialize sweep configuration and auto-run sweep
        self.load_sweep_configuration()
        
        # Add progress bar (initially hidden)
        self.sweep_progress_bar = QProgressBar()
        self.sweep_progress_bar.setMaximumWidth(200)
        self.sweep_progress_bar.setVisible(False)
        self.sweep_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        sweep_control_layout.addWidget(self.reconnect_button)
        sweep_control_layout.addWidget(self.sweep_button)
        sweep_control_layout.addWidget(self.sweep_info_label)
        sweep_control_layout.addWidget(self.sweep_progress_bar)
        sweep_control_layout.addStretch()

        # Creamos el QLabel de calibración como atributo de la clase
        self.calibration_label = QLabel()
        self.calibration_label.setStyleSheet("font-size: 12px;")
        sweep_control_layout.addWidget(self.calibration_label, alignment=Qt.AlignRight)

        # Inicializa el texto del label
        self.update_calibration_label_from_method()

        self.main_layout_vertical.addLayout(sweep_control_layout)
        
        # Set initial state of reconnect button after UI elements are created
        self._update_reconnect_button_state()

        # --- Initialize data arrays ---
        # Force everything to None for initial empty state
        self.freqs = None
        self.s11 = None 
        self.s21 = None
        
        # Log that plots will be empty until sweep is performed
        logging.info("[graphics_window.__init__] Initializing with empty plots - data will be loaded after first sweep")

        self.left_graph_type = left_graph_type
        self.left_s_param = left_s_param

        # =================== LEFT PANEL (EMPTY) ===================
        self.left_panel, self.info_panel_left, self.info_panel_left_2, self.fig_left, self.ax_left, self.canvas_left, \
        self.slider_left, self.slider_left_2, self.cursor_left, self.cursor_left_2, self.labels_left, self.labels_left_2, self.update_cursor, self.update_cursor_2, self.update_left_data = \
            create_left_panel(
                self,
                S_data=None,  # Force empty 
                freqs=None,   # Force empty
                settings=settings,
                graph_type=config['graph_type_tab1'], 
                s_param=config['s_param_tab1'], 
                tracecolor=config['trace_color1'],
                markercolor=config['marker_color1'],
                marker2color=config['marker_color2'],
                linewidth=config['trace_size1'],
                markersize=config['marker_size1'], 
                marker2size=config['marker_size2']  
            )

        # =================== RIGHT PANEL (EMPTY) ===================
        self.right_panel, self.info_panel_right, self.info_panel_right_2, self.fig_right, self.ax_right, self.canvas_right, \
        self.slider_right, self.slider_right_2, self.cursor_right, self.cursor_right_2, self.labels_right, self.labels_right_2, self.update_right_cursor, self.update_right_cursor_2, self.update_right_data = \
            create_right_panel(
                self,
                settings=settings,
                S_data=None,  # Force empty
                freqs=None,   # Force empty
                graph_type=config['graph_type_tab2'], 
                s_param=config['s_param_tab2'],
                tracecolor=config['trace_color2'],
                markercolor=config['marker_color2'],
                marker2color=config['marker2_color2'],
                linewidth=config['trace_size2'],
                markersize=config['marker_size2'],
                marker2size=config['marker2_size2']
            )

        self._update_cursor_orig = self.update_cursor 
        self._update_cursor_2_orig = self.update_cursor_2

        self._update_cursor_right_orig = self.update_right_cursor 
        self._update_cursor_2_right_orig = self.update_right_cursor_2

        # =================== PANELS LAYOUT ===================

        panels_layout = QHBoxLayout()

        while panels_layout.count():
            item = panels_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        panels_layout.addWidget(self.left_panel, 1)
        panels_layout.addWidget(self.right_panel, 1)
        self.main_layout_vertical.addLayout(panels_layout)

        self.markers_button = QPushButton("Markers Diff")
        self.markers_button_layout = QHBoxLayout()
        self.markers_button_layout.addStretch()
        self.markers_button_layout.addWidget(self.markers_button)
        self.markers_button_layout.addStretch()
        self.main_layout_vertical.addLayout(self.markers_button_layout)

        self.markers = [
            {"cursor": self.cursor_left, "cursor_2": self.cursor_left_2, "slider": self.slider_left, "slider_2": self.slider_left_2, "label": self.labels_left, "label_2": self.labels_left_2, "update_cursor": self.update_cursor, "update_cursor_2": self.update_cursor_2},
            {"cursor": self.cursor_right, "cursor_2": self.cursor_right_2, "slider": self.slider_right, "slider_2": self.slider_right_2, "label": self.labels_right, "label_2": self.labels_right_2, "update_cursor": self.update_right_cursor, "update_cursor_2": self.update_right_cursor_2}
        ]
        
        self.markers_button.clicked.connect(self.show_frequency_difference_dialog)
        self.markers_button.hide()
        
        # Clear all marker information fields until first sweep is completed
        self._clear_all_marker_fields()
        
        # Initialize exporters
        self.latex_exporter = LatexExporter(parent_widget=self)
        self.touchstone_exporter = TouchstoneExporter(parent_widget=self)

    def update_calibration_label_from_method(self, method=None):

        import configparser
    
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")

        parser = configparser.ConfigParser()
        parser.read(config_path)  

        kits_ok = parser.getboolean("Calibration", "Kits", fallback=False)
        no_calibration = parser.getboolean("Calibration", "NoCalibration", fallback=False)
        calibration_method = method or parser.get("Calibration", "Method", fallback="---")

        # Use new calibration structure
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
        settings_calibration = QSettings(config_path, QSettings.Format.IniFormat)

        is_import_dut = settings_calibration.value("Calibration/isImportDut", False, type=bool)

        if no_calibration and method == None and not is_import_dut:
            text = "No Calibration"
        elif kits_ok and not no_calibration and method == None and not is_import_dut:
            selected_full_name = parser.get("Calibration", "Name", fallback="Unknown")
            selected_kit_name = "_".join(selected_full_name.split("_")[:-1])
            kit_found = False
            i = 1
            while f"Kit_{i}" in parser:
                kit_name = parser.get(f"Kit_{i}", "kit_name", fallback=None)
                method_kit = parser.get(f"Kit_{i}", "method", fallback=None)
                if kit_name == selected_kit_name:
                    text = f"Calibration Kit | Name: {kit_name} and Method: {method_kit}"
                    kit_found = True
                    break
                i += 1
            if not kit_found:
                text = f"Calibration Kit: {selected_kit_name or 'Unknown'} (method not found)"
        elif not is_import_dut:
            text = f"Calibration Wizard | Method: {calibration_method}"
        elif is_import_dut:
            text = f"DUT"

        self.calibration_label.setText(text)

    def load_latest_osm_calibration(self):
        # OSM
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_dir = os.path.join(base_dir, "calibration", "config")
            
            if not os.path.exists(config_dir):
                return
            
            # Buscar archivos .cal
            cal_files = []
            for file in os.listdir(config_dir):
                if file.endswith('.cal') and 'OSM' in file:
                    file_path = os.path.join(config_dir, file)
                    cal_files.append((file_path, os.path.getmtime(file_path), file))
            
            if cal_files:
                # Ordenar por fecha de modificación (más reciente primero)
                cal_files.sort(key=lambda x: x[1], reverse=True)
                latest_file = cal_files[0]
                
                # Extraer nombre de calibración del archivo
                cal_name = os.path.splitext(latest_file[2])[0]
                
                # Actualizar la label
                self.update_calibration_label_from_method("OSM", cal_name)
                
                logging.info(f"[GraphicsWindow] Loaded latest OSM calibration: {cal_name}")
                
        except Exception as e:
            logging.error(f"[GraphicsWindow] Error loading latest calibration: {e}")

    def _load_graph_configuration(self):
        """Load graph configuration from settings file."""
        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.Format.IniFormat)

        return {
            'graph_type_tab1': settings.value("Tab1/GraphType1", "Smith Diagram"),
            's_param_tab1': settings.value("Tab1/SParameter", "S11"),
            'graph_type_tab2': settings.value("Tab2/GraphType2", "Magnitude"),
            's_param_tab2': settings.value("Tab2/SParameter", "S11"),
            'trace_color1': settings.value("Graphic1/TraceColor", "blue"),
            'marker_color1': settings.value("Graphic1/MarkerColor1", "blue"),
            'marker2_color1': settings.value("Graphic1/MarkerColor2", "blue"),
            'trace_size1': int(settings.value("Graphic1/TraceWidth", 2)),
            'marker_size1': int(settings.value("Graphic1/MarkerWidth1", 6)),
            'marker2_size1': int(settings.value("Graphic1/MarkerWidth2", 6)),
            'trace_color2': settings.value("Graphic2/TraceColor", "blue"),
            'marker_color2': settings.value("Graphic2/MarkerColor1", "blue"),
            'marker2_color2': settings.value("Graphic2/MarkerColor2", "blue"),
            'trace_size2': int(settings.value("Graphic2/TraceWidth", 2)),
            'marker_size2': int(settings.value("Graphic2/MarkerWidth1", 6)),
            'marker2_size2': int(settings.value("Graphic2/MarkerWidth2", 6))
        }

    def _clear_panel_labels(self, panel_side='left'):
        """Clear all labels for a specific panel (left or right)."""
        if panel_side == 'left' and hasattr(self, 'labels_left') and self.labels_left:
            if panel_side == 'left' and hasattr(self, 'labels_left') and self.labels_left:
                # allow "--" temporarily
                self.labels_left.get("freq") and self.labels_left["freq"].setText("--")
                self.labels_right["freq"].deselect()
                self.labels_right["freq"].clearFocus()
            self.labels_left.get("val") and self.labels_left["val"].setText(f"{self.left_s_param}: -- + j--")
            self.labels_left.get("mag") and self.labels_left["mag"].setText(f"|{self.left_s_param}|: --")
            self.labels_left.get("phase") and self.labels_left["phase"].setText("Phase: --")
            self.labels_left.get("z") and self.labels_left["z"].setText("Zin (Z0): -- + j--")
            self.labels_left.get("il") and self.labels_left["il"].setText("IL: --")
            self.labels_left.get("vswr") and self.labels_left["vswr"].setText("VSWR: --")
        elif panel_side == 'right' and hasattr(self, 'labels_right') and self.labels_right:
            if panel_side == 'left' and hasattr(self, 'labels_left') and self.labels_left:
                # allow "--" temporarily
                self.labels_left.get("freq") and self.labels_left["freq"].setText("--")
                self.labels_right["freq"].deselect()
                self.labels_right["freq"].clearFocus()
            self.labels_right.get("val") and self.labels_right["val"].setText(f"{self.right_s_param}: -- + j--")
            self.labels_right.get("mag") and self.labels_right["mag"].setText(f"|{self.right_s_param}|: --")
            self.labels_right.get("phase") and self.labels_right["phase"].setText("Phase: --")
            self.labels_right.get("z") and self.labels_right["z"].setText("Zin (Z0): -- + j--")
            self.labels_right.get("il") and self.labels_right["il"].setText("IL: --")
            self.labels_right.get("vswr") and self.labels_right["vswr"].setText("VSWR: --")

        if panel_side == 'left' and hasattr(self, 'labels_left_2') and self.labels_left_2:
            if panel_side == 'left' and hasattr(self, 'labels_left_2') and self.labels_left_2:
                # allow "--" temporarily
                self.labels_left_2.get("freq") and self.labels_left_2["freq"].setText("--")
                self.labels_right_2["freq"].deselect()
                self.labels_right_2["freq"].clearFocus()
            self.labels_left_2.get("val") and self.labels_left_2["val"].setText(f"{self.left_s_param}: -- + j--")
            self.labels_left_2.get("mag") and self.labels_left_2["mag"].setText(f"|{self.left_s_param}|: --")
            self.labels_left_2.get("phase") and self.labels_left_2["phase"].setText("Phase: --")
            self.labels_left_2.get("z") and self.labels_left_2["z"].setText("Zin (Z0): -- + j--")
            self.labels_left_2.get("il") and self.labels_left_2["il"].setText("IL: --")
            self.labels_left_2.get("vswr") and self.labels_left_2["vswr"].setText("VSWR: --")
        elif panel_side == 'right' and hasattr(self, 'labels_right_2') and self.labels_right_2:
            if panel_side == 'left' and hasattr(self, 'labels_left_2') and self.labels_left_2:
                # allow "--" temporarily
                self.labels_left_2.get("freq") and self.labels_left_2["freq"].setText("--")
                self.labels_right_2["freq"].deselect()
                self.labels_right_2["freq"].clearFocus()
            self.labels_right_2.get("val") and self.labels_right_2["val"].setText(f"{self.right_s_param}: -- + j--")
            self.labels_right_2.get("mag") and self.labels_right_2["mag"].setText(f"|{self.right_s_param}|: --")
            self.labels_right_2.get("phase") and self.labels_right_2["phase"].setText("Phase: --")
            self.labels_right_2.get("z") and self.labels_right_2["z"].setText("Zin (Z0): -- + j--")
            self.labels_right_2.get("il") and self.labels_right_2["il"].setText("IL: --")
            self.labels_right_2.get("vswr") and self.labels_right_2["vswr"].setText("VSWR: --")

    def _clear_axis_and_show_message(self, panel_side='right', message_pos=(0.5, 0.5)):
        """Clear axis and show waiting message for a specific panel."""
        if panel_side == 'right':
            if hasattr(self, 'ax_right') and self.ax_right:
                self.ax_right.text(
                    message_pos[0], message_pos[1],
                    r"$\mathrm{Waiting\ for\ sweep\ data\ ...}$",
                    transform=self.ax_right.transAxes,
                    ha='center', va='center',
                    fontsize=15, color='white'
                )

                for line in self.ax_right.lines:
                    line.remove()

                self.ax_right.grid(False)

            if hasattr(self, 'canvas_right') and self.canvas_right:
                self.canvas_right.draw()
        elif panel_side == 'left':
            if hasattr(self, 'ax_left') and self.ax_left:
                self.ax_left.text(
                    message_pos[0], message_pos[1],
                    r"$\mathrm{Waiting\ for\ sweep\ data\ ...}$",
                    transform=self.ax_left.transAxes,
                    ha='center', va='center',
                    fontsize=15, color='white'
                )

                for line in self.ax_left.lines:
                    line.remove()

                self.ax_left.grid(False)

            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw()

    def _clear_all_marker_fields(self):
        """Clear marker values but keep all panels and labels intact."""
        logging.info("[graphics_window._clear_all_marker_fields] Clearing marker values but keeping layout intact")

        config = self._load_graph_configuration()
        graph_type_tab1 = config['graph_type_tab1']
        graph_type_tab2 = config['graph_type_tab2']

        if graph_type_tab1 == "Smith Diagram":

            # Left panel
            self._clear_panel_labels('left')

            # Hide cursors
            if hasattr(self, 'cursor_left') and self.cursor_left:
                self.cursor_left.set_visible(False)

            if hasattr(self, 'cursor_left_2') and self.cursor_left_2:
                self.cursor_left_2.set_visible(False)
            
            # Clear axes but keep empty plot with message
            if hasattr(self, 'ax_left') and self.ax_left:
                #self.ax_left.clear()
                self.ax_left.text(
                    0.5, -0.1,
                    r"$\mathrm{Waiting\ for\ sweep\ data\ ...}$",
                    transform=self.ax_left.transAxes,
                    ha='center', va='center',
                    fontsize=15, color='white'
                )

                for line in self.ax_left.lines:
                    line.remove()

                self.ax_left.grid(False)

            # Redraw
            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw()
           
        if graph_type_tab2 == "Smith Diagram":

            # Right panel
            self._clear_panel_labels('right')

            if hasattr(self, 'cursor_right') and self.cursor_right:
                self.cursor_right.set_visible(False)
            
            if hasattr(self, 'cursor_right_2') and self.cursor_right_2:
                self.cursor_right_2.set_visible(False)

            self._clear_axis_and_show_message('right', (0.5, -0.1))

        if graph_type_tab1 == "Magnitude" or graph_type_tab1 == "Phase":
            # Left panel
            self._clear_panel_labels('left')

            # Hide cursors
            if hasattr(self, 'cursor_left') and self.cursor_left:
                self.cursor_left.set_visible(False)

            # Hide cursors
            if hasattr(self, 'cursor_left_2') and self.cursor_left_2:
                self.cursor_left_2.set_visible(False)

            # Clear axes but keep empty plot with message
            if hasattr(self, 'ax_left') and self.ax_left:
                self.ax_left.text(
                    0.5, 0.5,
                    r"$\mathrm{Waiting\ for\ sweep\ data\ ...}$",
                    transform=self.ax_left.transAxes,
                    ha='center', va='center',
                    fontsize=15, color='white'
                )

                for line in self.ax_left.lines:
                    line.remove()

                self.ax_left.grid(False)

            # Redraw
            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw()

        if graph_type_tab2 == "Magnitude" or graph_type_tab2 == "Phase":

            # Right panel
            self._clear_panel_labels('right')

            if hasattr(self, 'cursor_right_2') and self.cursor_right:
                self.cursor_right.set_visible(False)

            if hasattr(self, 'cursor_right_2') and self.cursor_right_2:
                self.cursor_right_2.set_visible(False)

            self._clear_axis_and_show_message('right', (0.5, 0.5))


    def _reset_markers_after_sweep(self):
        """Reset markers and all marker-dependent information after a sweep completes."""
        logging.info("[graphics_window._reset_markers_after_sweep] Resetting markers after sweep completion")
        
        try:
            # Reset slider positions to leftmost position (index 0) if they exist
            if hasattr(self, 'slider_left') and self.slider_left:
                # Reset left slider to leftmost position
                try:
                    self.slider_left.set_val(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Reset left slider to index 0 (leftmost)")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not reset left slider: {e}")

            if hasattr(self, 'slider_left_2') and self.slider_left_2:
                # Reset left slider to leftmost position
                try:
                    self.slider_left_2.set_val(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Reset left slider_2 to index 0 (leftmost)")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not reset left slider: {e}")
            
            if hasattr(self, 'slider_right') and self.slider_right:
                # Reset right slider to leftmost position  
                try:
                    self.slider_right.set_val(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Reset right slider to index 0 (leftmost)")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not reset right slider: {e}")

            if hasattr(self, 'slider_right_2') and self.slider_right_2:
                # Reset right slider to leftmost position  
                try:
                    self.slider_right_2.set_val(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Reset right slider to index 0 (leftmost)")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not reset right slider: {e}")
            
            
            # Reset ONLY marker field information - NOT the graphs themselves
            self._clear_marker_fields_only()
            
            # Update slider ranges to match the new sweep data
            self._update_slider_ranges()
            
            # Force cursor position updates if update functions exist
            if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                try:
                    # Always set cursor to leftmost position (index 0)
                    self.update_cursor(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Updated left cursor to index 0 (leftmost)")
                    
                    # Force cursor visibility and redraw after data update
                    if hasattr(self, 'cursor_left') and self.cursor_left and self.show_graphic1_marker1:
                        self.cursor_left.set_visible(True)
                        if hasattr(self.cursor_left, 'get_data'):
                            x_data, y_data = self.cursor_left.get_data()
                            logging.info(f"[graphics_window._reset_markers_after_sweep] Left cursor after update: x={x_data}, y={y_data}")

                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not update left cursor: {e}")

            if hasattr(self, 'update_cursor_2') and callable(self.update_cursor_2):
                try:
                    # Always set cursor to leftmost position (index 0)
                    self.update_cursor_2(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Updated left cursor to index 0 (leftmost)")
                    
                    # Force cursor visibility and redraw after data update
                    if hasattr(self, 'cursor_left_2') and self.cursor_left_2 and self.show_graphic1_marker2:
                        self.cursor_left_2.set_visible(True)
                        if hasattr(self.cursor_left_2, 'get_data'):
                            x_data, y_data = self.cursor_left_2.get_data()
                            logging.info(f"[graphics_window._reset_markers_after_sweep] Left cursor after update 2: x={x_data}, y={y_data}")
                        
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not update left cursor: {e}")
            
            if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                try:
                    # Always set cursor to leftmost position (index 0)
                    self.update_right_cursor(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Updated right cursor to index 0 (leftmost)")
                    
                    # Force cursor visibility and redraw after data update
                    if hasattr(self, 'cursor_right') and self.cursor_right and self.show_graphic2_marker1:
                        self.cursor_right.set_visible(True)
                        if hasattr(self.cursor_right, 'get_data'):
                            x_data, y_data = self.cursor_right.get_data()
                            logging.info(f"[graphics_window._reset_markers_after_sweep] Right cursor after update: x={x_data}, y={y_data}")
                        
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not update right cursor: {e}")

            if hasattr(self, 'update_right_cursor_2') and callable(self.update_right_cursor_2):
                try:
                    # Always set cursor to leftmost position (index 0)
                    self.update_right_cursor_2(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Updated right cursor_2 to index 0 (leftmost)")
                    
                    # Force cursor visibility and redraw after data update
                    if hasattr(self, 'cursor_right_2') and self.cursor_right_2 and self.show_graphic2_marker2:
                        self.cursor_right_2.set_visible(True)
                        if hasattr(self.cursor_right_2, 'get_data'):
                            x_data, y_data = self.cursor_right_2.get_data()
                            logging.info(f"[graphics_window._reset_markers_after_sweep] Right cursor after update: x={x_data}, y={y_data}")
                        
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not update right cursor: {e}")
                    
            # Final forced redraw with explicit visibility check
            try:
                # Force canvas redraw to show the cursors with their new data
                if hasattr(self, 'canvas_left') and self.canvas_left:
                    self.canvas_left.draw()  # Use draw() instead of draw_idle() for immediate effect
                    logging.info("[graphics_window._reset_markers_after_sweep] Forced left canvas redraw")
                if hasattr(self, 'canvas_right') and self.canvas_right:
                    self.canvas_right.draw()  # Use draw() instead of draw_idle() for immediate effect
                    logging.info("[graphics_window._reset_markers_after_sweep] Forced right canvas redraw")
                    
            except Exception as e:
                logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not force canvas redraw: {e}")
                    
            # Force marker information update after everything is set up
            # Use QTimer to ensure all cursor recreation is complete before updating info
            def force_cursor_info_update():
                try:
                    if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                        self.update_cursor(0)
                        logging.info("[graphics_window._reset_markers_after_sweep] DELAYED: Updated left cursor info to index 0")

                    if hasattr(self, 'update_cursor_2') and callable(self.update_cursor_2):
                        self.update_cursor_2(0)
                        logging.info("[graphics_window._reset_markers_after_sweep] DELAYED: Updated left 2 cursor info to index 0")
                    
                    if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                        self.update_right_cursor(0)
                        logging.info("[graphics_window._reset_markers_after_sweep] DELAYED: Updated right cursor info to index 0")

                    if hasattr(self, 'update_right_cursor_2') and callable(self.update_right_cursor_2):
                        self.update_right_cursor_2(0)
                        logging.info("[graphics_window._reset_markers_after_sweep] DELAYED: Updated right cursor info to index 0")
                        
                    # Force final canvas redraw
                    if hasattr(self, 'canvas_left') and self.canvas_left:
                        self.canvas_left.draw()
                    if hasattr(self, 'canvas_right') and self.canvas_right:
                        self.canvas_right.draw()
                        
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Error in delayed cursor update: {e}")
            
            # Execute the delayed update after 100ms to ensure cursor recreation is complete
            QTimer.singleShot(100, force_cursor_info_update)
                    
            # Force marker visibility with debug AND fix cursor references
            self._force_marker_visibility()
            self._force_marker_visibility_2()
                    
            logging.info("[graphics_window._reset_markers_after_sweep] Marker reset completed successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window._reset_markers_after_sweep] Error resetting markers: {e}")


    def _recreate_cursors_for_new_plots(self, marker_color_left, marker_color_right, 
        marker2_color_left, marker2_color_right, marker1_size_left, marker1_size_right, marker2_size_left, marker2_size_right):
        """Recreate cursors when the plot type changes."""
        try:
            logging.info("[graphics_window._recreate_cursors_for_new_plots] Recreating cursors for plot type changes")
            
            # Clear any existing wrapper functions
            if hasattr(self, '_original_update_cursor'):
                self.update_cursor = self._original_update_cursor
                delattr(self, '_original_update_cursor')
            if hasattr(self, '_original_update_cursor_2'):
                self.update_cursor_2 = self._original_update_cursor_2
                delattr(self, '_original_update_cursor_2')
            if hasattr(self, '_original_update_right_cursor'):
                self.update_right_cursor = self._original_update_right_cursor
                delattr(self, '_original_update_right_cursor')
            if hasattr(self, '_original_update_right_cursor_2'):
                self.update_right_cursor_2 = self._original_update_right_cursor_2
                delattr(self, '_original_update_right_cursor_2')
            
            # Remove existing cursors from axes
            if hasattr(self, 'cursor_left') and self.cursor_left:
                try:
                    self.cursor_left.remove()
                except:
                    pass
                self.cursor_left = None

            if hasattr(self, 'cursor_left_2') and self.cursor_left_2:
                try:
                    self.cursor_left_2.remove()
                except:
                    pass
                self.cursor_left_2 = None
                
            if hasattr(self, 'cursor_right') and self.cursor_right:
                try:
                    self.cursor_right.remove()
                except:
                    pass
                self.cursor_right = None

            if hasattr(self, 'cursor_right_2') and self.cursor_right_2:
                try:
                    self.cursor_right_2.remove()
                except:
                    pass
                self.cursor_right_2 = None
            
            # Create new cursors at position (0,0) - they will be positioned correctly later
            # Make them invisible initially to avoid the "fixed cursor" problem
            if hasattr(self, 'ax_left') and self.ax_left:
                self.cursor_left = self.ax_left.plot(0, 0, 'o', color=marker_color_left, markersize=marker1_size_left, 
                                                    markeredgecolor='darkred', markeredgewidth=2, visible=False)[0]

            if hasattr(self, 'ax_left') and self.ax_left:
                self.cursor_left_2 = self.ax_left.plot(0, 0, 'o', color=marker_color_left, markersize=5, 
                                                    markeredgecolor='darkred', markeredgewidth=2, visible=False)[0]
            
            if hasattr(self, 'ax_right') and self.ax_right:
                self.cursor_right = self.ax_right.plot(0, 0, 'o', color=marker_color_right, markersize=marker1_size_right, 
                                                      markeredgecolor='darkred', markeredgewidth=2, visible=False)[0]

            if hasattr(self, 'ax_right') and self.ax_right:
                self.cursor_right_2 = self.ax_right.plot(0, 0, 'o', color=marker_color_right, markersize=5, 
                                                      markeredgecolor='darkred', markeredgewidth=2, visible=False)[0]
            
            # Update markers list with new cursor references
            if hasattr(self, 'markers') and self.markers:
                if len(self.markers) >= 1 and self.markers[0]:
                    self.markers[0]['cursor'] = self.cursor_left
                if len(self.markers) >= 1 and self.markers[0]:
                    self.markers[0]['cursor_2'] = self.cursor_left_2
                if len(self.markers) >= 2 and self.markers[1]:
                    self.markers[1]['cursor'] = self.cursor_right
                if len(self.markers) >= 2 and self.markers[1]:
                    self.markers[1]['cursor_2'] = self.cursor_right_2
            
            # Force marker visibility setup to create the wrapper functions again
            self._force_marker_visibility(marker_color_left=marker_color_left, marker_color_right=marker_color_right, 
                marker1_size_left=marker1_size_left, marker1_size_right=marker1_size_right)

            self._force_marker_visibility_2(marker_color_left=marker2_color_left, marker_color_right=marker2_color_right,
                marker_size_left=marker2_size_left, marker_size_right=marker2_size_right)
            
            logging.info("[graphics_window._recreate_cursors_for_new_plots] Cursors recreated successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window._recreate_cursors_for_new_plots] Error recreating cursors: {e}")

    def _reset_sliders_and_markers_for_graph_change(self):
        """Reset sliders and markers to leftmost position specifically for graph type changes."""
        try:
            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Resetting sliders and markers for graph change")
            
            # Reset slider positions to leftmost position (index 0)
            if hasattr(self, 'slider_left') and self.slider_left:
                try:
                    self.slider_left.set_val(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Reset left slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not reset left slider: {e}")

            if hasattr(self, 'slider_left_2') and self.slider_left_2:
                try:
                    self.slider_left_2.set_val(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Reset left slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not reset left slider: {e}")
            
            if hasattr(self, 'slider_right') and self.slider_right:
                try:
                    self.slider_right.set_val(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Reset right slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not reset right slider: {e}")
            if hasattr(self, 'slider_right_2') and self.slider_right_2:
                try:
                    self.slider_right_2.set_val(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Reset right slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not reset right slider: {e}")
            
            # Clear marker information fields
            self._clear_marker_fields_only()
            
            # Force cursor position updates to leftmost position (index 0)
            if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                try:
                    self.update_cursor(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Updated left cursor to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not update left cursor: {e}")
            if hasattr(self, 'update_cursor_2') and callable(self.update_cursor_2):
                try:
                    self.update_cursor_2(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Updated left cursor to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not update left cursor: {e}")
            
            if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                try:
                    self.update_right_cursor(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Updated right cursor to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not update right cursor: {e}")
            if hasattr(self, 'update_right_cursor_2') and callable(self.update_right_cursor_2):
                try:
                    self.update_right_cursor_2(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Updated right cursor to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not update right cursor: {e}")
            
            
            # Make cursors visible
            if hasattr(self, 'cursor_left') and self.cursor_left:
                self.cursor_left.set_visible(True)
            if hasattr(self, 'cursor_left_2') and self.cursor_left_2:
                self.cursor_left_2.set_visible(True)
            if hasattr(self, 'cursor_right') and self.cursor_right:
                self.cursor_right.set_visible(True)
            if hasattr(self, 'cursor_right_2') and self.cursor_right_2:
                self.cursor_right_2.set_visible(True)
            
            # Force marker information update after everything is set up (for graph changes)
            def force_cursor_info_update_graph_change():
                try:
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Starting forced cursor info update")
                    
                    # Ensure sliders are at position 0 first
                    if hasattr(self, 'slider_left') and self.slider_left:
                        try:
                            self.slider_left.set_val(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Ensured left slider at position 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Could not set left slider: {e}")

                    if hasattr(self, 'slider_left_2') and self.slider_left_2:
                        try:
                            self.slider_left_2.set_val(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Ensured left slider at position 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Could not set left slider: {e}")
                    
                    if hasattr(self, 'slider_right') and self.slider_right:
                        try:
                            self.slider_right.set_val(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Ensured right slider at position 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Could not set right slider: {e}")

                    if hasattr(self, 'slider_right_2') and self.slider_right_2:
                        try:
                            self.slider_right_2.set_val(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Ensured right slider at position 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Could not set right slider: {e}")
                    
                    # Force cursor information update
                    if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                        try:
                            self.update_cursor(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Updated left cursor info to index 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Error updating left cursor: {e}")

                    if hasattr(self, 'update_cursor_2') and callable(self.update_cursor_2):
                        try:
                            self.update_cursor_2(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Updated left cursor info to index 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Error updating left cursor: {e}")
                    
                    if hasattr(self, 'update_right_cursor_2') and callable(self.update_right_cursor_2):
                        try:
                            self.update_right_cursor_2(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Updated right cursor info to index 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Error updating right cursor: {e}")
                    
                    # Force canvas redraw to ensure visual update
                    if hasattr(self, 'canvas_left') and self.canvas_left:
                        self.canvas_left.draw()
                    if hasattr(self, 'canvas_right') and self.canvas_right:
                        self.canvas_right.draw()
                    
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Cursor info update completed")
                        
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Error in delayed cursor update: {e}")
            
            # Execute the delayed update after 150ms for graph changes (increased delay)
            QTimer.singleShot(150, force_cursor_info_update_graph_change)
            
            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Sliders and markers reset successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Error resetting sliders and markers: {e}")

    def _reset_sliders_before_sweep(self):
        """Reset sliders and CLEAR all cursor information before starting a sweep."""
        try:
            logging.info("[graphics_window._reset_sliders_before_sweep] Resetting sliders and clearing info before sweep starts")
            
            # Reset slider positions to leftmost position (index 0)
            if hasattr(self, 'slider_left') and self.slider_left:
                try:
                    self.slider_left.set_val(0)
                    logging.info("[graphics_window._reset_sliders_before_sweep] Reset left slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_before_sweep] Could not reset left slider: {e}")

            if hasattr(self, 'slider_left_2') and self.slider_left_2:
                try:
                    self.slider_left_2.set_val(0)
                    logging.info("[graphics_window._reset_sliders_before_sweep] Reset left slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_before_sweep] Could not reset left slider: {e}")
            
            if hasattr(self, 'slider_right') and self.slider_right:
                try:
                    self.slider_right.set_val(0)
                    logging.info("[graphics_window._reset_sliders_before_sweep] Reset right slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_before_sweep] Could not reset right slider: {e}")
            
            if hasattr(self, 'slider_right_2') and self.slider_right_2:
                try:
                    self.slider_right_2.set_val(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Ensured right slider at position 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Could not set right slider: {e}")
            
            # CLEAR all marker information (DO NOT update cursor info - just clear it)
            self._clear_all_marker_fields()
            logging.info("[graphics_window._reset_sliders_before_sweep] Cleared all marker information display")
                    
            logging.info("[graphics_window._reset_sliders_before_sweep] Sliders reset and info cleared before sweep")
            
        except Exception as e:
            logging.error(f"[graphics_window._reset_sliders_before_sweep] Error resetting sliders before sweep: {e}")

    def _reset_sliders_after_reconnect(self):
        """Reset sliders and show cursor information after successful device reconnection."""
        try:
            logging.info("[graphics_window._reset_sliders_after_reconnect] Resetting sliders after successful reconnection")
            
            # Only reset if we have data available
            if not (hasattr(self, 'freqs') and self.freqs is not None and len(self.freqs) > 0):
                logging.info("[graphics_window._reset_sliders_after_reconnect] No sweep data available, skipping reset")
                return
            
            # Reset slider positions to leftmost position (index 0)
            if hasattr(self, 'slider_left') and self.slider_left:
                try:
                    self.slider_left.set_val(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Reset left slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not reset left slider: {e}")

            if hasattr(self, 'slider_left_2') and self.slider_left_2:
                try:
                    self.slider_left_2.set_val(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Reset left slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not reset left slider: {e}")
            
            
            if hasattr(self, 'slider_right') and self.slider_right:
                try:
                    self.slider_right.set_val(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Reset right slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not reset right slider: {e}")

            if hasattr(self, 'slider_right_2') and self.slider_right_2:
                try:
                    self.slider_right_2.set_val(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Reset right slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not reset right slider: {e}")
            
            # Update cursor information to show data for minimum position
            if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                try:
                    self.update_cursor(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Updated left cursor info to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not update left cursor: {e}")

            if hasattr(self, 'update_cursor_2') and callable(self.update_cursor_2):
                try:
                    self.update_cursor_2(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Updated left cursor info to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not update left cursor: {e}")
            
            if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                try:
                    self.update_right_cursor(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Updated right cursor info to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not update right cursor: {e}")
            if hasattr(self, 'update_right_cursor_2') and callable(self.update_right_cursor_2):
                try:
                    self.update_right_cursor_2(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Updated right cursor info to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not update right cursor: {e}")
            
            # Force canvas redraw to ensure visual update
            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw()
            if hasattr(self, 'canvas_right') and self.canvas_right:
                self.canvas_right.draw()
                    
            logging.info("[graphics_window._reset_sliders_after_reconnect] Sliders reset and info updated after reconnection")
            
        except Exception as e:
            logging.error(f"[graphics_window._reset_sliders_after_reconnect] Error resetting sliders after reconnection: {e}")

    def left_slider_moved(self, val):
        if self.markers_locked:
            if self.slider_right.val != val:
                self.slider_right.set_val(val)
                self.update_right_cursor(val)

    def right_slider_moved(self, val):
        if self.markers_locked:
            if self.slider_left.val != val:
                self.slider_left.set_val(val)
                self.update_cursor(val)

    def left_slider_moved_2(self, val):
        if self.markers_locked:
            if self.slider_right_2.val != val:
                self.slider_right_2.set_val(val)
                self.update_right_cursor_2(val)

    def right_slider_moved_2(self, val):
        if self.markers_locked:
            if self.slider_left_2.val != val:
                self.slider_left_2.set_val(val)
                self.update_cursor_2(val)

    def _force_marker_visibility_2(self, marker_color_left, marker_color_right, marker_size_left, marker_size_right):
        """Force markers to be visible by recreating them directly on axes"""

        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "ui", "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.Format.IniFormat)

        unit_mode_left = settings.value("Graphic1/db_times", "dB") 
        unit_mode_right  = settings.value("Graphic2/db_times", "dB")

        logging.info(f"[graphics_window] Left panel unit mode: {unit_mode_left}")
        logging.info(f"[graphics_window] Right panel unit mode: {unit_mode_right}")
        
        if hasattr(self, 'cursor_left_2') and hasattr(self, 'ax_left') and self.cursor_left_2 and self.ax_left:
            try:
                # Remove the old cursor first to avoid duplicates
                try:
                    if self.cursor_left_2:
                        self.cursor_left_2.remove()
                        logging.info("[graphics_window._force_marker_visibility] Removed old left cursor to prevent duplicates")
                except:
                    pass  # Ignore errors if cursor can't be removed
                
                # Get current data from the old cursor if possible, otherwise use defaults
                x_val, y_val = 0.0, 0.0
                try:
                    x_data_2 = self.cursor_left_2.get_xdata()
                    y_data_2 = self.cursor_left_2.get_ydata()

                    if hasattr(x_data_2, '__len__') and hasattr(y_data_2, '__len__') and len(x_data_2) > 0 and len(y_data_2) > 0:
                        x_val_2 = float(y_data_2[0])
                        y_val_2 = float(y_data_2[0])
                except:
                    pass  # Use defaults
                
                # Create new cursor directly on the axes
                new_cursor_2 = self.ax_left.plot(x_val_2, y_val_2, 'o', color=marker_color_left, markersize=marker_size_left, markeredgewidth=2, visible=self.show_graphic1_marker2)[0]
                self.cursor_left_2 = new_cursor_2
                logging.info(f"[graphics_window._force_marker_visibility] Created new left cursor at ({x_val_2}, {y_val_2})")

                if hasattr(self, 'slider_left_2') and self.slider_left_2:
                    self.slider_left_2.on_changed(lambda val: self.update_cursor_2(int(val), from_slider=True))
                
                # Also update in markers list if it exists
                if hasattr(self, 'markers') and self.markers:
                    for i, marker in enumerate(self.markers):
                        if marker and marker.get('cursor_2') and i == 0:  # First marker
                            marker['cursor_2'] = new_cursor_2
                                
                    # Store the original update_cursor function and replace with a wrapper
                    if hasattr(self, 'update_cursor_2') and not hasattr(self, '_original_update_cursor_2'):
                        self._original_update_cursor_2 = self.update_cursor_2
                        
                        def cursor_left_wrapper_2(index, from_slider=False):
                            # Call the original function first to update labels
                            result = self._original_update_cursor_2(index, from_slider)
                            
                            # Then update our visible cursor position 
                    
                            if hasattr(self, 'cursor_left') and self.cursor_left and hasattr(self.cursor_left, 'set_data'):
                                try:
                                    # Get current graph type and S parameter for left panel
                                    actual_dir = os.path.dirname(os.path.dirname(__file__))  
                                    ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")
                                    settings = QSettings(ruta_ini, QSettings.Format.IniFormat)
                                    graph_type_left = settings.value("Tab1/GraphType1", "Smith Diagram")
                                    s_param_left = settings.value("Tab1/SParameter", "S11")
                                    
                                    # Determine which S parameter data to use
                                    s_data = None
                                    if s_param_left == "S21" and hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21
                                    elif s_param_left == "S11" and hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11
                                    elif hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21  # Default fallback to S21
                                    elif hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11  # Final fallback to S11
                                    
                                    if s_data is not None and hasattr(self, 'freqs') and self.freqs is not None and index < len(s_data) and index < len(self.freqs):
                                        val_complex = s_data[index]
                                        
                                        # Use appropriate coordinates based on graph type
                                        if graph_type_left == "Smith Diagram":
                                            # Smith diagram coordinates (real/imag)
                                            real_part = float(np.real(val_complex))
                                            imag_part = float(np.imag(val_complex))
                                            self.cursor_left_2.set_data([real_part], [imag_part])
                                        elif graph_type_left == "Magnitude":
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            if unit_mode_left == "dB":
                                                mag_val = float(20 * np.log10(np.abs(val_complex)))
                                            elif unit_mode_left == "Power ratio":
                                                mag_val = float(np.abs(val_complex)**2)
                                            elif unit_mode_left == "Voltage ratio":
                                                mag_val = float(np.abs(val_complex))
                                            else:
                                                mag_val = float(np.abs(val_complex))
                                            self.cursor_left_2.set_data([freq_mhz], [mag_val])
                                        elif graph_type_left == "Phase":
                                            # Phase plot coordinates (freq in MHz, phase in degrees)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            phase_deg = float(np.angle(val_complex) * 180 / np.pi)
                                            self.cursor_left_2.set_data([freq_mhz], [phase_deg])
                                        elif graph_type_left == "VSWR":
                                            # VSWR plot coordinates (freq in MHz, VSWR value)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            s_magnitude = np.abs(val_complex)
                                            vswr_val = (1 + s_magnitude) / (1 - s_magnitude) if s_magnitude < 1 else 999
                                            self.cursor_left_2.set_data([freq_mhz], [float(vswr_val)])
                                        
                                        # Force redraw
                                        if hasattr(self, 'canvas_left') and self.canvas_left:
                                            self.canvas_left.draw_idle()
                                except Exception as e:
                                    print(f"Error updating cursor_left position: {e}")
                        
                            return result
                
                        self.update_cursor_2 = cursor_left_wrapper_2

                        if hasattr(self, 'slider_left_2') and self.slider_left_2:
                            try:
                                self.slider_left_2.observers.clear()
                            except:
                                pass
                            self.slider_left_2.on_changed(self.left_slider_moved_2)
                        
                        # Reconnect the slider to use our wrapper
                        if hasattr(self, 'slider_left_2') and self.slider_left_2:
                            try:
                                self.slider_left_2.observers.clear()
                            except:
                                try:
                                    self.slider_left_2.disconnect()
                                except:
                                    pass
                            self.slider_left_2.on_changed(lambda val: cursor_left_wrapper_2(int(val), from_slider=True))

            except Exception as e:
                print(f"Error forcing cursor_left to ax_left: {e}")

        if hasattr(self, 'cursor_right_2') and hasattr(self, 'ax_right') and self.cursor_right_2 and self.ax_right:
            try:
                # Remove the old cursor first to avoid duplicates
                try:
                    if self.cursor_right_2:
                        self.cursor_right_2.remove()
                        logging.info("[graphics_window._force_marker_visibility] Removed old right cursor to prevent duplicates")
                except:
                    pass  # Ignore errors if cursor can't be removed
                
                # Get current data from the old cursor if possible, otherwise use defaults
                x_val, y_val = 0.0, 0.0
                try:
                    x_data = self.cursor_right_2.get_xdata()
                    y_data = self.cursor_right_2.get_ydata()
                    if hasattr(x_data, '__len__') and hasattr(y_data, '__len__') and len(x_data) > 0 and len(y_data) > 0:
                        x_val = float(x_data[0])
                        y_val = float(y_data[0])
                except:
                    pass  # Use defaults
                
                # Create new cursor directly on the axes
                new_cursor = self.ax_right.plot(x_val, y_val, 'o', color=marker_color_right, markersize=marker_size_right, markeredgewidth=2, visible=self.show_graphic2_marker2)[0]
                self.cursor_right_2 = new_cursor
                logging.info(f"[graphics_window._force_marker_visibility] Created new right cursor at ({x_val}, {y_val})")
                
                if hasattr(self, 'slider_right_2') and self.slider_right_2:
                    self.slider_right_2.on_changed(lambda val: self.update_right_cursor_2(int(val), from_slider=True))

                # Also update in markers list if it exists
                if hasattr(self, 'markers') and self.markers:
                    for i, marker in enumerate(self.markers):
                        if marker and marker.get('cursor_2') and i == 1:  # Second marker
                            marker['cursor_2'] = new_cursor
                                
                    # Store the original update_right_cursor function and replace with a wrapper
                    if hasattr(self, 'update_right_cursor_2') and not hasattr(self, '_original_update_right_cursor_2'):
                        self._original_update_right_cursor_2 = self.update_right_cursor_2
                        
                        def cursor_right_wrapper_2(index, from_slider=False):
                            # Call the original function first to update labels
                            result = self._original_update_right_cursor_2(index, from_slider)
                            
                            # Then update our visible cursor position 
                            if hasattr(self, 'cursor_right_2') and self.cursor_right_2 and hasattr(self.cursor_right_2, 'set_data'):
                                try:
                                    # Get current graph type for right panel
                                    actual_dir = os.path.dirname(os.path.dirname(__file__))  
                                    ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")
                                    settings = QSettings(ruta_ini, QSettings.Format.IniFormat)
                                    graph_type_right = settings.value("Tab2/GraphType2", "Magnitude")
                                    s_param_right = settings.value("Tab2/SParameter", "S11")
                                    
                                    # Determine which S parameter data to use
                                    s_data = None
                                    if s_param_right == "S21" and hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21
                                    elif s_param_right == "S11" and hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11
                                    elif hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21  # Default fallback to S21
                                    elif hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11  # Final fallback to S11
                                    
                                    if s_data is not None and hasattr(self, 'freqs') and self.freqs is not None and index < len(s_data) and index < len(self.freqs):
                                        val_complex = s_data[index]
                                        
                                        # Use appropriate coordinates based on graph type
                                        if graph_type_right == "Smith Diagram":
                                            # Smith diagram coordinates (real/imag)
                                            real_part = float(np.real(val_complex))
                                            imag_part = float(np.imag(val_complex))
                                            self.cursor_right_2.set_data([real_part], [imag_part])
                                        elif graph_type_right == "Magnitude":
                                            # Magnitude plot coordinates (freq in MHz, magnitude in dB)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            if unit_mode_right == "dB":
                                                mag_val = float(20 * np.log10(np.abs(val_complex)))
                                            elif unit_mode_right == "Power ratio":
                                                mag_val = float(np.abs(val_complex)**2)
                                            elif unit_mode_right == "Voltage ratio":
                                                mag_val = float(np.abs(val_complex))
                                            else:
                                                mag_val = float(np.abs(val_complex))
                                            self.cursor_right_2.set_data([freq_mhz], [mag_val])
                                        elif graph_type_right == "Phase":
                                            # Phase plot coordinates (freq in MHz, phase in degrees)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            phase_deg = float(np.angle(val_complex) * 180 / np.pi)
                                            self.cursor_right_2.set_data([freq_mhz], [phase_deg])
                                        elif graph_type_right == "VSWR":
                                            # VSWR plot coordinates (freq in MHz, VSWR value)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            s_magnitude = np.abs(val_complex)
                                            vswr_val = (1 + s_magnitude) / (1 - s_magnitude) if s_magnitude < 1 else 999
                                            self.cursor_right_2.set_data([freq_mhz], [float(vswr_val)])
                                        
                                        # Force redraw
                                        if hasattr(self, 'canvas_right') and self.canvas_right:
                                            self.canvas_right.draw_idle()
                                except Exception as e:
                                    print(f"Error updating cursor_right position: {e}")
                            
                            return result
                        
                        self.update_right_cursor_2 = cursor_right_wrapper_2

                        if hasattr(self, 'slider_right_2') and self.slider_right_2:
                            try:
                                self.slider_right_2.observers.clear()
                            except:
                                pass
                            self.slider_right_2.on_changed(self.right_slider_moved_2)
                            self.right_slider_moved_2()
                        
                        # Reconnect the slider to use our wrapper
                        if hasattr(self, 'slider_right_2') and self.slider_right_2:
                            try:
                                self.slider_right_2.observers.clear()
                            except:
                                try:
                                    self.slider_right_2.disconnect()
                                except:
                                    pass
                            self.slider_right_2.on_changed(lambda val: cursor_right_wrapper_2(int(val), from_slider=True))
                
            except Exception as e:
                print(f"Error forcing cursor_right to ax_right: {e}")
 
    def _force_marker_visibility(self, marker_color_left, marker_color_right, marker1_size_left, marker1_size_right):
        """Force markers to be visible by recreating them directly on axes"""

        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "ui", "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.Format.IniFormat)

        unit_mode_left = settings.value("Graphic1/db_times", "dB") 
        unit_mode_right  = settings.value("Graphic2/db_times", "dB")

        logging.info(f"[graphics_window] Left panel unit mode: {unit_mode_left}")
        logging.info(f"[graphics_window] Right panel unit mode: {unit_mode_right}")
        
        if (hasattr(self, 'cursor_left') or hasattr(self, 'cursor_left_2')) and hasattr(self, 'ax_left') and (self.cursor_left or self.cursor_left_2) and self.ax_left:
            try:
                # Remove the old cursor first to avoid duplicates
                try:
                    if self.cursor_left:
                        self.cursor_left.remove()
                        logging.info("[graphics_window._force_marker_visibility] Removed old left cursor to prevent duplicates")
                except:
                    pass  # Ignore errors if cursor can't be removed
                
                # Get current data from the old cursor if possible, otherwise use defaults
                x_val, y_val = 0.0, 0.0
                try:
                    x_data = self.cursor_left.get_xdata()
                    y_data = self.cursor_left.get_ydata()

                    if hasattr(x_data, '__len__') and hasattr(y_data, '__len__') and len(x_data) > 0 and len(y_data) > 0:
                        x_val = float(x_data[0])
                        y_val = float(y_data[0])
                except:
                    pass  # Use defaults
                
                # Create new cursor directly on the axes
                new_cursor = self.ax_left.plot(x_val, y_val, 'o', color=marker_color_left, markersize=marker1_size_left, markeredgewidth=2)[0]
                self.cursor_left = new_cursor
                logging.info(f"[graphics_window._force_marker_visibility] Created new left cursor at ({x_val}, {y_val})")

                # Also update in markers list if it exists
                if hasattr(self, 'markers') and self.markers:
                    for i, marker in enumerate(self.markers):
                        if marker and marker.get('cursor') and i == 0:  # First marker
                            marker['cursor'] = new_cursor
                                
                    # Store the original update_cursor function and replace with a wrapper
                    if hasattr(self, 'update_cursor') and not hasattr(self, '_original_update_cursor'):
                        self._original_update_cursor = self.update_cursor
                        
                        def cursor_left_wrapper(index, from_slider=False):
                            # Call the original function first to update labels
                            result = self._original_update_cursor(index, from_slider)
                            
                            # Then update our visible cursor position 
                            if hasattr(self, 'cursor_left') and self.cursor_left and hasattr(self.cursor_left, 'set_data'):
                                try:
                                    # Get current graph type and S parameter for left panel
                                    actual_dir = os.path.dirname(os.path.dirname(__file__))  
                                    ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")
                                    settings = QSettings(ruta_ini, QSettings.Format.IniFormat)
                                    graph_type_left = settings.value("Tab1/GraphType1", "Smith Diagram")
                                    s_param_left = settings.value("Tab1/SParameter", "S11")
                                    
                                    # Determine which S parameter data to use
                                    s_data = None
                                    if s_param_left == "S21" and hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21
                                    elif s_param_left == "S11" and hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11
                                    elif hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21  # Default fallback to S21
                                    elif hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11  # Final fallback to S11
                                    
                                    if s_data is not None and hasattr(self, 'freqs') and self.freqs is not None and index < len(s_data) and index < len(self.freqs):
                                        val_complex = s_data[index]
                                        
                                        # Use appropriate coordinates based on graph type
                                        if graph_type_left == "Smith Diagram":
                                            # Smith diagram coordinates (real/imag)
                                            real_part = float(np.real(val_complex))
                                            imag_part = float(np.imag(val_complex))
                                            self.cursor_left.set_data([real_part], [imag_part])
                                        elif graph_type_left == "Magnitude":
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            if unit_mode_left == "dB":
                                                mag_val = float(20 * np.log10(np.abs(val_complex)))
                                            elif unit_mode_left == "Power ratio":
                                                mag_val = float(np.abs(val_complex)**2)
                                            elif unit_mode_left == "Voltage ratio":
                                                mag_val = float(np.abs(val_complex))
                                            else:
                                                mag_val = float(np.abs(val_complex))
                                            self.cursor_left.set_data([freq_mhz], [mag_val])
                                        elif graph_type_left == "Phase":
                                            # Phase plot coordinates (freq in MHz, phase in degrees)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            phase_deg = float(np.angle(val_complex) * 180 / np.pi)
                                            self.cursor_left.set_data([freq_mhz], [phase_deg])
                                        elif graph_type_left == "VSWR":
                                            # VSWR plot coordinates (freq in MHz, VSWR value)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            s_magnitude = np.abs(val_complex)
                                            vswr_val = (1 + s_magnitude) / (1 - s_magnitude) if s_magnitude < 1 else 999
                                            self.cursor_left.set_data([freq_mhz], [float(vswr_val)])
                                        
                                        # Force redraw
                                        if hasattr(self, 'canvas_left') and self.canvas_left:
                                            self.canvas_left.draw_idle()
                                except Exception as e:
                                    print(f"Error updating cursor_left position: {e}")
                            
                            return result
                        
                        self.update_cursor = cursor_left_wrapper

                        if hasattr(self, 'slider_left') and self.slider_left:
                            try:
                                self.slider_left.observers.clear()
                            except:
                                pass
                            self.slider_left.on_changed(self.left_slider_moved)
                        
                        # Reconnect the slider to use our wrapper
                        if hasattr(self, 'slider_left') and self.slider_left:
                            try:
                                self.slider_left.observers.clear()
                            except:
                                try:
                                    self.slider_left.disconnect()
                                except:
                                    pass
                            self.slider_left.on_changed(lambda val: cursor_left_wrapper(int(val), from_slider=True))

            except Exception as e:
                print(f"Error forcing cursor_left to ax_left: {e}")
                
        if hasattr(self, 'cursor_right') and hasattr(self, 'ax_right') and self.cursor_right and self.ax_right:
            try:
                # Remove the old cursor first to avoid duplicates
                try:
                    if self.cursor_right:
                        self.cursor_right.remove()
                        logging.info("[graphics_window._force_marker_visibility] Removed old right cursor to prevent duplicates")
                except:
                    pass  # Ignore errors if cursor can't be removed
                
                # Get current data from the old cursor if possible, otherwise use defaults
                x_val, y_val = 0.0, 0.0
                try:
                    x_data = self.cursor_right.get_xdata()
                    y_data = self.cursor_right.get_ydata()
                    if hasattr(x_data, '__len__') and hasattr(y_data, '__len__') and len(x_data) > 0 and len(y_data) > 0:
                        x_val = float(x_data[0])
                        y_val = float(y_data[0])
                except:
                    pass  # Use defaults
                
                # Create new cursor directly on the axes
                new_cursor = self.ax_right.plot(x_val, y_val, 'o', color=marker_color_right, markersize=marker1_size_right, markeredgewidth=2)[0]
                self.cursor_right = new_cursor
                logging.info(f"[graphics_window._force_marker_visibility] Created new right cursor at ({x_val}, {y_val})")
                
                if hasattr(self, 'slider_right') and self.slider_right:
                    self.slider_right.on_changed(lambda val: self.update_right_cursor(int(val), from_slider=True))

                # Also update in markers list if it exists
                if hasattr(self, 'markers') and self.markers:
                    for i, marker in enumerate(self.markers):
                        if marker and marker.get('cursor') and i == 1:  # Second marker
                            marker['cursor'] = new_cursor
                                
                    # Store the original update_right_cursor function and replace with a wrapper
                    if hasattr(self, 'update_right_cursor') and not hasattr(self, '_original_update_right_cursor'):
                        self._original_update_right_cursor = self.update_right_cursor
                        
                        def cursor_right_wrapper(index, from_slider=False):
                            # Call the original function first to update labels
                            result = self._original_update_right_cursor(index, from_slider)
                            
                            # Then update our visible cursor position 
                            if hasattr(self, 'cursor_right') and self.cursor_right and hasattr(self.cursor_right, 'set_data'):
                                try:
                                    # Get current graph type for right panel
                                    actual_dir = os.path.dirname(os.path.dirname(__file__))  
                                    ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")
                                    settings = QSettings(ruta_ini, QSettings.Format.IniFormat)
                                    graph_type_right = settings.value("Tab2/GraphType2", "Magnitude")
                                    s_param_right = settings.value("Tab2/SParameter", "S11")
                                    
                                    # Determine which S parameter data to use
                                    s_data = None
                                    if s_param_right == "S21" and hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21
                                    elif s_param_right == "S11" and hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11
                                    elif hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21  # Default fallback to S21
                                    elif hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11  # Final fallback to S11
                                    
                                    if s_data is not None and hasattr(self, 'freqs') and self.freqs is not None and index < len(s_data) and index < len(self.freqs):
                                        val_complex = s_data[index]
                                        
                                        # Use appropriate coordinates based on graph type
                                        if graph_type_right == "Smith Diagram":
                                            # Smith diagram coordinates (real/imag)
                                            real_part = float(np.real(val_complex))
                                            imag_part = float(np.imag(val_complex))
                                            self.cursor_right.set_data([real_part], [imag_part])
                                        elif graph_type_right == "Magnitude":
                                            # Magnitude plot coordinates (freq in MHz, magnitude in dB)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            if unit_mode_right == "dB":
                                                mag_val = float(20 * np.log10(np.abs(val_complex)))
                                            elif unit_mode_right == "Power ratio":
                                                mag_val = float(np.abs(val_complex)**2)
                                            elif unit_mode_right == "Voltage ratio":
                                                mag_val = float(np.abs(val_complex))
                                            else:
                                                mag_val = float(np.abs(val_complex))
                                            self.cursor_right.set_data([freq_mhz], [mag_val])
                                        elif graph_type_right == "Phase":
                                            # Phase plot coordinates (freq in MHz, phase in degrees)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            phase_deg = float(np.angle(val_complex) * 180 / np.pi)
                                            self.cursor_right.set_data([freq_mhz], [phase_deg])
                                        elif graph_type_right == "VSWR":
                                            # VSWR plot coordinates (freq in MHz, VSWR value)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            s_magnitude = np.abs(val_complex)
                                            vswr_val = (1 + s_magnitude) / (1 - s_magnitude) if s_magnitude < 1 else 999
                                            self.cursor_right.set_data([freq_mhz], [float(vswr_val)])
                                        
                                        # Force redraw
                                        if hasattr(self, 'canvas_right') and self.canvas_right:
                                            self.canvas_right.draw_idle()
                                except Exception as e:
                                    print(f"Error updating cursor_right position: {e}")
                            
                            return result
                        
                        self.update_right_cursor = cursor_right_wrapper

                        if hasattr(self, 'slider_right') and self.slider_right:
                            try:
                                self.slider_right.observers.clear()
                            except:
                                pass
                            self.slider_right.on_changed(self.right_slider_moved)
                            self.right_slider_moved()
                        
                        # Reconnect the slider to use our wrapper
                        if hasattr(self, 'slider_right') and self.slider_right:
                            try:
                                self.slider_right.observers.clear()
                            except:
                                try:
                                    self.slider_right.disconnect()
                                except:
                                    pass
                            self.slider_right.on_changed(lambda val: cursor_right_wrapper(int(val), from_slider=True))
                
            except Exception as e:
                print(f"Error forcing cursor_right to ax_right: {e}")


    def _clear_marker_fields_only(self):
        """Clear only marker information fields without affecting the graphs."""
        logging.info("[graphics_window._clear_marker_fields_only] Clearing marker information fields only")
        
        # --- Clear left panel marker information ---
        if hasattr(self, 'labels_left') and self.labels_left:
            freq_left = self.labels_left.get("freq")
            if freq_left:
                freq_left.setText("--")    # set "--"
                freq_left.deselect()       # remove selection
                freq_left.clearFocus()     # remove focus so it's not blue
            self.labels_left.get("val") and self.labels_left["val"].setText("S11: -- + j--")
            self.labels_left.get("mag") and self.labels_left["mag"].setText("|S11|: --")
            self.labels_left.get("phase") and self.labels_left["phase"].setText("Phase: --")
            self.labels_left.get("z") and self.labels_left["z"].setText("Zin (Z0): -- + j--")
            self.labels_left.get("il") and self.labels_left["il"].setText("IL: --")
            self.labels_left.get("vswr") and self.labels_left["vswr"].setText("VSWR: --")

        # --- Clear right panel marker information ---
        if hasattr(self, 'labels_right') and self.labels_right:
            freq_right = self.labels_right.get("freq")
            if freq_right:
                freq_right.setText("--")   # set "--"
                freq_right.deselect()      # remove selection
                freq_right.clearFocus()    # remove focus so it's not blue
            self.labels_right.get("val") and self.labels_right["val"].setText("S21: -- + j--")
            self.labels_right.get("mag") and self.labels_right["mag"].setText("|S21|: --")
            self.labels_right.get("phase") and self.labels_right["phase"].setText("Phase: --")
            self.labels_right.get("z") and self.labels_right["z"].setText("Zin (Z0): -- + j--")
            self.labels_right.get("il") and self.labels_right["il"].setText("IL: --")
            self.labels_right.get("vswr") and self.labels_right["vswr"].setText("VSWR: --")

        # --- Clear left panel marker information ---
        if hasattr(self, 'labels_left_2') and self.labels_left_2:
            freq_left = self.labels_left_2.get("freq")
            if freq_left:
                freq_left.setText("--")    # set "--"
                freq_left.deselect()       # remove selection
                freq_left.clearFocus()     # remove focus so it's not blue
            self.labels_left_2.get("val") and self.labels_left_2["val"].setText("S11: -- + j--")
            self.labels_left_2.get("mag") and self.labels_left_2["mag"].setText("|S11|: --")
            self.labels_left_2.get("phase") and self.labels_left_2["phase"].setText("Phase: --")
            self.labels_left_2.get("z") and self.labels_left_2["z"].setText("Zin (Z0): -- + j--")
            self.labels_left_2.get("il") and self.labels_left_2["il"].setText("IL: --")
            self.labels_left_2.get("vswr") and self.labels_left_2["vswr"].setText("VSWR: --")

        # --- Clear right panel marker information ---
        if hasattr(self, 'labels_right_2') and self.labels_right_2:
            freq_right = self.labels_right_2.get("freq")
            if freq_right:
                freq_right.setText("--")   # set "--"
                freq_right.deselect()      # remove selection
                freq_right.clearFocus()    # remove focus so it's not blue
            self.labels_right_2.get("val") and self.labels_right_2["val"].setText("S21: -- + j--")
            self.labels_right_2.get("mag") and self.labels_right_2["mag"].setText("|S21|: --")
            self.labels_right_2.get("phase") and self.labels_right_2["phase"].setText("Phase: --")
            self.labels_right_2.get("z") and self.labels_right_2["z"].setText("Zin (Z0): -- + j--")
            self.labels_right_2.get("il") and self.labels_right_2["il"].setText("IL: --")
            self.labels_right_2.get("vswr") and self.labels_right_2["vswr"].setText("VSWR: --")

        # Do NOT clear the graphs - leave them with the actual data
        logging.info("[graphics_window._clear_marker_fields_only] Marker fields cleared, graphs preserved")

    def _update_slider_ranges(self):
        """Update slider ranges and steps to match the current sweep data."""
        if not hasattr(self, 'freqs') or self.freqs is None or len(self.freqs) == 0:
            logging.warning("[graphics_window._update_slider_ranges] No frequency data available, cannot update sliders")
            return
            
        try:
            num_points = len(self.freqs)
            max_index = num_points - 1
            middle_index = max_index // 2
            
            logging.info(f"[graphics_window._update_slider_ranges] Updating sliders for {num_points} frequency points (indices 0 to {max_index})")
            logging.info(f"[graphics_window._update_slider_ranges] Frequency range: {self.freqs[0]/1e6:.3f} - {self.freqs[-1]/1e6:.3f} MHz")
            
            # Update left slider range if it exists and make it visible
            if hasattr(self, 'slider_left') and self.slider_left:
                try:
                    # Update slider range to match frequency data indices
                    self.slider_left.valmin = 0
                    self.slider_left.valmax = max_index
                    self.slider_left.valstep = 1
                    
                    # Set slider to middle position
                    self.slider_left.set_val(middle_index)
                    
                    # Make sure the slider is visible and active
                    if hasattr(self.slider_left, 'ax'):
                        self.slider_left.ax.set_visible(True)
                    if hasattr(self.slider_left, 'set_active'):
                        self.slider_left.set_active(True)
                    
                    logging.info(f"[graphics_window._update_slider_ranges] Left slider updated: range 0-{max_index}, positioned at index {middle_index} ({self.freqs[middle_index]/1e6:.3f} MHz)")
                except Exception as e:
                    logging.warning(f"[graphics_window._update_slider_ranges] Could not update left slider: {e}")
            
            # Update right slider range if it exists and make it visible
            if hasattr(self, 'slider_right') and self.slider_right:
                try:
                    # Update slider range to match frequency data indices  
                    self.slider_right.valmin = 0
                    self.slider_right.valmax = max_index
                    self.slider_right.valstep = 1
                    
                    # Set slider to middle position
                    self.slider_right.set_val(middle_index)
                    
                    # Make sure the slider is visible and active
                    if hasattr(self.slider_right, 'ax'):
                        self.slider_right.ax.set_visible(True)
                    if hasattr(self.slider_right, 'set_active'):
                        self.slider_right.set_active(True)
                    
                    logging.info(f"[graphics_window._update_slider_ranges] Right slider updated: range 0-{max_index}, positioned at index {middle_index} ({self.freqs[middle_index]/1e6:.3f} MHz)")
                except Exception as e:
                    logging.warning(f"[graphics_window._update_slider_ranges] Could not update right slider: {e}")

            # Force canvas redraw to show updated markers
            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw_idle()
            if hasattr(self, 'canvas_right') and self.canvas_right:
                self.canvas_right.draw_idle()
                    
            logging.info("[graphics_window._update_slider_ranges] Slider ranges updated successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window._update_slider_ranges] Error updating slider ranges: {e}")

    # =================== CONNECTION FUNCTION ==================

    def open_connection_window(self):
        from NanoVNA_UTN_Toolkit.ui.connection_window import NanoVNAStatusApp

        logging.info("[connection_windows.open_connection_window] Opening connection")
        
        self.connection_window = NanoVNAStatusApp()
        self.connection_window.show()
        self.close()
        self.deleteLater()

    # =================== CALIBRATION WIZARD FUNCTION ==================

    def open_calibration_wizard(self):
        from NanoVNA_UTN_Toolkit.ui.wizard_windows import CalibrationWizard

        logging.info("[wizard_windows.open_calibration_wizard] Opening calibration wizard")
        
        if self.vna_device:
            self.welcome_windows = CalibrationWizard(self.vna_device, caller="graphics")
        else:
            self.welcome_windows = CalibrationWizard(caller="graphics")
        self.welcome_windows.show()
        self.close()
        self.deleteLater()

    # =================== KITS OPTIONS FUNCTION ==================

    def select_kit_dialog(self): 
        from PySide6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
            QLabel, QPushButton, QWidget, QScrollArea
        )
        from PySide6.QtCore import Qt, QSettings
        from PySide6.QtGui import QIcon
        from PySide6 import QtCore
        import os

        # --- Create dialog ---
        dialog = QDialog(self)
        dialog.setWindowTitle("Select a Calibration Kit")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # --- Base directory and ini path ---
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
        settings = QSettings(config_path, QSettings.Format.IniFormat)

        # --- List widget for kits ---
        list_widget = QListWidget()
        layout.addWidget(QLabel("Select a kit:"))
        layout.addWidget(list_widget)

        # --- Populate list ---
        groups = settings.childGroups()
        kits_info = {}  # Para guardar info de cada kit
        for g in groups:
            if g.startswith("Kit_"):
                name = settings.value(f"{g}/kit_name", "").strip()
                method = settings.value(f"{g}/method", "").strip()
                kit_id = int(settings.value(f"{g}/id", 0))
                if name:
                    item = QListWidgetItem(name)
                    item.setData(Qt.UserRole, g)
                    list_widget.addItem(item)
                    kits_info[name] = {"id": kit_id, "method": method}

        # --- Selected tag area (solo uno) ---
        selected_name = [None]  # lista de un elemento para mutabilidad
        selected_area = QHBoxLayout()
        selected_container = QWidget()
        selected_container.setLayout(selected_area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(selected_container)
        layout.addWidget(scroll)

        # --- Add selected kit to tag area ---
        def add_selected(item):
            # Limpiar selección previa
            for i in reversed(range(selected_area.count())):
                widget = selected_area.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            selected_name[0] = None

            name = item.text()
            selected_name[0] = name

            tag_widget = QWidget()
            tag_layout = QHBoxLayout(tag_widget)
            tag_layout.setContentsMargins(5, 2, 5, 2)
            label = QLabel(name)

            # Botón de “deseleccionar” (cruz roja)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            icon_path = os.path.join(project_root, "NanoVNA_UTN_Toolkit", "assets", "icons", "delete.svg")

            remove_btn = QPushButton()
            remove_btn.setIcon(QIcon(icon_path))
            remove_btn.setIconSize(QtCore.QSize(20, 20))
            remove_btn.setFixedSize(30, 30)
            remove_btn.setFlat(True)
            remove_btn.setStyleSheet("""
                QPushButton { border: none; background-color: transparent; }
                QPushButton:hover { background-color: rgba(255, 0, 0, 50); }
            """)

            tag_layout.addWidget(label)
            tag_layout.addWidget(remove_btn)

            def remove_tag():
                tag_widget.setParent(None)
                selected_name[0] = None

            remove_btn.clicked.connect(remove_tag)
            selected_area.addWidget(tag_widget)

        # --- Select button action ---
        def select_kit():
            if not selected_name[0]:
                return  # No hay kit seleccionado
            name = selected_name[0]
            kit_info = kits_info[name]

            kit_name_with_id = f"{name}_{kit_info['id']}" 

            
            if kit_info["method"] == "OSM (Open - Short - Match)":
                parameter = "S11"
            elif kit_info["method"] == "Normalization":
                parameter = "S21"
            else:
                parameter = "S11, S21"

            # Guardar en [Calibration]
            settings.beginGroup("Calibration")
            settings.setValue("Name", kit_name_with_id)
            settings.setValue("id", kit_info["id"])
            settings.setValue("Method", kit_info["method"])
            settings.setValue("Kits", True)
            settings.setValue("NoCalibration", False)
            settings.setValue("Parameter", parameter)
            settings.endGroup()
            settings.sync()

            dialog.accept()  

            if self.vna_device:
                graphics_window = NanoVNAGraphics(vna_device=self.vna_device)
            else:
                graphics_window = NanoVNAGraphics()
            graphics_window.show()
            self.close()

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_select = QPushButton("Select")
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_select)
        layout.addLayout(btn_layout)

        # --- Connect signals ---
        list_widget.itemClicked.connect(add_selected)
        btn_cancel.clicked.connect(dialog.reject)
        btn_select.clicked.connect(select_kit)  # <--- sin paréntesis

        dialog.exec()

    # Method to show a warning message
    def show_calibration_warning(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Calibration Warning")
        msg.setText(
            "Save operation is disabled because calibration was not performed from scratch.\n"
            "Please use the calibration wizard to create a new calibration before saving."
        )
        msg.exec()

    def save_kit_dialog(self):
        from PySide6.QtWidgets import QMessageBox
        """Shows a dialog to save the calibration without advancing to graphics window"""

        self.osm_calibration.is_complete_true()
        self.thru_calibration.is_complete_true()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        osm_dir = os.path.join(base_dir, "Calibration", "osm_results")
        thru_dir = os.path.join(base_dir, "Calibration", "thru_results")

        files = [
            os.path.join(osm_dir, "open.s1p"),
            os.path.join(osm_dir, "short.s1p"),
            os.path.join(osm_dir, "match.s1p"),
            os.path.join(thru_dir, "thru.s2p")
        ]

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")

        settings = QSettings(config_path, QSettings.Format.IniFormat)

        # Method
        selected_method = settings.value("Calibration/Method", "No Kit")

        # Dialog to enter calibration name
        from PySide6.QtWidgets import QInputDialog

        logging.info(f"[Calibration_Kit] Selected Method: {selected_method}")

        if selected_method == "OSM (Open - Short - Match)":
            prefix = "OSM"
        elif selected_method == "Normalization":
            prefix = "Normalization"
        elif selected_method== "1-Port+N":
            prefix = "1PortN"
        elif selected_method == "Enhanced-Response":
            prefix = "Enhanced Response"

        name, ok = QInputDialog.getText(
            self, 
            'Save Calibration', 
            f'Enter calibration name:\n\nMeasurements to save:',
            text=f'{prefix}_Calibration_{self.get_current_timestamp()}'
        )
        
        if ok and name:
            try:
                # Save calibration (it will save only the available measurements)
                if selected_method != "Normalization": 
                    success = self.osm_calibration.save_calibration_file(name, selected_method, False, files)
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
                        #QMessageBox.warning(self, "Error", "Failed to save calibration") hay un error aca y entra primero

                success = self.thru_calibration.save_calibration_file(name, selected_method, True, files, osm_instance=self.osm_calibration)
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
                """
                # --- If a kit was previously saved in this session, show its name ---
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

                # --- Save data ---
                settings_calibration.beginGroup(calibration_entry_name)
                settings_calibration.setValue("kit_name", name)
                settings_calibration.setValue("method", selected_method)
                settings_calibration.setValue("id", next_id)
                settings_calibration.endGroup()

                # --- Update active calibration reference ---
                settings_calibration.beginGroup("Calibration")
                settings_calibration.setValue("Name", full_calibration_name)
                settings_calibration.endGroup()
                settings_calibration.sync()

                logging.info(f"[welcome_windows.open_save_calibration] Saved calibration {full_calibration_name}")

            except Exception as e:
                logging.error(f"[CalibrationKit] Error saving calibration: {e}")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Error saving calibration: {str(e)}")

    def delete_kit_dialog(self):
        from PySide6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
            QLabel, QPushButton, QWidget, QScrollArea, QMessageBox
        )
        from PySide6.QtCore import Qt, QSettings
        import os
        import shutil
        import logging

        # --- Create dialog ---
        dialog = QDialog(self)
        dialog.setWindowTitle("Delete Calibration Kits")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # --- Base directory and ini path ---
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
        settings = QSettings(config_path, QSettings.Format.IniFormat)

        # --- List widget for kits ---
        list_widget = QListWidget()
        layout.addWidget(QLabel("Select kits to delete:"))
        layout.addWidget(list_widget)

        # --- Populate list ---
        groups = settings.childGroups()
        for g in groups:
            if g.startswith("Kit_"):
                name = settings.value(f"{g}/kit_name", "").strip()
                if name:
                    item = QListWidgetItem(name)
                    item.setData(Qt.UserRole, g)
                    list_widget.addItem(item)

        # --- Selected tags area ---
        selected_names = set()
        selected_area = QHBoxLayout()
        selected_container = QWidget()
        selected_container.setLayout(selected_area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(selected_container)
        layout.addWidget(scroll)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_delete = QPushButton("Delete")
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_delete)
        layout.addLayout(btn_layout)

        from PySide6.QtGui import QIcon
        from PySide6 import QtCore

        # --- Add selected kit to tag area ---
        def add_selected(item):
            name = item.text()
            if name in selected_names:
                return
            selected_names.add(name)

            tag_widget = QWidget()
            tag_layout = QHBoxLayout(tag_widget)
            tag_layout.setContentsMargins(5, 2, 5, 2)
            label = QLabel(name)
            
            from PySide6.QtGui import QIcon

            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            icon_path = os.path.join(project_root, "NanoVNA_UTN_Toolkit", "assets", "icons", "delete.svg")

            remove_btn = QPushButton()
            remove_btn.setIcon(QIcon(icon_path))
            remove_btn.setIconSize(QtCore.QSize(20, 20))
            remove_btn.setFixedSize(30, 30)
            remove_btn.setFlat(True)

            # Quitar fondo y borde, hacer hover más rojo
            remove_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: rgba(255, 0, 0, 50);  /* efecto hover rojo suave */
                }
            """)

            tag_layout.addWidget(label)
            tag_layout.addWidget(remove_btn)

            def remove_tag():
                tag_widget.setParent(None)
                selected_names.remove(name)

            remove_btn.clicked.connect(remove_tag)
            selected_area.addWidget(tag_widget)

        # --- Delete selected kits ---
        def delete_selected():
            if not selected_names:
                QMessageBox.warning(dialog, "No Selection", "Please select at least one kit to delete.")
                return

            confirm = QMessageBox.question(
                dialog,
                "Confirm Delete",
                f"Are you sure you want to delete these kits?\n\n" + "\n".join(selected_names),
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return

            # --- Read current calibration name ---
            current_full_name = settings.value("Calibration/Name", "")
            current_name_base = "_".join(current_full_name.split("_")[:-1]) if current_full_name else ""

            deleted_current_kit = False

            # --- Delete physical folders and mark if current kit is deleted ---
            kits_to_delete = []
            for g in settings.childGroups():
                if g.startswith("Kit_"):
                    kit_name_ini = settings.value(f"{g}/kit_name", "").strip()
                    if kit_name_ini in selected_names:
                        if kit_name_ini == current_name_base:
                            deleted_current_kit = True  # MARKER: current kit will be deleted
                        kit_path = os.path.join(base_dir, "calibration", "kits", kit_name_ini)
                        if os.path.exists(kit_path) and os.path.isdir(kit_path):
                            shutil.rmtree(kit_path)
                            logging.info(f"Deleted folder: {kit_path}")
                        else:
                            logging.warning(f"Folder not found: {kit_path}")
                        kits_to_delete.append(g)

            # --- Remove from ini ---
            for g in kits_to_delete:
                settings.remove(g)

            settings.sync()

            # --- Reorder remaining kits (same as before) ---
            remaining_kits = []
            for g in settings.childGroups():
                if g.startswith("Kit_"):
                    kit_name = settings.value(f"{g}/kit_name", "").strip()
                    method = settings.value(f"{g}/method", "")
                    kit_id = int(settings.value(f"{g}/id", 0))
                    remaining_kits.append((kit_id, g, kit_name, method))

            remaining_kits.sort(key=lambda x: x[0])

            # --- Clear old groups ---
            for _, g, _, _ in remaining_kits:
                settings.remove(g)

            # --- Save remaining kits with consecutive IDs ---
            for new_id, (_, _, kit_name, method) in enumerate(remaining_kits, start=1):
                group_name = f"Kit_{new_id}"
                settings.beginGroup(group_name)
                settings.setValue("kit_name", kit_name)
                settings.setValue("method", method)
                settings.setValue("id", new_id)
                settings.endGroup()

            # --- Update [Calibration] Name and id ---
            if remaining_kits:
                first_kit_name = remaining_kits[0][2]  # kit_name of first kit
                settings.beginGroup("Calibration")
                settings.setValue("Name", f"{first_kit_name}_1")
                settings.setValue("id", 1)
                settings.setValue("Kits", True)
                settings.setValue("NoCalibration", False)
                settings.endGroup()

                was_current_deleted = deleted_current_kit


            else:
                # No kits left, remove Name/id and reset flags
                settings.beginGroup("Calibration")
                settings.remove("Name")
                settings.remove("id")
                settings.setValue("Kits", False)
                settings.setValue("NoCalibration", True)
                settings.endGroup()

                was_current_deleted = "all"

            settings.sync()
            QMessageBox.information(dialog, "Deleted", "Selected kits have been deleted and IDs updated.")
            dialog.accept()

            # --- Now handle navigation AFTER user confirms ---
            if was_current_deleted == True:
                self.handle_deleted_current_kit()
            elif was_current_deleted == "all":
                self.handle_all_kits_deleted()
 
        # --- Connect signals ---
        list_widget.itemClicked.connect(add_selected)
        btn_cancel.clicked.connect(dialog.reject)
        btn_delete.clicked.connect(delete_selected)

        dialog.exec()

    def handle_deleted_current_kit(self):
        from PySide6.QtCore import QSettings
        import os

        # Path to calibration_config.ini
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")

        settings = QSettings(config_path, QSettings.Format.IniFormat)
        settings.sync()

        # --- Check if there's still a Kit_1 ---
        if settings.contains("Kit_1/kit_name"):
            first_kit_name = settings.value("Kit_1/kit_name", "").strip()
            method = settings.value("Kit_1/method", "")
            
            # Get previous method/parameter if they exist
            prev_method = settings.value("Calibration/Method", method)
            prev_parameter = settings.value("Calibration/Parameter", "S21")

            # --- Update Calibration section ---
            settings.beginGroup("Calibration")
            settings.setValue("Kits", True)
            settings.setValue("NoCalibration", False)
            settings.setValue("Method", prev_method)
            settings.setValue("Parameter", prev_parameter)
            settings.setValue("Name", f"{first_kit_name}_1")
            settings.setValue("id", 1)
            settings.endGroup()

        else:
            # If no kits remain, fallback to a safe state
            settings.beginGroup("Calibration")
            settings.setValue("Kits", False)
            settings.setValue("NoCalibration", True)
            settings.remove("Name")
            settings.remove("id")
            settings.endGroup()

        settings.sync()

        if self.vna_device:
            graphics_window = NanoVNAGraphics(vna_device=self.vna_device)
        else:
            graphics_window = NanoVNAGraphics()
        graphics_window.show()
        self.close()


    def handle_all_kits_deleted(self):
        from PySide6.QtCore import QSettings
        import os

        # Path to calibration_config.ini
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")

        settings = QSettings(config_path, QSettings.Format.IniFormat)
        settings.sync()

        # --- Set calibration state to NoCalibration ---
        settings.beginGroup("Calibration")
        settings.setValue("Kits", False)
        settings.setValue("NoCalibration", True)
        settings.remove("Name")
        settings.remove("id")
        settings.endGroup()
        settings.sync()

        # --- Reopen graphics window in no-calibration mode ---
        if self.vna_device:
            graphics_window = NanoVNAGraphics(vna_device=self.vna_device)
        else:
            graphics_window = NanoVNAGraphics()
        graphics_window.show()
        self.close()

    # =================== SWEEP OPTIONS FUNCTION ==================

    def open_sweep_options(self):
        from NanoVNA_UTN_Toolkit.ui.sweep_window import SweepOptionsWindow

        # Log sweep options opening
        logging.info("[graphics_window.open_sweep_options] Opening sweep options window")

        # Try to get the current VNA device (this is a placeholder for now)
        vna_device = self.get_current_vna_device()

        # Log device information being passed to sweep options
        if vna_device:
            device_type = type(vna_device).__name__
            logging.info(f"[graphics_window.open_sweep_options] Device found: {device_type}")
            if hasattr(vna_device, 'sweep_points_min') and hasattr(vna_device, 'sweep_points_max'):
                logging.info(f"[graphics_window.open_sweep_options] Device sweep limits: {vna_device.sweep_points_min} to {vna_device.sweep_points_max}")
            else:
                logging.info("[graphics_window.open_sweep_options] Device has no sweep_points limits")
        else:
            logging.warning("[graphics_window.open_sweep_options] No VNA device available - using default limits")

        if hasattr(self, 'sweep_options_window') and self.sweep_options_window is not None:
            self.sweep_options_window.close()
            self.sweep_options_window.deleteLater()
            self.sweep_options_window = None

        logging.info("[graphics_window.open_sweep_options] Creating new sweep options window")
        self.sweep_options_window = SweepOptionsWindow(parent=self, vna_device=self.vna_device)

        self.sweep_options_window.show()
        self.sweep_options_window.raise_()
        self.sweep_options_window.activateWindow()

        
    def get_current_vna_device(self):
        """Try to get the current VNA device."""
        logging.info("[graphics_window.get_current_vna_device] Searching for current VNA device")
        
        try:
            # Check if we have device stored in this graphics window
            if hasattr(self, 'vna_device') and self.vna_device is not None:
                device_type = type(self.vna_device).__name__
                logging.info(f"[graphics_window.get_current_vna_device] Found stored device: {device_type}")
                return self.vna_device
                
            # Check if we can access the connection window device
            # This is a more advanced implementation for future development
            logging.warning("[graphics_window.get_current_vna_device] No VNA device found in graphics window")
            logging.warning("[graphics_window.get_current_vna_device] Device wasn't passed from previous window")
            
            return None
        except Exception as e:
            logging.error(f"[graphics_window.get_current_vna_device] Error getting current VNA device: {e}")
            return None

    # =================== RIGHT CLICK ==================

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        view_menu = menu.addAction("View")

        menu.addSeparator()
        
        marker1_graphic1_action = menu.addAction("Marker 1 - Graphic 1")
        marker1_graphic1_action.setCheckable(True)
        marker1_graphic1_action.setChecked(self.show_graphic1_marker1)

        marker1_graphic2_action = menu.addAction("Marker 1 - Graphic 2")
        marker1_graphic2_action.setCheckable(True)
        marker1_graphic2_action.setChecked(self.show_graphic2_marker1)

        marker2_graphic1_action = menu.addAction("Marker 2 -Graphic 1")
        marker2_graphic1_action.setCheckable(True)
        marker2_graphic1_action.setChecked(False)
        marker2_graphic1_action.setChecked(self.show_graphic1_marker2)

        marker2_graphic2_action = menu.addAction("Marker 2 -Graphic 2")
        marker2_graphic2_action.setCheckable(True)
        marker2_graphic2_action.setChecked(False)
        marker2_graphic2_action.setChecked(self.show_graphic2_marker2)

        # --- Lock markers action ---
        lock_markers_action = menu.addAction("Lock Markers ✓" if self.markers_locked else "Lock Markers")
        lock_markers_action.setCheckable(True)
        lock_markers_action.setChecked(self.markers_locked)

        # --- Determine which graph was clicked ---
        widget_under_cursor = QApplication.widgetAt(event.globalPos())
        graph_number = 1  # default left
        current_widget = widget_under_cursor
        while current_widget:
            if hasattr(self, "canvas_right") and current_widget == self.canvas_right:
                graph_number = 2
                break
            elif hasattr(self, "canvas_left") and current_widget == self.canvas_left:
                graph_number = 1
                break
            current_widget = current_widget.parent()

        # --- Read the current unit from INI ---
        import os
        from PySide6.QtCore import QSettings
        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "ui", "graphics_windows", "ini", "config.ini")
        settings = QSettings(ruta_ini, QSettings.Format.IniFormat)
        ini_section = "Graphic1" if graph_number == 1 else "Graphic2"
        settings.beginGroup(ini_section)
        current_unit = settings.value("db_times", "dB")
        settings.endGroup()

        # --- Unit submenu ---
        menu.addSeparator()
        unit_menu = QMenu(f"Unit ({current_unit})", self)
        if current_unit == "dB":
            power_action = unit_menu.addAction("Power ratio (times)")
            voltage_action = unit_menu.addAction("Voltage ratio (times)")
        else:
            db_action = unit_menu.addAction("dB")
        menu.addMenu(unit_menu)

        # ---- grid ----

        menu.addSeparator()

        # --- Grid action ---
        widget_under_cursor = QApplication.widgetAt(event.globalPos())
        target_ax = None
        target_fig = None
        target_attr = None

        current_widget = widget_under_cursor
        while current_widget:
            if hasattr(self, "canvas_right") and current_widget == self.canvas_right:
                target_ax = self.ax_right
                target_fig = self.fig_right
                target_attr = "grid_enabled_right"
                selected_graph_name = "right"
                break
            elif hasattr(self, "canvas_left") and current_widget == self.canvas_left:
                target_ax = self.ax_left
                target_fig = self.fig_left
                target_attr = "grid_enabled_left"
                selected_graph_name = "left"
                break
            current_widget = current_widget.parent()

        current_state = getattr(self, target_attr, True) if target_attr else True
        if target_attr is not None:
            setattr(self, target_attr, current_state)

        if target_ax and target_fig:
            target_ax.grid(current_state)
            target_fig.canvas.draw_idle()

        grid_action = menu.addAction("Grid ✓" if current_state else "Grid")
        grid_action.setCheckable(True)
        grid_action.setChecked(current_state)

        range_action = menu.addAction("Set range")
        #grid_action.setChecked(current_state)

        smith_action = menu.addAction("Smith Normalized")

        # --- Export ---
        menu.addSeparator()
        export_action = menu.addAction("Export...")

        selected_action = menu.exec(event.globalPos())

        self.ax_to_network = {
            self.ax_left: rf.Network(frequency=self.freqs, s=self.s11, z0=50),
            self.ax_right: rf.Network(frequency=self.freqs, s=self.s11, z0=50)
        }

        # --- Handle actions ---
        if selected_action == view_menu:
            self.open_view()

        # --- Markers ---

        elif selected_action == marker1_graphic1_action:
            self.show_graphic1_marker1 = not self.show_graphic1_marker1
            self.toggle_marker_visibility(0, self.show_graphic1_marker1)

            if self.show_graphic1_marker1:
                self.info_panel_left.show()
            if not self.show_graphic1_marker1 and self.show_graphic1_marker2:
                self.info_panel_left.hide()

        elif selected_action == marker1_graphic2_action:
            self.show_graphic2_marker1 = not self.show_graphic2_marker1
            self.toggle_marker_visibility(1, self.show_graphic2_marker1)

            if self.show_graphic2_marker1:
                self.info_panel_right.show()
            if not self.show_graphic2_marker1 and self.show_graphic2_marker2:
                self.info_panel_right.hide()

        elif selected_action == marker2_graphic1_action:
            self.show_graphic1_marker2 = not self.show_graphic1_marker2
         
            self.toggle_marker2_visibility(0, self.show_graphic1_marker2)

            if self.show_graphic1_marker2:
                self.info_panel_left_2.show()
            if not self.show_graphic1_marker2 and self.show_graphic1_marker1:
                self.info_panel_left_2.hide()

        elif selected_action == marker2_graphic2_action:
            self.show_graphic2_marker2 = not self.show_graphic2_marker2
         
            self.toggle_marker2_visibility(1, self.show_graphic2_marker2)

            if self.show_graphic2_marker2:
                self.info_panel_right_2.show()
            if not self.show_graphic2_marker2 and self.show_graphic2_marker1:
                self.info_panel_right_2.hide()

        # --- Lock Markers ---

        elif selected_action == lock_markers_action:
            self.markers_locked = not self.markers_locked

            lock_markers_action.setChecked(self.markers_locked)

            settings.setValue("Markers/locked", self.markers_locked)
            
            if self.markers_locked:
                val = self.slider_left.val
                self.slider_right.set_val(val)
                self.update_right_cursor(val)

                val_2 = self.slider_left_2.val
                self.slider_right_2.set_val(val_2)
                self.update_right_cursor_2(val_2)

        # --- Grid ---
          
        elif selected_action == grid_action and target_ax and target_fig and target_attr:
            new_state = not getattr(self, target_attr, True)
            if target_attr is not None:
                setattr(self, target_attr, new_state)
            target_ax.grid(new_state)
            target_fig.canvas.draw_idle()
            grid_action.setText("Grid ✓" if new_state else "Grid")

        # --- Range ---

        elif selected_action == range_action:
            self.show_y_range_dialog(target_ax)

        # --- Smith Normalized ---
          
        # --- Toggle Smith Normalized ---
        elif selected_action == smith_action and target_ax and target_fig:
            # Determinar si el gráfico seleccionado es tipo Smith

            logging.info(f"selected_graph_name: {selected_graph_name}")
            logging.info(f"left_graph_type: {self.left_graph_type}")
            logging.info(f"right_graph_type: {self.right_graph_type}")
            logging.info(f"target_ax: {target_ax}")
            logging.info(f"target_fig: {target_fig}")

            is_smith = (selected_graph_name == "left" and self.left_graph_type.lower() == "smith diagram") or \
                    (selected_graph_name == "right" and self.right_graph_type.lower() == "smith diagram")

            if not is_smith:
                # Mostrar advertencia al usuario
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Smith Normalized",
                                        "The selected graph is not a Smith chart and cannot be normalized to Γ.")
                return

            # Tomar el Network asociado al ax
            net = self.ax_to_network.get(target_ax, None)
            if net is None:
                return

            # Dibujar Gamma normalizado
            gamma = net.s[:,0,0]
            target_ax.clear()
            target_ax.plot(gamma.real, gamma.imag, 'o-')
            target_ax.set_xlim(-1, 1)
            target_ax.set_ylim(-1, 1)
            target_ax.set_xlabel("Re(Γ)")
            target_ax.set_ylabel("Im(Γ)")
            target_ax.grid(True)
            target_fig.canvas.draw_idle()

        # --- Export ---

        elif selected_action == export_action:
            self.open_export_dialog(event)

        # --- Handle unit change ---
        elif current_unit == "dB":
            if selected_action == power_action:
                self.toggle_db_times(event, "Power ratio")
            elif selected_action == voltage_action:
                self.toggle_db_times(event, "Voltage ratio")
        elif current_unit in ("Power ratio", "Voltage ratio"):
            if selected_action == db_action:
                self.toggle_db_times(event, "dB")

        if self.show_graphic1_marker1 and self.show_graphic1_marker2 or self.show_graphic2_marker1 and self.show_graphic2_marker2:
            self.markers_button.show()
        else:
            self.markers_button.hide()

    def show_y_range_dialog(self, target_ax):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

        if target_ax is None:
            QMessageBox.warning(None, "Error", "No axis selected.")
            return

        if self.left_graph_type != "Smith Diagram" or self.right_graph_type != "Smith Diagram": 

            dlg = QDialog(self)
            dlg.setWindowTitle("Set Y Range")
            dlg.setFixedSize(250, 150)

            layout = QVBoxLayout(dlg)

            # --- Inputs ---
            l1 = QHBoxLayout()
            l1.addWidget(QLabel("Y min:"))
            ymin_edit = QLineEdit()
            ymin_edit.setPlaceholderText(str(target_ax.get_ylim()[0]))
            l1.addWidget(ymin_edit)
            layout.addLayout(l1)

            l2 = QHBoxLayout()
            l2.addWidget(QLabel("Y max:"))
            ymax_edit = QLineEdit()
            ymax_edit.setPlaceholderText(str(target_ax.get_ylim()[1]))
            l2.addWidget(ymax_edit)
            layout.addLayout(l2)

            # --- Buttons ---
            btn_layout = QHBoxLayout()
            apply_btn = QPushButton("Apply")
            cancel_btn = QPushButton("Cancel")
            btn_layout.addWidget(apply_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)

            # --- Logic ---
            def apply_clicked():
                try:
                    ymin_text = ymin_edit.text().strip()
                    ymax_text = ymax_edit.text().strip()

                    if not ymin_text and not ymax_text:
                        dlg.reject()
                        return

                    ymin = float(ymin_text) if ymin_text else target_ax.get_ylim()[0]
                    ymax = float(ymax_text) if ymax_text else target_ax.get_ylim()[1]

                    target_ax.set_ylim(ymin, ymax)
                    target_ax.figure.canvas.draw_idle()
                    dlg.accept()

                except ValueError:
                    QMessageBox.warning(dlg, "Invalid Input", "Please enter valid numbers for Y min and Y max.")

            apply_btn.clicked.connect(apply_clicked)
            cancel_btn.clicked.connect(dlg.reject)

            dlg.exec()

    def show_frequency_difference_dialog(self):
        import os
        from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout
        from PySide6.QtCore import Qt, QSettings

        # --- Path to config.ini ---
        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "ui", "graphics_windows", "ini", "config.ini")
        settings = QSettings(ruta_ini, QSettings.IniFormat)

        # --- Read cursor indices ---
        cursor_1_1_index = int(settings.value("Cursor_1_1/index", 0))
        cursor_1_2_index = int(settings.value("Cursor_1_2/index", 0))
        cursor_2_1_index = int(settings.value("Cursor_2_1/index", 0))
        cursor_2_2_index = int(settings.value("Cursor_2_2/index", 0))

        # --- LEFT PANEL VALUES ---
        left_marker1_vals = self._update_cursor_orig(cursor_1_1_index, return_values=True)
        left_marker2_vals = self._update_cursor_2_orig(cursor_2_1_index, return_values=True)
        left_diff = {key: left_marker2_vals[key] - left_marker1_vals[key] for key in ["freq", "mag", "phase"]}

        # --- RIGHT PANEL VALUES ---
        right_marker1_vals = self._update_cursor_right_orig(cursor_1_2_index, return_values=True)
        right_marker2_vals = self._update_cursor_2_right_orig(cursor_2_2_index, return_values=True)
        right_diff = {key: right_marker2_vals[key] - right_marker1_vals[key] for key in ["freq", "mag", "phase"]}

        # --- Determine which panels to show ---
        show_left = False
        show_right = False

        # All true → both panels
        if (self.show_graphic1_marker1 and self.show_graphic1_marker2) and (self.show_graphic2_marker1 and self.show_graphic2_marker2):
            show_left = True
            show_right = True
        # Only left
        elif (self.show_graphic1_marker1 and self.show_graphic1_marker2):
            show_left = True
        # Only right
        elif (self.show_graphic2_marker1 and self.show_graphic2_marker2):
            show_right = True

        # --- CREATE DIALOG ---
        dialog = QDialog(self)
        dialog.setWindowTitle("Marker Differences")
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QHBoxLayout()

        # --- Adjust size based on panels shown ---
        if show_left and show_right:
            dialog.setFixedSize(500, 120)
        else:  # only one panel
            dialog.setFixedSize(260, 120)

        # --- LEFT PANEL DISPLAY ---
        if show_left:
            left_layout = QVBoxLayout()
            left_title = QLabel("Left Panel Differences")
            left_title.setAlignment(Qt.AlignCenter)
            left_layout.addWidget(left_title)
            for key in ["freq", "mag", "phase"]:
                row = QHBoxLayout()
                row.addWidget(QLabel(f"{key.capitalize()} Diff:"))
                row.addWidget(QLabel(f"{left_diff[key]:.3f}"))
                left_layout.addLayout(row)
            layout.addLayout(left_layout)

        # --- RIGHT PANEL DISPLAY ---
        if show_right:
            right_layout = QVBoxLayout()
            right_title = QLabel("Right Panel Differences")
            right_title.setAlignment(Qt.AlignCenter)
            right_layout.addWidget(right_title)
            for key in ["freq", "mag", "phase"]:
                row = QHBoxLayout()
                row.addWidget(QLabel(f"{key.capitalize()} Diff:"))
                row.addWidget(QLabel(f"{right_diff[key]:.3f}"))
                right_layout.addLayout(row)
            layout.addLayout(right_layout)

        # --- Set layout and show ---
        dialog.setLayout(layout)
        dialog.exec()


    def toggle_db_times(self, event, new_mode):
        """
        Toggle between dB and times for the clicked graph.
        Saves independently for Left (Graphic1) and Right (Graphic2) graph in the INI.
        """
        import os
        from PySide6.QtCore import QSettings

        try:
            # Detect the graph clicked
            widget_under_cursor = QApplication.widgetAt(event.globalPos())
            if widget_under_cursor is None:
                return

            graph_number = 1  # default left
            current_widget = widget_under_cursor
            while current_widget:
                if hasattr(self, "canvas_right") and current_widget == self.canvas_right:
                    graph_number = 2
                    break
                elif hasattr(self, "canvas_left") and current_widget == self.canvas_left:
                    graph_number = 1
                    break
                current_widget = current_widget.parent()

            # Decide INI section based on graph
            ini_section = "Graphic1" if graph_number == 1 else "Graphic2"

            # Ruta del INI
            ui_dir = os.path.dirname(os.path.dirname(__file__))  
            ruta_ini = os.path.join(ui_dir, "ui", "graphics_windows", "ini", "config.ini")
            settings = QSettings(ruta_ini, QSettings.Format.IniFormat)

            settings.beginGroup(ini_section)

            # Guardar la unidad seleccionada
            settings.setValue("db_times", new_mode)

            # Guardar número de gráfico
            settings.setValue("graph_number", graph_number)

            settings.endGroup()
            settings.sync()

            logging.info(f"Unit {new_mode} saved for {ini_section}")

            self.update_plots_with_new_data(skip_reset=False)

            self.update_cursor()
            self.update_right_cursor()

            self.update_cursor_2()
            self.update_right_cursor_2()

        except Exception as e:
            logging.error(f"Error toggling db/times: {e}")

    def open_export_dialog(self, event):
        """Open the export dialog for the clicked graph."""
        # Determine which graph was clicked based on event position
        widget_under_cursor = QApplication.widgetAt(event.globalPos())
        
        try:
            # Default to left figure
            figure_to_export = self.fig_left
            panel_name = "Left Panel"
            
            # Try to determine which canvas was clicked
            if hasattr(self, 'canvas_right') and widget_under_cursor:
                # Walk up the widget hierarchy to find the canvas
                current_widget = widget_under_cursor
                while current_widget:
                    if current_widget == self.canvas_right:
                        figure_to_export = self.fig_right
                        panel_name = "Right Panel"
                        break
                    elif current_widget == self.canvas_left:
                        figure_to_export = self.fig_left
                        panel_name = "Left Panel"
                        break
                    current_widget = current_widget.parent()

            # Close previous export dialog if it exists
            if hasattr(self, 'export_dialog') and self.export_dialog is not None:
                self.export_dialog.close()
                self.export_dialog.deleteLater()
                self.export_dialog = None

            # Create and show new export dialog
            show_left_markers = [self.show_graphic1_marker1, self.show_graphic1_marker2]
            show_right_markers = [self.show_graphic2_marker1, self.show_graphic2_marker2]

            update_cursor_left = [self.update_cursor, self.update_cursor_2]
            update_cursor_right = [self.update_right_cursor, self.update_right_cursor_2]

            self.export_dialog = ExportDialog(
                self,
                figure_to_export,
                left_graph=self.left_graph_type,
                right_graph=self.right_graph_type,
                freqs=self.freqs,
                show_markers_left = show_left_markers,
                show_markers_right = show_right_markers,
                update_cursor_left = update_cursor_left,
                update_cursor_right = update_cursor_right
            )

            self.export_dialog.setWindowTitle(f"Export Graph - {panel_name}")
            self.export_dialog.exec()
            
        except Exception as e:
            logging.error(f"Error opening export dialog: {e}")
            QMessageBox.warning(self, "Export Error", f"Failed to open export dialog: {str(e)}")


    # =================== MARKERS ==================

    def edit_graphics_markers(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.edit_graphics_window import EditGraphics
        self.edit_graphics_window = EditGraphics(nano_window=self) 
        self.edit_graphics_window.show()

    # =================== VIEW ==================

    def open_view(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.view_window import View
        
        # Cerrar la instancia anterior si existe
        if hasattr(self, 'view_window') and self.view_window is not None:
            self.view_window.close()
            self.view_window.deleteLater()
            self.view_window = None

        # Crear nueva instancia de View
        self.view_window = View(nano_window=self)
        self.view_window.show()
        self.view_window.raise_()
        self.view_window.activateWindow()

    # =================== TOGGLE MARKERS==================

    def clear_freq_edit(self, edit_widget):
        edit_widget.blockSignals(True) 
        edit_widget.setText("--")
        edit_widget.setFixedWidth(edit_widget.fontMetrics().horizontalAdvance(edit_widget.text()) + 4)
        edit_widget.blockSignals(False)

    def toggle_marker_visibility(self, marker_index, show=True):
        marker = self.markers[marker_index]
        cursor = marker["cursor"]
        slider = marker["slider"]
        labels = marker["label"]
        update_cursor_func = marker.get("update_cursor", None)

        logging.info(f"cursor data: {cursor.get_data()}")

        # Check if cursor is valid before using it
        if cursor is None or cursor.figure is None:
            logging.warning(f"[graphics_window.toggle_marker_visibility] Cursor {marker_index} is invalid, skipping toggle")
            return

        cursor.set_visible(show)

        if marker_index == 0:  
            slider = self.slider_left
            slider_2 = self.slider_left_2
            fig = self.fig_left
        elif marker_index == 1: 
            slider = self.slider_right
            slider_2 = self.slider_right_2
            fig = self.fig_right
        else:
            logging.warning(f"[move_marker2_slider_left] Invalid marker_index {marker_index}")
            return

        if show:
            slider_2.ax.set_position([0.55,0.04,0.35,0.03])

            slider.ax.set_visible(True)
            slider.set_active(True)
            if hasattr(marker, "slider_callback"):
                slider.on_changed(marker.slider_callback)

            if update_cursor_func:
                update_cursor_func(0)

            edit_value = labels["freq"]
            edit_value.setEnabled(True)
            if self.freqs is not None and len(self.freqs) > 0:
                if self.freqs[0] < 1e6:  
                    edit_value.setText(f"{self.freqs[0]/1e3:.3f}")
                elif self.freqs[0] < 1e9:  
                    edit_value.setText(f"{self.freqs[0]/1e6:.3f}")
                else: 
                    edit_value.setText(f"{self.freqs[0]/1e9:.3f}")
            else:
                edit_value.setText("--") 

        else:
            slider.set_val(0)
            slider.ax.set_visible(False)
            slider.set_active(False)

            edit_value = labels["freq"]
            edit_value.setEnabled(False)
            edit_value.setText("0")

            # --- Limpiar otros labels ---
            labels["val"].setText(f"{self.left_s_param if marker_index==0 else 'S11'}: -- + j--")
            labels["mag"].setText("|S11|: --")
            labels["phase"].setText("Phase: --")
            labels["z"].setText("Z: -- + j--")
            labels["il"].setText("IL: --")
            labels["vswr"].setText("VSWR: --")

            slider_2.ax.set_position([0.25,0.04,0.5,0.03])

        # Only draw if cursor and figure are valid
        if cursor is not None and cursor.figure is not None and cursor.figure.canvas is not None:
            cursor.figure.canvas.draw_idle()
        else:
            logging.warning(f"[graphics_window.toggle_marker_visibility] Cannot draw cursor {marker_index}, figure or canvas is None")

    def toggle_marker2_visibility(self, marker_index, show_markers):
        """
        Move Marker 2 slider to the left of the corresponding canvas
        without hiding or deactivating it.
        """
        marker_2 = self.markers[marker_index]

        cursor_2 = marker_2["cursor_2"]
        slider_2 = marker_2["slider_2"]
        labels_2 = marker_2["label_2"]

        update_cursor_func_2 = marker_2.get("update_cursor_2", None)

        logging.info(f"cursor_2 data: {cursor_2.get_data()}")

        if cursor_2 is None or cursor_2.figure is None:
            logging.warning(f"[graphics_window.toggle_marker_visibility_2] Cursor {marker_index} is invalid, skipping toggle")
            return

        cursor_2.set_visible(show_markers)

        if marker_index == 0:  
            slider = self.slider_left
            slider_2 = self.slider_left_2
            fig = self.fig_left
        elif marker_index == 1: 
            slider = self.slider_right
            slider_2 = self.slider_right_2
            fig = self.fig_right
        else:
            logging.warning(f"[move_marker2_slider_left] Invalid marker_index {marker_index}")
            return

        if show_markers:

            slider_2.ax.set_visible(True)
            slider_2.set_active(True)

            slider.ax.set_position([0.1, 0.04, 0.35, 0.03])

            #slider_2.on_changed(lambda val: update_cursor(int(val), from_slider=True))

            if slider.ax.figure is not None:
                slider.ax.figure.canvas.draw_idle()

            if update_cursor_func_2:
                update_cursor_func_2(0)

            edit_value_2 = labels_2["freq"]
            edit_value_2.setEnabled(True)
            if self.freqs is not None and len(self.freqs) > 0:
                if self.freqs[0] < 1e6:  
                    edit_value_2.setText(f"{self.freqs[0]/1e3:.3f}")
                elif self.freqs[0] < 1e9:  
                    edit_value_2.setText(f"{self.freqs[0]/1e6:.3f}")
                else: 
                    edit_value_2.setText(f"{self.freqs[0]/1e9:.3f}")
            else:
                edit_value_2.setText("--") 
   
        elif not show_markers:

            slider_2.set_val(0)
            slider_2.ax.set_visible(False)
            slider_2.set_active(False) 

            # --- Limpiar otros labels ---
            labels_2["val"].setText(f"{self.left_s_param if marker_index==0 else 'S11'}: -- + j--")
            labels_2["mag"].setText("|S11|: --")
            labels_2["phase"].setText("Phase: --")
            labels_2["z"].setText("Z: -- + j--")
            labels_2["il"].setText("IL: --")
            labels_2["vswr"].setText("VSWR: --")

            slider.ax.set_position([0.25,0.04,0.5,0.03])

        # Only draw if cursor and figure are valid
        if cursor_2 is not None and cursor_2.figure is not None and cursor_2.figure.canvas is not None:
            cursor_2.figure.canvas.draw_idle()
        else:
            logging.warning(f"[graphics_window.toggle_marker_visibility] Cannot draw cursor {marker_index}, figure or canvas is None")

    # =================== SWEEP FUNCTIONALITY ===================
    
    def load_sweep_configuration(self):
        """Load sweep configuration from sweep options config file."""
        
        try:
            # Get path to sweep options config
            actual_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sweep_config_path = os.path.join(actual_dir, "ui", "sweep_window", "config", "config.ini")
            sweep_config_path = os.path.normpath(sweep_config_path)

            if os.path.exists(sweep_config_path):
                settings = QSettings(sweep_config_path, QSettings.Format.IniFormat)

                self.start_freq_hz = int(float(str(settings.value("Frequency/StartFreqHz", 50000))))
                self.stop_freq_hz = int(float(str(settings.value("Frequency/StopFreqHz", 1.5e9))))
                self.segments = int(str(settings.value("Frequency/Segments", 101)))

                logging.info(f"[graphics_window.load_sweep_configuration] Loaded sweep config: "
                            f"{self.start_freq_hz/1e6:.3f} MHz - {self.stop_freq_hz/1e6:.3f} MHz, "
                            f"{self.segments} points")

                self.start_unit = settings.value("Frequency/StartUnit", "kHz")
                self.stop_unit = settings.value("Frequency/StopUnit", "GHz")

                # Update info label if it exists
                if hasattr(self, 'sweep_info_label'):
                    self.update_sweep_info_label()

            else:
                # Default values if config file doesn't exist
                self.start_freq_hz = 50000
                self.stop_freq_hz = int(1.5e9)
                self.segments = 101
                logging.warning("[graphics_window.load_sweep_configuration] Config file not found, using defaults")

        except Exception as e:
            logging.error(f"[graphics_window.load_sweep_configuration] Error loading sweep config: {e}")
            # Fallback defaults
            self.start_freq_hz = 50000
            self.stop_freq_hz = int(1.5e9)
            self.segments = 101

    def update_sweep_info_label(self):
        """Update the sweep information label with current configuration."""
        try:
            start_val = self.start_freq_hz
            stop_val  = self.stop_freq_hz

            logging.info(f"[update_sweep_info_label] start_val={start_val} Hz")
            logging.info(f"[update_sweep_info_label] stop_val={stop_val} Hz")

            start_unit = self.start_unit
            stop_unit = self.stop_unit

            logging.info(f"[update_sweep_info_label] start_val={start_val}, stop_val={stop_val}")
            logging.info(f"[update_sweep_info_label] start_unit={start_unit}, stop_unit={stop_unit}")

            # Convert to proper units
            if start_unit.lower() == "khz":
                freq_start_str = f"{start_val/1e3:.1f} kHz"
            elif start_unit.lower() == "mhz":
                freq_start_str = f"{start_val/1e6:.3f} MHz"
            elif start_unit.lower() == "ghz":
                freq_start_str = f"{start_val/1e9:.3f} GHz"
            else:
                freq_start_str = f"{start_val} Hz"

            if stop_unit.lower() == "khz":
                freq_stop_str = f"{stop_val/1e3:.1f} kHz"
            elif stop_unit.lower() == "mhz":
                freq_stop_str = f"{stop_val/1e6:.3f} MHz"
            elif stop_unit.lower() == "ghz":
                freq_stop_str = f"{stop_val/1e9:.3f} GHz"
            else:
                freq_stop_str = f"{stop_val} Hz"

            info_text = f"Sweep: {freq_start_str} - {freq_stop_str}, {self.segments} points"
            self.sweep_info_label.setText(info_text)
            logging.info(f"[graphics_window.update_sweep_info_label] Updated info: {info_text}")
        except Exception as e:
            logging.error(f"[graphics_window.update_sweep_info_label] Error updating label: {e}")

    def run_sweep(self):
        """Run a sweep on the connected device."""
        logging.info("[graphics_window.run_sweep] Starting sweep operation")
        
        if not self.vna_device:
            error_msg = "No VNA device connected. Cannot perform sweep."
            QMessageBox.warning(self, "No Device", error_msg)
            logging.warning(f"[graphics_window.run_sweep] {error_msg}")
            return
            
        # Check and ensure device connection
        if not self.vna_device.connected():
            logging.warning("[graphics_window.run_sweep] Device not connected, attempting to reconnect...")
            try:
                self.vna_device.connect()
                if not self.vna_device.connected():
                    error_msg = "VNA device connection failed. Please check device and try again."
                    QMessageBox.warning(self, "Connection Failed", error_msg)
                    logging.error(f"[graphics_window.run_sweep] {error_msg}")
                    return
                logging.info("[graphics_window.run_sweep] Device reconnected successfully")
            except Exception as e:
                error_msg = f"Failed to reconnect to VNA device: {str(e)}"
                QMessageBox.critical(self, "Connection Error", error_msg)
                logging.error(f"[graphics_window.run_sweep] {error_msg}")
                return
            
        try:
            # Reset sliders and clear all marker information before starting sweep
            logging.info("[graphics_window.run_sweep] Preparing for sweep - resetting sliders and clearing info")
            self._reset_sliders_before_sweep()
            
            # Disable sweep button and show progress bar
            self.sweep_button.setEnabled(False)
            self.sweep_button.setText("Sweeping...")
            self.sweep_progress_bar.setVisible(True)
            self.sweep_progress_bar.setValue(0)
            
            # Also disable reconnect button during sweep
            self.reconnect_button.setEnabled(False)
            
            # Load current sweep configuration
            self.load_sweep_configuration()
            
            device_type = type(self.vna_device).__name__
            logging.info(f"[graphics_window.run_sweep] Running sweep on {device_type}")
            logging.info(f"[graphics_window.run_sweep] Frequency range: {self.start_freq_hz/1e6:.3f} MHz - {self.stop_freq_hz/1e6:.3f} MHz")
            logging.info(f"[graphics_window.run_sweep] Number of points: {self.segments}")
            
            # Validate sweep parameters
            if self.segments < 11 or self.segments > 101:
                error_msg = f"Invalid number of sweep points: {self.segments}. Must be between 11 and 101."
                QMessageBox.warning(self, "Invalid Parameters", error_msg)
                logging.error(f"[graphics_window.run_sweep] {error_msg}")
                self._reset_sweep_ui()
                return
                
            if self.start_freq_hz >= self.stop_freq_hz:
                error_msg = f"Invalid frequency range: start ({self.start_freq_hz/1e6:.3f} MHz) must be less than stop ({self.stop_freq_hz/1e6:.3f} MHz)"
                QMessageBox.warning(self, "Invalid Parameters", error_msg)
                logging.error(f"[graphics_window.run_sweep] {error_msg}")
                self._reset_sweep_ui()
                return
            
            # Update progress bar
            self.sweep_progress_bar.setValue(10)
            QApplication.processEvents()  # Force UI update
            
            # Configure VNA sweep parameters
            logging.info(f"[graphics_window.run_sweep] Setting datapoints to {self.segments}")
            self.vna_device.datapoints = self.segments
            self.sweep_progress_bar.setValue(20)
            QApplication.processEvents()
            
            # Set sweep range
            logging.info(f"[graphics_window.run_sweep] Setting sweep range: {self.start_freq_hz} - {self.stop_freq_hz} Hz")
            self.vna_device.setSweep(self.start_freq_hz, self.stop_freq_hz)
            self.sweep_progress_bar.setValue(40)
            QApplication.processEvents()
            
            # Read frequency points
            logging.info("[graphics_window.run_sweep] Reading frequency points...")
            freqs_data = self.vna_device.read_frequencies()
            freqs = np.array(freqs_data)
            logging.info(f"[graphics_window.run_sweep] Got {len(freqs)} frequency points")
            self.sweep_progress_bar.setValue(60)
            QApplication.processEvents()
            
            # Read S11 data
            logging.info("[graphics_window.run_sweep] Reading S11 data...")
            s11_data = self.vna_device.readValues("data 0")
            s11_med = np.array(s11_data)

            logging.info(f"[graphics_window.run_sweep] Got {len(s11_med)} S11 data points")
            self.sweep_progress_bar.setValue(80)
            QApplication.processEvents()
            
            # Read S21 data
            logging.info("[graphics_window.run_sweep] Reading S21 data...")
            s21_data = self.vna_device.readValues("data 1")
            s21_med = np.array(s21_data)

            logging.info(f"[graphics_window.run_sweep] Got {len(s21_med)} S21 data points")
            self.sweep_progress_bar.setValue(90)
            QApplication.processEvents()

            # Apply calibration if applicable
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
            settings = QSettings(config_path, QSettings.Format.IniFormat)
            calibration_method = settings.value("Calibration/Method", "---")
            kit_name = settings.value("Calibration/Name", "---")
            if "_" in kit_name:
                kit_name = kit_name.rsplit("_", 1)[0]

            logging.info(f"[graphics_window.run_sweep] calibration_method leído: '{calibration_method}'")

            # Cal_Directory
            cal_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Calibration", "osm_results")
            methods = Methods(cal_dir)

            kits_ok = settings.value("Calibration/Kits", False, type=bool)
            no_calibration = settings.value("Calibration/NoCalibration", False, type=bool)
            is_import_dut = settings.value("Calibration/isImportDut", False, type=bool)

            if not kits_ok and not no_calibration and not is_import_dut:
                self.update_calibration_label_from_method(calibration_method)
            elif not is_import_dut:
                self.update_calibration_label_from_method()

            if kits_ok == False and no_calibration == True and not is_import_dut:
                s11 = s11_med
                s21 = s21_med

            elif kits_ok == False and no_calibration == False and not is_import_dut:
                print(f"kit_name calibrador: {kit_name}")
                if calibration_method == "OSM (Open - Short - Match)":
                    s11 = methods.osm_calibrate_s11(s11_med)
                    s21 = s21_med  # S21 sin calibrar
                elif calibration_method == "Normalization":
                    # Cal_Directory
                    cal_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Calibration", "thru_results")
                    methods = Methods(cal_dir)
                    s11 = s11_med  # S11 sin calibrar
                    s21 = methods.normalization_calibrate_s21(s21_med)
                elif calibration_method == "1-Port+N":
                    # Cal_Directory
                    cal_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Calibration", "osm_results")
                    methods = Methods(cal_dir)

                    s11 = methods.osm_calibrate_s11(s11_med)

                    cal_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Calibration", "thru_results")
                    methods = Methods(cal_dir)
                
                    s21 = methods.normalization_calibrate_s21(s21_med)

                elif calibration_method == "Enhanced-Response":
                    # Cal_Directory
                    osm_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Calibration", "osm_results")
                    thru_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Calibration", "thru_results")

                    s11, s21 = methods.enhanced_response_calibrate(s11_med, s21_med, osm_dir, thru_dir)
                else:
                    s11 = s11_med
                    s21 = s21_med
            elif kits_ok == True and no_calibration == False and not is_import_dut:
                selected_kit_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Calibration", "kits")
                kits_calibrator = KitsCalibrator(selected_kit_dir)
                s11, s21 = kits_calibrator.kits_selected(calibration_method, kit_name, s11_med, s21_med)

            elif is_import_dut:

                settings.setValue("Calibration/DUT", True)

                data_dut = rf.Network(self.dut)

                freqs = data_dut.f

                s11 = data_dut.s[:, 0, 0]  
                s21 = data_dut.s[:, 1, 0]  

            # Validate data consistency
            if len(freqs) != len(s11) or len(freqs) != len(s21):
                error_msg = f"Data length mismatch: freqs={len(freqs)}, s11={len(s11)}, s21={len(s21)}"
                logging.error(f"[graphics_window.run_sweep] {error_msg}")
                QMessageBox.critical(self, "Data Error", f"Sweep data inconsistency: {error_msg}")
                self._reset_sweep_ui()
                return
            
            # Update internal data
            self.freqs = freqs
            self.s11 = s11
            self.s21 = s21
            
            # Update plots with new data (skip graph-change reset since we're doing a sweep reset)
            self.update_plots_with_new_data(skip_reset=True)
            self.sweep_progress_bar.setValue(100)
            QApplication.processEvents()
            
            # Reset markers and all marker-dependent information after new sweep
            self._reset_markers_after_sweep()
            
            # Additional reset specifically for Run Sweep to ensure cursor info is updated
            def final_run_sweep_cursor_reset():
                try:
                    logging.info("[graphics_window.run_sweep] FINAL: Ensuring cursor information is displayed after run sweep")
                    
                    # Force sliders to leftmost position
                    if hasattr(self, 'slider_left') and self.slider_left:
                        self.slider_left.set_val(0)
                    if hasattr(self, 'slider_left_2') and self.slider_left_2:
                        self.slider_left_2.set_val(0)
                    if hasattr(self, 'slider_right') and self.slider_right:
                        self.slider_right.set_val(0)
                    if hasattr(self, 'slider_right_2') and self.slider_right_2:
                        self.slider_right_2.set_val(0)
                    
                    # Force cursor information update
                    if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                        self.update_cursor(0)
                        logging.info("[graphics_window.run_sweep] FINAL: Left cursor info updated to show minimum frequency data")

                    if hasattr(self, 'update_cursor_2') and callable(self.update_cursor_2):
                        self.update_cursor_2(0)
                        logging.info("[graphics_window.run_sweep] FINAL: Left cursor info updated to show minimum frequency data")
                    
                    if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                        self.update_right_cursor(0)
                        logging.info("[graphics_window.run_sweep] FINAL: Right cursor info updated to show minimum frequency data")
                    
                    if hasattr(self, 'update_right_cursor_2') and callable(self.update_right_cursor_2):
                        self.update_right_cursor_2(0)
                        logging.info("[graphics_window.run_sweep] FINAL: Right cursor info updated to show minimum frequency data")
                        
                    # Force canvas redraw
                    if hasattr(self, 'canvas_left') and self.canvas_left:
                        self.canvas_left.draw()
                    if hasattr(self, 'canvas_right') and self.canvas_right:
                        self.canvas_right.draw()
                        
                except Exception as e:
                    logging.warning(f"[graphics_window.run_sweep] Error in final cursor reset: {e}")
            
            # Execute final reset after 200ms to ensure everything is configured
            QTimer.singleShot(200, final_run_sweep_cursor_reset)
            
            # Success message
            success_msg = f"Sweep completed successfully.\n{len(freqs)} data points acquired.\nFrequency range: {freqs[0]/1e6:.3f} - {freqs[-1]/1e6:.3f} MHz"
            logging.info(f"[graphics_window.run_sweep] {success_msg}")
            
            # Reset UI after longer delay to show 100% completion and allow cursor updates
            QTimer.singleShot(700, self._reset_sweep_ui)
            
        except Exception as e:
            error_msg = f"Error during sweep: {str(e)}"
            logging.error(f"[graphics_window.run_sweep] {error_msg}")
            logging.error(f"[graphics_window.run_sweep] Exception details: {type(e).__name__}")
            QMessageBox.critical(self, "Sweep Error", error_msg)
            self._reset_sweep_ui()

    def _reset_sweep_ui(self):
        """Reset the sweep UI elements to their initial state."""
        self.sweep_button.setEnabled(True)
        self.sweep_button.setText("Run Sweep")
        self.sweep_progress_bar.setVisible(False)
        self.sweep_progress_bar.setValue(0)
        
        # Update reconnect button state based on device connection
        self._update_reconnect_button_state()

    def reconnect_device(self):
        """Reconnect to the VNA device."""
        logging.info("[graphics_window.reconnect_device] Manual reconnection requested")
        
        if not self.vna_device:
            # Show error dialog but don't disable the button
            error_msg = ("No VNA device is currently available.\n\n"
                        "Please:\n"
                        "1. Ensure your VNA device is connected via USB\n"
                        "2. Remove and reconnect the device\n"
                        "3. Try clicking Connect again\n\n"
                        "If the problem persists, check USB connection and restart the program.")
            QMessageBox.critical(self, "Device Connection Error", error_msg)
            logging.warning(f"[graphics_window.reconnect_device] No VNA device available")
            return
            
        # Disable reconnect button during reconnection
        self.reconnect_button.setEnabled(False)
        self.reconnect_button.setText("Connecting...")
        # Remove custom styling to use standard disabled button appearance
        self.reconnect_button.setStyleSheet("")
        # Force complete style refresh to clear any persistent styling
        if hasattr(self.reconnect_button, 'style'):
            self.reconnect_button.style().unpolish(self.reconnect_button)
            self.reconnect_button.style().polish(self.reconnect_button)
            self.reconnect_button.update()
        
        # Also disable sweep button during reconnection
        self.sweep_button.setEnabled(False)
        
        try:
            device_type = type(self.vna_device).__name__
            logging.info(f"[graphics_window.reconnect_device] Attempting to reconnect {device_type}")
            
            # If already connected, disconnect first
            if self.vna_device.connected():
                logging.info("[graphics_window.reconnect_device] Device already connected, disconnecting first")
                self.vna_device.disconnect()
                
            # Attempt reconnection
            self.vna_device.connect()
            
            if self.vna_device.connected():
                success_msg = f"Successfully reconnected to {device_type}"
                logging.info(f"[graphics_window.reconnect_device] {success_msg}")
                QMessageBox.information(self, "Connection Successful", success_msg)
                
                # Reset sliders and cursors to initial position after successful reconnection
                self._reset_sliders_after_reconnect()
                
                # Enable sweep button since device is now connected
                self.sweep_button.setEnabled(True)
            else:
                # Connection failed - show detailed error dialog but keep button enabled
                error_msg = (f"Failed to connect to {device_type}.\n\n"
                           "Please try the following:\n"
                           "1. Remove and reconnect the VNA device\n"
                           "2. Check USB cable and port\n"
                           "3. Ensure device drivers are properly installed\n"
                           "4. Close other software that might be using the device\n"
                           "5. Try clicking Connect again\n\n"
                           "The Connect button remains available for retry.")
                logging.error(f"[graphics_window.reconnect_device] Connection failed for {device_type}")
                QMessageBox.critical(self, "Connection Failed", error_msg)
                
        except Exception as e:
            # Exception during connection - show error but keep button enabled
            error_msg = (f"Error during device connection: {str(e)}\n\n"
                        "Please try the following:\n"
                        "1. Remove and reconnect the VNA device\n"
                        "2. Check USB cable and port\n"
                        "3. Restart the application if needed\n"
                        "4. Try clicking Connect again")
            logging.error(f"[graphics_window.reconnect_device] Exception during connection: {str(e)}")
            QMessageBox.critical(self, "Connection Error", error_msg)
            
        finally:
            # Reset reconnect button state
            self._update_reconnect_button_state()
            
            # Re-enable sweep button after reconnection attempt
            self.sweep_button.setEnabled(True)
            
    def _update_reconnect_button_state(self):
        """Update the reconnect button state based on device connection."""
        if not self.vna_device:
            # Instead of disabling, show "Connect" button so user can try to connect
            self.reconnect_button.setEnabled(True)
            self.reconnect_button.setText("Connect")
            self.reconnect_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45A049;
                }
            """)
            return
            
        is_connected = self.vna_device.connected()
        
        if is_connected:
            # Connected state: standard button saying "Reconnect" (same style as Run Sweep button)
            self.reconnect_button.setEnabled(True)
            self.reconnect_button.setText("Reconnect")
            # Force reset to standard button appearance by setting style to None and updating
            self.reconnect_button.setStyleSheet("")
            self.reconnect_button.style().unpolish(self.reconnect_button)
            self.reconnect_button.style().polish(self.reconnect_button)
            self.reconnect_button.update()
        else:
            # Disconnected state: green button saying "Connect"
            self.reconnect_button.setEnabled(True)
            self.reconnect_button.setText("Connect")
            self.reconnect_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45A049;
                }
            """)

    
    def get_graph_unit(self, graph_number):
        """Read the unit from INI for left (1) or right (2) graph."""
        try:
            ui_dir = os.path.dirname(os.path.dirname(__file__))
            ini_path = os.path.join(ui_dir, "ui", "graphics_windows", "ini", "config.ini")
            settings = QSettings(ini_path, QSettings.Format.IniFormat)
            
            group_name = f"Graphic{graph_number}"
            settings.beginGroup(group_name)
            unit = settings.value("db_times", "dB")  # default dB
            settings.endGroup()
            
            return unit
        except Exception as e:
            logging.error(f"Error reading unit from INI: {e}")
            return "dB"

    def update_plots_with_new_data(self, skip_reset=False):
        """Update both plots with new sweep data."""
        try:
            logging.info("[graphics_window.update_plots_with_new_data] Updating plots with new sweep data")
            
            if self.freqs is None or self.s11 is None or self.s21 is None:
                logging.warning("[graphics_window.update_plots_with_new_data] No data available for plotting")
                return
                
            logging.info(f"[graphics_window.update_plots_with_new_data] New data: {len(self.freqs)} frequency points")
            
            # Get current graph settings
            actual_dir = os.path.dirname(os.path.dirname(__file__))  
            ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")
            settings = QSettings(ruta_ini, QSettings.Format.IniFormat)

            graph_type_tab1 = settings.value("Tab1/GraphType1", "Smith Diagram")
            s_param_tab1    = settings.value("Tab1/SParameter", "S11")
            graph_type_tab2 = settings.value("Tab2/GraphType2", "Magnitude")
            s_param_tab2    = settings.value("Tab2/SParameter", "S11")
            
            trace_color1 = settings.value("Graphic1/TraceColor", "blue")
            marker_color1 = settings.value("Graphic1/MarkerColor1", "blue")
            marker2_color1 = settings.value("Graphic1/MarkerColor2", "blue")
            background_color1 = settings.value("Graphic1/BackgroundColor", "blue")
            text_color1 = settings.value("Graphic1/TextColor", "blue")
            axis_color1 = settings.value("Graphic1/AxisColor", "blue")
            trace_size1 = int(settings.value("Graphic1/TraceWidth", 2))
            marker_size1 = int(settings.value("Graphic1/MarkerWidth1", 6))
            marker2_size1 = int(settings.value("Graphic1/MarkerWidth2", 6))

            trace_color2 = settings.value("Graphic2/TraceColor", "blue")
            marker_color2 = settings.value("Graphic2/MarkerColor1", "blue")
            marker2_color2 = settings.value("Graphic2/MarkerColor2", "blue")
            background_color2 = settings.value("Graphic2/BackgroundColor", "blue")
            text_color2 = settings.value("Graphic2/TextColor", "blue")
            axis_color2 = settings.value("Graphic2/AxisColor", "blue")
            trace_size2 = int(settings.value("Graphic2/TraceWidth", 2))
            marker_size2 = int(settings.value("Graphic2/MarkerWidth1", 6))
            marker2_size2 = int(settings.value("Graphic2/MarkerWidth2", 6))

            # Determine which data to plot for each panel
            s_data_left = self.s11 if s_param_tab1 == "S11" else self.s21
            s_data_right = self.s11 if s_param_tab2 == "S11" else self.s21
            
            # Clear existing plots
            self.ax_left.clear()
            self.ax_right.clear()

            # Recreate left panel plot
            logging.info(f"[graphics_window.update_plots_with_new_data] Recreating left plot: {graph_type_tab1} - {s_param_tab1}")

            unit_left = self.get_graph_unit(1)

            self._recreate_single_plot(
                ax=self.ax_left,
                fig=self.fig_left,
                s_data=s_data_left,
                freqs=self.freqs,
                graph_type=graph_type_tab1,
                s_param=s_param_tab1,
                tracecolor=trace_color1,
                markercolor=marker_color1,
                brackground_color_graphics=background_color1,
                text_color=text_color1,
                axis_color=axis_color1,
                linewidth=trace_size1,
                markersize=marker_size1,
                unit= unit_left,
                cursor_graph=self.cursor_left,
                cursor_graph_2=self.cursor_left_2
            )

            unit_right = self.get_graph_unit(2)
            
            # Recreate right panel plot
            logging.info(f"[graphics_window.update_plots_with_new_data] Recreating right plot: {graph_type_tab2} - {s_param_tab2}")
            self._recreate_single_plot(
                ax=self.ax_right,
                fig=self.fig_right,
                s_data=s_data_right,
                freqs=self.freqs,
                graph_type=graph_type_tab2,
                s_param=s_param_tab2,
                tracecolor=trace_color2,
                markercolor=marker_color2,
                brackground_color_graphics=background_color2,
                text_color=text_color2,
                axis_color=axis_color2,
                linewidth=trace_size2,
                markersize=marker_size2,
                unit=unit_right,
                cursor_graph=self.cursor_right,
                cursor_graph_2=self.cursor_right_2
            )
            
            # Update data references in cursor functions
            logging.info("[graphics_window.update_plots_with_new_data] Updating cursor data references")
            if hasattr(self, 'update_left_data') and self.update_left_data:
                self.update_left_data(s_data_left, self.freqs)
            if hasattr(self, 'update_right_data') and self.update_right_data:
                self.update_right_data(s_data_right, self.freqs)
            
            # Recreate cursors for the new graph types
            logging.info("[graphics_window.update_plots_with_new_data] Recreating cursors for new graph types")
            self._recreate_cursors_for_new_plots(marker_color_left=marker_color1, marker_color_right=marker_color2, marker2_color_left=marker2_color1,
                marker2_color_right=marker2_color2, marker1_size_left=marker_size1, marker1_size_right=marker_size2, marker2_size_left=marker2_size1, marker2_size_right=marker2_size2)

            # Reset sliders and markers to leftmost position (index 0) for graph type changes
            # Skip this reset if we're doing a sweep (will be handled by _reset_markers_after_sweep)
            if not skip_reset:
                logging.info("[graphics_window.update_plots_with_new_data] Resetting sliders and markers to initial position")
                self._reset_sliders_and_markers_for_graph_change()
            else:
                logging.info("[graphics_window.update_plots_with_new_data] Skipping reset - will be handled by sweep reset")
            
            # Force redraw
            self.canvas_left.draw()
            self.canvas_right.draw()
            
            logging.info("[graphics_window.update_plots_with_new_data] Plots updated successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window.update_plots_with_new_data] Error updating plots: {e}")
    
    def _recreate_single_plot(self, ax, fig, s_data, freqs, graph_type, s_param, 
                            tracecolor, markercolor, brackground_color_graphics, text_color, axis_color, linewidth, markersize,
                            unit="dB", cursor_graph=None, cursor_graph_2 = None):
        """Recreate a single plot with new data."""
        try:
            from matplotlib.lines import Line2D

            # Use new calibration structure
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
            settings_calibration = QSettings(config_path, QSettings.Format.IniFormat)

            settings_calibration.setValue("Calibration/isImportDut", False)

            fig.patch.set_facecolor(f"{brackground_color_graphics}")
            ax.set_facecolor(f"{brackground_color_graphics}")

            if graph_type == "Smith Diagram":
                # Use consolidated Smith chart functionality
                from ..utils.smith_chart_utils import SmithChartConfig, SmithChartBuilder
                
                # Create custom config to match original settings
                config = SmithChartConfig()
                config.background_color = brackground_color_graphics
                config.axis_color = axis_color
                config.text_color = axis_color
                config.trace_color = tracecolor
                config.linewidth = linewidth
                
                # Use builder to recreate Smith chart on existing axis
                builder = SmithChartBuilder(config)
                builder.ax = ax
                builder.fig = fig
                
                # Create network and draw Smith chart
                network = builder.create_network_from_data(freqs, s_data)
                builder.draw_base_smith_chart(network, draw_labels=True, show_legend=False)
                
                # Add legend
                builder.add_legend([s_param], colors=[tracecolor])
                
                # Update data line styles
                builder.update_data_line_styles(freqs, color=tracecolor, linewidth=linewidth)
                        
            elif graph_type == "Magnitude":
                # Plot magnitude

                if unit == "dB":
                    magnitude_db = 20 * np.log10(np.abs(s_data))
                elif unit == "Power ratio":
                    magnitude_db = np.abs(s_data)**2
                elif unit == "Voltage ratio":
                    magnitude_db = np.abs(s_data)

                cursor_graph.set_xdata([freqs[0] * 1e-6])
                cursor_graph.set_ydata([magnitude_db[0]])

                fig.canvas.draw_idle()

                cursor_x = cursor_graph.get_xdata()[0]
                cursor_y = cursor_graph.get_ydata()[0]

                logging.info(f"[Cursor] Frequency: {cursor_x:.6f} MHz, Magnitude: {cursor_y:.3f} {unit}")

                ax.plot(freqs / 1e6, magnitude_db, color=tracecolor, linewidth=linewidth)

                ax.set_xlabel(r"$\mathrm{Frequency\ [MHz]}$", color=f"{text_color}")
                if unit == "dB":
                    ax.set_ylabel(r"$%s\ \mathrm{[dB]}$" % s_param, color=text_color)
                    ax.set_title(r"$%s\ \mathrm{Magnitude\ [dB]}$" % s_param, color=text_color)
                else:
                    ax.set_ylabel(r"$|%s|$" % s_param, color=f"{text_color}")
                    ax.set_title(r"$%s\ \mathrm{Magnitude}$" % s_param, color=text_color)
                # Set X-axis limits with margins to match actual frequency range of the sweep
                freq_start = freqs[0] / 1e6
                freq_end = freqs[-1] / 1e6
                freq_range = freq_end - freq_start
                margin = freq_range * 0.05  # 5% margin on each side
                ax.set_xlim(freq_start - margin, freq_end + margin)
                # Set Y-axis limits with margins to provide visual spacing
                y_min = np.min(magnitude_db)
                y_max = np.max(magnitude_db)
                y_range = y_max - y_min
                y_margin = y_range * 0.05  # 5% margin on each side
                ax.set_ylim(y_min - y_margin, y_max + y_margin)
                ax.autoscale(False)  # Prevent matplotlib from overriding our xlim/ylim settings
                ax.tick_params(axis='x', colors=f"{axis_color}")
                ax.tick_params(axis='y', colors=f"{axis_color}")

                for spine in ax.spines.values():
                    spine.set_color(f"{axis_color}")
                    
                ax.grid(True, which='both', axis='both', color=f"{axis_color}", linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)
                
            elif graph_type == "Phase":
                # Plot phase
                phase_deg = np.angle(s_data) * 180 / np.pi

                ax.plot(freqs / 1e6, phase_deg, color=tracecolor, linewidth=linewidth)

                ax.set_xlabel(r"$\mathrm{Frequency\ [MHz]}$", color=f"{text_color}")
                ax.set_ylabel(r"$\phi_{%s}\ [^\circ]$" % s_param, color=f"{text_color}")
                ax.set_title(r"$%s\ \mathrm{Phase}$" % s_param, color=f"{text_color}")
                
                # Set X-axis limits with margins to match actual frequency range of the sweep
                freq_start = freqs[0] / 1e6
                freq_end = freqs[-1] / 1e6
                freq_range = freq_end - freq_start
                margin = freq_range * 0.05  # 5% margin on each side
                ax.set_xlim(freq_start - margin, freq_end + margin)
                # Set Y-axis limits with margins to provide visual spacing
                y_min = np.min(phase_deg)
                y_max = np.max(phase_deg)
                y_range = y_max - y_min
                y_margin = y_range * 0.05  # 5% margin on each side
                ax.set_ylim(y_min - y_margin, y_max + y_margin)
                ax.autoscale(False)  # Prevent matplotlib from overriding our xlim/ylim settings
                ax.tick_params(axis='x', colors=f"{axis_color}")
                ax.tick_params(axis='y', colors=f"{axis_color}")

                for spine in ax.spines.values():
                    spine.set_color(f"{axis_color}")
                    
                ax.grid(True, which='both', axis='both', color=f"{axis_color}", linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)
                
            elif graph_type == "VSWR":
                # Calculate and plot VSWR
                s_magnitude = np.abs(s_data)
                vswr = (1 + s_magnitude) / (1 - s_magnitude)
                ax.plot(freqs / 1e6, vswr, color=tracecolor, linewidth=linewidth)
                ax.set_xlabel('Frequency (MHz)')
                ax.set_ylabel('VSWR')
                ax.set_title(f'{s_param} VSWR')
                ax.grid(True)
                
            # Set axis properties
            ax.tick_params(axis='both', which='major', labelsize=8)

            cursor_graph.set_zorder(10)
            ax.add_line(cursor_graph)

            cursor_graph_2.set_zorder(10)
            ax.add_line(cursor_graph_2)
            
        except Exception as e:
            logging.error(f"[graphics_window._recreate_single_plot] Error recreating plot: {e}")

    def export_latex_pdf(self):
        """
        Export a PDF using LaTeX with a title page and structured sections.
        
        This method has been refactored to use the LatexExporter module.
        """
        device_name = None
        if self.vna_device:
            device_name = getattr(self.vna_device, 'name', type(self.vna_device).__name__)
        
        return self.latex_exporter.export_to_pdf(
            freqs=self.freqs,
            s11_data=self.s11,
            s21_data=self.s21,
            measurement_name=device_name
        )

    def import_touchstone_data_dut(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import os

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select DUT Touchstone File",
            "",
            "Touchstone Files (*.s2p);;All Files (*)"
        )

        if not file_path:
            QMessageBox.warning(self, "No File Selected", "Please select a Touchstone .s2p file.")
            return

        files = file_path

        QMessageBox.information(self, "File Loaded", "Touchstone file loaded successfully!")
        print("Selected DUT file:", file_path)

        # Use new calibration structure
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "calibration", "config", "calibration_config.ini")
        settings_calibration = QSettings(config_path, QSettings.Format.IniFormat)

        settings_calibration.setValue("Calibration/isImportDut", True)

        if self.vna_device:
            graphics_window = NanoVNAGraphics(vna_device=self.vna_device, dut=files)
        else:
            graphics_window = NanoVNAGraphics()

        graphics_window.show()

        self.close()

    def import_touchstone_data_calibration(self):
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
        dialog.setWindowTitle("Select Method")

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)  

        label = QLabel("Select Method", dialog)
        main_layout.addWidget(label)

        self.select_method = QComboBox()
        self.select_method.setStyleSheet("""
            QComboBox {
                color: black;
                background-color: white;
                border: 1px solid #5f5f5f;
                border-radius: 5px;
                padding-left: 5px;
            }
            QComboBox QAbstractItemView {
                color: black;
                background-color: white;
                selection-background-color: lightgray;
                selection-color: black;
            }
            QComboBox:focus {
                background-color: white;
            }
            QComboBox::placeholder {
                color: lightgray;
            }
        """)

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

    def get_current_timestamp(self):
        """Generate timestamp for filenames"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

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

                # --- Save data ---
                settings_calibration.beginGroup(calibration_entry_name)
                settings_calibration.setValue("kit_name", name)
                settings_calibration.setValue("method", selected_method)
                settings_calibration.setValue("id", next_id)
                settings_calibration.endGroup()

                # --- Update active calibration reference ---
                settings_calibration.beginGroup("Calibration")
                settings_calibration.setValue("Name", full_calibration_name)
                settings_calibration.endGroup()
                settings_calibration.sync()

                settings_calibration.setValue("Calibration/Kits", True)
                settings_calibration.setValue("Calibration/NoCalibration", False)

                if selected_method == "OSM (Open - Short - Match)":
                    parameter = "S11"
                elif selected_method == "Normalization":
                    parameter = "S21"
                else:
                    parameter = "S11, S21"

                settings.setValue("Calibration/Parameter", parameter)
                settings.sync()

                logging.info(f"[welcome_windows.open_save_calibration] Saved calibration {full_calibration_name}")

            except Exception as e:
                logging.error(f"[CalibrationWelcome] Error saving calibration: {e}")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Error saving calibration: {str(e)}")

    def export_touchstone_data(self):
        """
        Export sweep data to Touchstone format.
        
        This method has been refactored to use the TouchstoneExporter module.
        """
        device_name = None
        if self.vna_device:
            device_name = getattr(self.vna_device, 'name', type(self.vna_device).__name__)
        
        return self.touchstone_exporter.export_to_s2p(
            freqs=self.freqs,
            s11_data=self.s11,
            s21_data=self.s21,
            device_name=device_name
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NanoVNAGraphics()
    window.show()
    sys.exit(app.exec())