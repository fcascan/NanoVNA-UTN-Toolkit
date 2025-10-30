"""
Edit graphics window for NanoVNA devices.
"""

import skrf as rf
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTabWidget, QFrame, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, QSettings

try:
    from NanoVNA_UTN_Toolkit.ui.utils.edit_graphics_utils import create_edit_tab1, create_edit_tab2
except ImportError as e:
    import logging, sys
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

from NanoVNA_UTN_Toolkit.ui.graphics_window import NanoVNAGraphics


class EditGraphics(QMainWindow):
    def __init__(self, nano_window: NanoVNAGraphics, freqs=None):
        super().__init__()

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
            QFrame#separatorLine {{
                color: {qframe_color};           
                background: {qframe_color};
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

        carpeta_ini = os.path.join(os.path.dirname(__file__), "ini")

        os.makedirs(carpeta_ini, exist_ok=True)

        ruta_ini = os.path.join(carpeta_ini, "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        self.nano_window = nano_window

        self.setWindowTitle("Edit Graphics")
        self.setFixedSize(800, 530)

        # --- Frequency array placeholder ---
        if freqs is None:
            freqs = np.linspace(1e6, 100e6, 101)
        self.freqs = freqs

        # --- Data placeholders ---
        self.s11 = np.zeros_like(freqs, dtype=complex)  # S11 data
        self.s21 = np.zeros_like(freqs, dtype=complex)  # S21 data

        # --- Central widget setup ---
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(15, 15, 15, 15)
        central_layout.setSpacing(10)

        # --- Tabs setup ---
        tabs = QTabWidget()

        tab1_widget, trace_color, marker_color, brackground_color_graphics, text_color, axis_color, line_width, marker_size = create_edit_tab1(self, tabs=tabs, nano_window=nano_window)
        tab2_widget, trace_color2, marker_color2, brackground_color_graphics2, text_color2, axis_color2, line_width2, marker_size2 = create_edit_tab2(self, tabs=tabs, nano_window=nano_window)

        tabs.addTab(tab1_widget, "Graphic 1")
        tabs.addTab(tab2_widget, "Graphic 2")

        central_layout.addWidget(tabs)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        btn_cancel = QPushButton("Cancel")
        btn_apply = QPushButton("Apply")
        btn_cancel.clicked.connect(self.close)
        btn_apply.clicked.connect(lambda: self.on_apply_clicked(trace_color=trace_color(), trace_color2=trace_color2(), 
                                                                brackground_color_graphics=brackground_color_graphics(), brackground_color_graphics2=brackground_color_graphics2(),
                                                                marker_color=marker_color(), marker_color2=marker_color2(),
                                                                text_color=text_color(), text_color2=text_color2(),
                                                                axis_color=axis_color(), axis_color2=axis_color2(),
                                                                line_width=line_width(), line_width2=line_width2(),
                                                                marker_size=marker_size(), marker_size2=marker_size2(),
                                                                settings=settings))

        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_apply)
        central_layout.addLayout(button_layout)

        # --- Apply styles ---
        self.setCentralWidget(central_widget)
        #self.setStyleSheet("background-color: #7f7f7f;")

    def on_apply_clicked(self, settings, trace_color="blue", trace_color2="blue",
                     brackground_color_graphics="blue", brackground_color_graphics2="blue",
                     marker_color="blue", marker_color2="blue", 
                     text_color="blue", text_color2="blue",
                     axis_color="blue", axis_color2="blue",
                     line_width=2, line_width2=2,
                     marker_size=2, marker_size2=2):
        from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_left_panel, create_right_panel

        settings.setValue("Graphic1/TraceColor", trace_color)
        settings.setValue("Graphic1/MarkerColor", marker_color)
        settings.setValue("Graphic1/BackgroundColor", brackground_color_graphics)
        settings.setValue("Graphic1/TextColor", text_color)
        settings.setValue("Graphic1/AxisColor", axis_color)
        settings.setValue("Graphic1/TraceWidth", line_width)
        settings.setValue("Graphic1/MarkerWidth", marker_size)

        settings.setValue("Graphic2/TraceColor", trace_color2)
        settings.setValue("Graphic2/MarkerColor", marker_color2)
        settings.setValue("Graphic2/BackgroundColor", brackground_color_graphics2)
        settings.setValue("Graphic2/TextColor", text_color2)
        settings.setValue("Graphic2/AxisColor", axis_color2)
        settings.setValue("Graphic2/TraceWidth", line_width2)
        settings.setValue("Graphic2/MarkerWidth", marker_size2)
        settings.sync()

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")
        settings = QSettings(ruta_ini, QSettings.IniFormat)

        graph_type1 = settings.value("Tab1/GraphType1", "Smith Diagram")
        s_param1 = settings.value("Tab1/SParameter", "S11")
        graph_type2 = settings.value("Tab2/GraphType2", "Magnitude")
        s_param2 = settings.value("Tab2/SParameter", "S11")

        self.s11 = self.nano_window.s11
        self.s21 = self.nano_window.s21
        self.freqs = self.nano_window.freqs

        data_left = self.s11 if s_param1 == "S11" else self.s21
        data_right = self.s11 if s_param2 == "S11" else self.s21

        unit_left = self.nano_window.get_graph_unit(1)
        unit_right = self.nano_window.get_graph_unit(2)

        self.nano_window.update_plots_with_new_data(skip_reset=True)

        self.nano_window._recreate_single_plot(
            ax=self.nano_window.ax_left,
            fig=self.nano_window.fig_left,
            s_data=data_left,
            freqs=self.freqs,
            graph_type=graph_type1,
            s_param=s_param1,
            tracecolor=trace_color,
            markercolor=marker_color,
            brackground_color_graphics=brackground_color_graphics,
            text_color=text_color,
            axis_color=axis_color,
            linewidth=line_width,
            markersize=marker_size,
            unit=unit_left,
            cursor_graph=self.nano_window.cursor_left,
            cursor_graph_2=self.nano_window.cursor_left_2
        )

        self.nano_window._recreate_single_plot(
            ax=self.nano_window.ax_right,
            fig=self.nano_window.fig_right,
            s_data=data_right,
            freqs=self.freqs,
            graph_type=graph_type2,
            s_param=s_param2,
            tracecolor=trace_color2,
            markercolor=marker_color2,
            brackground_color_graphics=brackground_color_graphics2,
            text_color=text_color2,
            axis_color=axis_color2,
            linewidth=line_width2,
            markersize=marker_size2,
            unit=unit_right,
            cursor_graph=self.nano_window.cursor_right,
            cursor_graph_2=self.nano_window.cursor_right_2
        )

        self.nano_window.s11 = self.s11
        self.nano_window.s21 = self.s21
        self.nano_window.freqs = self.freqs
        self.nano_window.left_graph_type = graph_type1
        self.nano_window.left_s_param = s_param1
        self.nano_window.right_graph_type = graph_type2
        self.nano_window.right_s_param = s_param2

        self.nano_window.canvas_left.draw_idle()
        self.nano_window.canvas_right.draw_idle()

        self.nano_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    window = EditGraphics()
    window.show()
    app.exec()
