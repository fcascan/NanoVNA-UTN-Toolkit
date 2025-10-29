"""
Graphic view window for NanoVNA devices.
"""

import skrf as rf
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTabWidget, QFrame, QSizePolicy, QApplication,
    QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt, QSettings

try:
    from NanoVNA_UTN_Toolkit.ui.utils.view_utils import create_tab1
    from NanoVNA_UTN_Toolkit.ui.utils.view_utils import create_tab2
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

class View(QMainWindow):
    def __init__(self, nano_window=None, freqs=None):
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
            QFrame {{
                background-color: {qframe_color};
                color: {qframe_color};
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

        self.nano_window = nano_window 

        self.setWindowTitle("Graphic View")
        self.setFixedSize(800, 500)

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

        tab1_widget, self.fig, self.ax, self.canvas, self.left_panel, self.update_graph, self.current_s_tab1, self.current_graph_tab1 = create_tab1(self)

        tab2_widget, self.fig_right, self.ax_right, self.canvas_right, self.right_panel2, self.update_graph_right, self.current_s_tab2, self.current_graph_tab2 = create_tab2(self)

        tabs.addTab(tab1_widget, "Graphic 1")
        tabs.addTab(tab2_widget, "Graphic 2")

        central_layout.addWidget(tabs)

        # --- Line above buttons ---
        line_above_buttons = QFrame()
        line_above_buttons.setFrameShape(QFrame.HLine)
        line_above_buttons.setFrameShadow(QFrame.Plain)
        line_above_buttons.setFixedHeight(2)
        central_layout.addWidget(line_above_buttons)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        btn_cancel = QPushButton("Cancel")
        btn_apply = QPushButton("Apply")
        btn_cancel.clicked.connect(self.close)
        btn_apply.clicked.connect(lambda: self.on_apply_clicked())

        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_apply)
        central_layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)

        # --- Initial plot ---
        self.update_graph()

    def on_apply_clicked(self):
        from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_left_panel, create_right_panel

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        graph_type_tab1 = settings.value("Tab1/GraphType1", "Smith Diagram")
        s_param_tab1    = settings.value("Tab1/SParameter", "S11")
        graph_type_tab2 = settings.value("Tab2/GraphType2", "Magnitude")
        s_param_tab2    = settings.value("Tab2/SParameter", "S11")
        
        trace_color1 = settings.value("Graphic1/TraceColor", "blue")
        marker_color1 = settings.value("Graphic1/MarkerColor", "blue")
        background_color1 = settings.value("Graphic1/BackgroundColor", "blue")
        text_color1 = settings.value("Graphic1/TextColor", "blue")
        axis_color1 = settings.value("Graphic1/AxisColor", "blue")
        trace_size1 = int(settings.value("Graphic1/TraceWidth", 2))
        marker_size1 = int(settings.value("Graphic1/MarkerWidth", 6))
        
        trace_color2 = settings.value("Graphic2/TraceColor", "blue")
        marker_color2 = settings.value("Graphic2/MarkerColor", "blue")
        background_color2 = settings.value("Graphic2/BackgroundColor", "blue")
        text_color2 = settings.value("Graphic2/TextColor", "blue")
        axis_color2 = settings.value("Graphic2/AxisColor", "blue")
        trace_size2 = int(settings.value("Graphic2/TraceWidth", 2))
        marker_size2 = int(settings.value("Graphic2/MarkerWidth", 6))

        self.s11 = self.nano_window.s11
        self.s21 = self.nano_window.s21
        self.freqs = self.nano_window.freqs

        data_left = self.s11 if self.current_s_tab1 == "S11" else self.s21
        data_right = self.s11 if self.current_s_tab2 == "S11" else self.s21

        selected_graph_left = self.current_graph_tab1
        selected_graph_right = self.current_graph_tab2

        settings.setValue("Tab1/SParameter", self.current_s_tab1)
        settings.setValue("Tab1/GraphType1", selected_graph_left)

        settings.setValue("Tab2/SParameter", self.current_s_tab2)
        settings.setValue("Tab2/GraphType2", selected_graph_right)

        settings.sync()

        unit_left = self.nano_window.get_graph_unit(1)

        unit_right = self.nano_window.get_graph_unit(2)

        if self.nano_window is not None:
            # Datos para el gráfico izquierdo y derecho
            data_left = self.s11 if self.current_s_tab1 == "S11" else self.s21
            data_right = self.s11 if self.current_s_tab2 == "S11" else self.s21

            self.nano_window.update_plots_with_new_data(skip_reset=True)

            self.nano_window._recreate_single_plot(
                ax=self.nano_window.ax_left,
                fig=self.nano_window.fig_left,
                s_data=data_left,
                freqs=self.freqs,
                graph_type=self.current_graph_tab1,
                s_param=self.current_s_tab1,
                tracecolor=trace_color1,
                markercolor=marker_color1,
                brackground_color_graphics=background_color1,
                text_color=text_color1,
                axis_color=axis_color1,
                linewidth=trace_size1,
                markersize=marker_size1,
                unit=unit_left,
                cursor_graph=self.nano_window.cursor_left,
                cursor_graph_2=self.nano_window.cursor_left_2
            )

            self.nano_window._recreate_single_plot(
                ax=self.nano_window.ax_right,
                fig=self.nano_window.fig_right,
                s_data=data_right,
                freqs=self.freqs,
                graph_type=self.current_graph_tab2,
                s_param=self.current_s_tab2,
                tracecolor=trace_color2,
                markercolor=marker_color2,
                brackground_color_graphics=background_color2,
                text_color=text_color2,
                axis_color=axis_color2,
                linewidth=trace_size2,
                markersize=marker_size2,
                unit=unit_right,
                cursor_graph=self.nano_window.cursor_right,
                cursor_graph_2=self.nano_window.cursor_right_2
            )

            # Actualizamos datos en nano_window
            self.nano_window.s11 = self.s11
            self.nano_window.s21 = self.s21
            self.nano_window.freqs = self.freqs
            self.nano_window.left_graph_type = self.current_graph_tab1
            self.nano_window.left_s_param = self.current_s_tab1
            self.nano_window.right_graph_type = self.current_graph_tab2
            self.nano_window.right_s_param = self.current_s_tab2

            self.nano_window.show()


        self.close()


if __name__ == "__main__":
    app = QApplication([])
    window = View()
    window.show()
    app.exec()
