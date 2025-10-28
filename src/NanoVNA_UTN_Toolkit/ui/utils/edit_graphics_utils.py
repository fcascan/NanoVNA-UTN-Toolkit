from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox, 
    QColorDialog, QSpinBox, QCheckBox, QPushButton, QSizePolicy, QSpacerItem, QApplication
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QPixmap, QIcon

import qtawesome as qta

# --- Matplotlib ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

plt.rcParams['mathtext.fontset'] = 'cm'   # Fuente Computer Modern
plt.rcParams['text.usetex'] = False       # No requiere LaTeX externo
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['font.family'] = 'serif'     # Coincide con el estilo de LaTeX
plt.rcParams['mathtext.rm'] = 'serif'     # Números y texto coherentes

from matplotlib.ticker import ScalarFormatter

# --- Scikit-RF ---
import skrf as rf
import numpy as np
import os
import logging

spin_style = """
    QSpinBox {
        color: black;
        background-color: white;
        border: 1px solid gray;
        border-radius: 2px;
        padding: 0px 2px;
    }
"""

groupbox_style = """
    QGroupBox {
        color: white;
        font-weight: bold;
    }
"""

####################################################################################################
#--------- Tab 1  ---------------------------------------------------------------------------------#
####################################################################################################

def create_edit_tab1(self, tabs, nano_window):

    ui_dir = os.path.dirname(os.path.dirname(__file__))  
    ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

    settings = QSettings(ruta_ini, QSettings.IniFormat)

    trace_color1 = settings.value("Graphic1/TraceColor", "blue")
    marker_color1 = settings.value("Graphic1/MarkerColor", "blue")
    brackground_color_graphics1 = settings.value("Graphic1/BackgroundColor", "red")
    text_color = settings.value("Graphic1/TextColor", "red")
    axis_color = settings.value("Graphic1/AxisColor", "red")

    trace_size1 = int(settings.value("Graphic1/TraceWidth", 2))
    marker_size1 = int(settings.value("Graphic1/MarkerWidth", 6))

    graph_type1 = settings.value("Tab1/GraphType1", "Smith Diagram")
    s_param1 = settings.value("Tab1/SParameter", "S11")

    index = int(settings.value("Cursor1/index", 0))

####################################################################################################
#--------- Tab1 -----------------------------------------------------------------------------------#
####################################################################################################

    tab1 = QWidget()
    tab1_container = QVBoxLayout(tab1)
    tab1_container.setContentsMargins(0, 0, 0, 0)
    tab1_container.setSpacing(0)

    line_tab = QFrame()
    line_tab.setObjectName("separatorLine")
    line_tab.setFixedHeight(2)
    tab1_container.addWidget(line_tab)

    spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

    tab1_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

####################################################################################################
#--------- Left Data ------------------------------------------------------------------------------#
####################################################################################################

    # Layout principal
    layout_container = QWidget()
    layout = QHBoxLayout(layout_container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignVCenter)
    tab1_container.addWidget(layout_container)

    # LayoutV
    layout_container_V = QWidget()
    layoutV = QVBoxLayout(layout_container_V)
    layoutV.setContentsMargins(0, 0, 0, 0)
    layoutV.setSpacing(20)
    layoutV.setAlignment(Qt.AlignHCenter)
    tab1_container.addWidget(layout_container_V)
    
    # --- Left Trace GroupBox ---
    left_group_trace = QGroupBox(" Edit Trace ")
    left_group_trace.setStyleSheet(groupbox_style)
    left_layout = QVBoxLayout(left_group_trace)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setSpacing(20)
    left_layout.setContentsMargins(10, 10, 10, 5)

    # --- Trace color ---
    trace_layout = QHBoxLayout()
    lbl_trace = QLabel("Trace color:")
    lbl_trace.setStyleSheet("font-size: 11pt;")
    btn_trace = QFrame()
    btn_trace.setFixedSize(26, 26)
    btn_trace.setStyleSheet(f"background-color: {trace_color1}; border: 1px solid white; border-radius: 6px;")
    trace_layout.addWidget(lbl_trace)
    trace_layout.addWidget(btn_trace, alignment=Qt.AlignVCenter)
    left_layout.addLayout(trace_layout)

     # --- Line width ---
    line_layout = QHBoxLayout()
    lbl_line = QLabel("Trace width (all):")
    lbl_line.setStyleSheet("font-size: 11pt;")
    spin_line_tab1 = QSpinBox()
    spin_line_tab1.setRange(1, 10)
    spin_line_tab1.setValue(trace_size1)
    spin_line_tab1.setStyle(QApplication.style())
    spin_line_tab1.setAlignment(Qt.AlignCenter)
    spin_line_tab1.setFrame(True)                
    spin_line_tab1.setFixedWidth(50)
    line_layout.addWidget(lbl_line)
    line_layout.addWidget(spin_line_tab1, alignment=Qt.AlignVCenter)
    left_layout.addLayout(line_layout)

    # --- Left Marker GroupBox ---
    left_group_marker = QGroupBox(" Edit Markers ")
    left_group_marker.setStyleSheet(groupbox_style)
    left_layout = QVBoxLayout(left_group_marker)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setSpacing(20)
    left_layout.setContentsMargins(10, 10, 10, 5)

    # --- Marker color ---
    marker_layout = QHBoxLayout()
    lbl_marker = QLabel("Marker color:")
    lbl_marker.setStyleSheet("font-size: 11pt;")
    btn_marker = QFrame()
    btn_marker.setFixedSize(26, 26)
    btn_marker.setStyleSheet(f"background-color: {marker_color1}; border: 1px solid white; border-radius: 6px;")
    marker_layout.addWidget(lbl_marker)
    marker_layout.addWidget(btn_marker, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_layout)

    # --- Marker size ---
    marker_size_layout = QHBoxLayout()
    lbl_marker_size = QLabel("Marker size (all):")
    lbl_marker_size.setStyleSheet("font-size: 11pt;")
    spin_marker_tab1 = QSpinBox()
    spin_marker_tab1.setRange(1, 20)
    spin_marker_tab1.setValue(marker_size1)
    spin_marker_tab1.setStyle(QApplication.style())
    spin_marker_tab1.setFrame(True)  
    spin_marker_tab1.setAlignment(Qt.AlignCenter)             
    spin_marker_tab1.setFixedWidth(50)
    marker_size_layout.addWidget(lbl_marker_size)
    marker_size_layout.addWidget(spin_marker_tab1, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_size_layout)

    # --- Left Graphic GroupBox ---
    left_group_graphics = QGroupBox(" Edit Graphics ")
    left_group_graphics.setStyleSheet(groupbox_style)
    left_layout = QVBoxLayout(left_group_graphics)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setSpacing(20)
    left_layout.setContentsMargins(10, 10, 10, 15)

    # --- Brackground Color ---
    graphic_brackground_color_layout = QHBoxLayout()
    lbl_graphic_color = QLabel("Background Color:")
    lbl_graphic_color.setStyleSheet("font-size: 11pt;")
    btn_graphic = QFrame()
    btn_graphic.setFixedSize(26, 26)
    btn_graphic.setStyleSheet(f"background-color: {brackground_color_graphics1}; border: 1px solid white; border-radius: 6px;")
    graphic_brackground_color_layout.addWidget(lbl_graphic_color)
    graphic_brackground_color_layout.addWidget(btn_graphic, alignment=Qt.AlignVCenter)
    left_layout.addLayout(graphic_brackground_color_layout)

    # --- Text Color ---
    text_color_layout = QHBoxLayout()
    lbl_text_color = QLabel("Text Color:")
    lbl_text_color.setStyleSheet("font-size: 11pt;")
    btn_text = QFrame()
    btn_text.setFixedSize(26, 26)
    btn_text.setStyleSheet(f"background-color: {text_color}; border: 1px solid white; border-radius: 6px;")
    text_color_layout.addWidget(lbl_text_color)
    text_color_layout.addWidget(btn_text, alignment=Qt.AlignVCenter)
    left_layout.addLayout(text_color_layout)

    # --- Axis Color ---
    axis_color_layout = QHBoxLayout()
    lbl_axis_color = QLabel("Axis Color:")
    lbl_axis_color.setStyleSheet("font-size: 11pt;")
    btn_axis = QFrame()
    btn_axis.setFixedSize(26, 26)
    btn_axis.setStyleSheet(f"background-color: {axis_color}; border: 1px solid white; border-radius: 6px;")
    axis_color_layout.addWidget(lbl_axis_color)
    axis_color_layout.addWidget(btn_axis, alignment=Qt.AlignVCenter)
    left_layout.addLayout(axis_color_layout)

####################################################################################################
#--------- Getters --------------------------------------------------------------------------------#
####################################################################################################

    def get_trace_color():
        return btn_trace.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_marker_color():
        return btn_marker.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_background_color():
        return btn_graphic.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_text_color():
        return btn_text.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_axis_color():
        return btn_axis.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_trace_width():
        return spin_line_tab1.value()

    def get_marker_size():
        return spin_marker_tab1.value()

####################################################################################################
#--------- Smith  ---------------------------------------------------------------------------------#
####################################################################################################

    # --- Matplotlib figure y canvas ---
    fig, ax = plt.subplots(figsize=(4,4))
    fig.subplots_adjust(left=0.25, right=0.9, top=0.82, bottom=0.18)
    canvas = FigureCanvas(fig)
    canvas.setFixedSize(350, 350)

    # --- Datos dummy ---
    freqs = nano_window.freqs
    S_data = nano_window.s11 if s_param1 == "S11" else nano_window.s21

    logging.info(f"[edit_graphics_utils] freqs type: {type(freqs)}, shape: {getattr(freqs, 'shape', 'N/A')}, first 5 values: {freqs[:5] if len(freqs) >= 5 else freqs}")

    cursor_graph, = ax.plot([0], [0], 'o', markersize=marker_size1, color=marker_color1, visible=True)

    def update_graph(graph_type1):
        ax.clear()
        ax.legend().remove()
        
        fig.patch.set_facecolor(f"{get_background_color()}")
        ax.set_facecolor(f"{get_background_color()}")

        if graph_type1 == "Smith Diagram":  
            fig.subplots_adjust(left=0.15, right=0.9, top=0.82, bottom=0.18)

            ntw = rf.Network(frequency=freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
            ntw.plot_s_smith(ax=ax, draw_labels=True, show_legend=False)
            ax.legend([Line2D([0],[0], color=get_trace_color())],[s_param1], loc='upper left', bbox_to_anchor=(-0.17, 1.14))

            for text in ax.texts:
                text.set_color(f"{get_axis_color()}")

            for patch in ax.patches:
                patch.set_edgecolor(f"{get_axis_color()}")   
                patch.set_facecolor("none")    

            ax.hlines(0, -1, 1, color=f"{get_axis_color()}", linewidth=1.1, zorder=10)

            # Aplicar color y ancho al primer line del smith
            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color())
                    line.set_linewidth(get_trace_width())
                    break

            # Cursor como secuencia
            cursor_graph, = ax.plot([np.real(S_data[index])], [np.imag(S_data[index])], 'o',
                                    markersize=get_marker_size(), color=get_marker_color(), visible=True)

        elif graph_type1 == "Magnitude":  
            if np.any(S_data):
                magnitude_db = 20 * np.log10(np.abs(S_data))
                ax.plot(freqs / 1e-6, magnitude_db, color=get_trace_color(), label=s_param1)

            # Magnitude
            ax.set_xlabel(r"$\mathrm{Frequency\ [GHz]}$", color=f"{get_text_color()}")
            ax.set_ylabel(r"$|%s|$" % s_param1, color=f"{get_text_color()}")
            ax.set_title(r"$%s\ \mathrm{Magnitude}$" % s_param1, color=f"{get_text_color()}")

            ax.tick_params(axis='x', colors=f"{get_axis_color()}")
            ax.tick_params(axis='y', colors=f"{get_axis_color()}")

            for side in ['left', 'right', 'top', 'bottom']:
                ax.spines[side].set_visible(True)
                ax.spines[side].set_color(get_axis_color())
                ax.spines[side].set_linewidth(0.7)

            ax.grid(True, which='both', axis='both', color=f"{get_axis_color()}",
                    linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color())
                    line.set_linewidth(get_trace_width())
                    break

            cursor_graph, = ax.plot([freqs[index]/1e-6], [20 * np.log10(np.abs(S_data[index]))], 'o',
                                    markersize=get_marker_size(), color=get_marker_color(), visible=True)

        elif graph_type1 == "Phase":  
            if np.any(S_data):
                ax.plot(freqs / 1e-6, np.angle(S_data) * 180 / np.pi, color=get_trace_color(), label=s_param1)

            # Phase
            ax.set_xlabel(r"$\mathrm{Frequency\ [GHz]}$", color=f"{get_text_color()}")
            ax.set_ylabel(r"$\phi_{%s}\ [^\circ]$" % s_param1, color=f"{get_text_color()}")
            ax.set_title(r"$%s\ \mathrm{Phase}$" % s_param1, color=f"{get_text_color()}")

            ax.tick_params(axis='x', colors=f"{get_axis_color()}")
            ax.tick_params(axis='y', colors=f"{get_axis_color()}")
            ax.yaxis.set_label_coords(-0.24, 0.5)

            for side in ['left', 'right', 'top', 'bottom']:
                ax.spines[side].set_visible(True)
                ax.spines[side].set_color(get_axis_color())
                ax.spines[side].set_linewidth(0.7)

            ax.grid(True, which='both', axis='both', color=f"{get_axis_color()}",
                    linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color())
                    line.set_linewidth(get_trace_width())
                    break

            cursor_graph, = ax.plot([freqs[index]/1e-6], [np.angle(S_data[index])*180/np.pi], 'o',
                                    markersize=get_marker_size(), color=get_marker_color(), visible=True)

        canvas.draw()

    # --- Inicializa el gráfico ---
    update_graph(graph_type1=graph_type1)

    # --- Funciones de actualización ---
    def update_trace_color():
        color = get_trace_color()
        if smith_line:
            smith_line.set_color(color)
            legend_line.set_color(color)
            canvas.draw()

    def update_marker_color():
        color = get_marker_color()
        cursor_graph.set_color(color)
        canvas.draw()

    def update_line_width():
        update_graph(graph_type1=graph_type1)

    def update_marker_size():
        update_graph(graph_type1=graph_type1)

    def pick_trace_color(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_trace.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph(graph_type1=graph_type1)

    def pick_marker_color(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_marker.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph(graph_type1=graph_type1)
            canvas.draw()

    def pick_text_color(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_text.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph(graph_type1=graph_type1)
            canvas.draw()
    
    def pick_axis_color(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_axis.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph(graph_type1=graph_type1)
            canvas.draw()

    def pick_graphic_color(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_graphic.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph(graph_type1=graph_type1)
            canvas.draw()

    btn_trace.mousePressEvent = pick_trace_color
    btn_marker.mousePressEvent = pick_marker_color
    btn_graphic.mousePressEvent = pick_graphic_color
    btn_text.mousePressEvent = pick_text_color
    btn_axis.mousePressEvent = pick_axis_color
    spin_line_tab1.valueChanged.connect(lambda val: update_line_width())
    spin_marker_tab1.valueChanged.connect(lambda val: update_marker_size())

    layout.addWidget(layout_container_V, 1)

    left_group_trace.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    left_group_marker.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    left_group_graphics.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    layoutV.addWidget(left_group_trace, 1)
    layoutV.addWidget(left_group_marker, 1)
    layoutV.addWidget(left_group_graphics, 1)

    layout.addWidget(canvas, 2)

    spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

    tab1_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

    # --- Line above buttons ---
    line_above_buttons = QFrame()
    line_above_buttons.setObjectName("separatorLine")
    line_above_buttons.setFixedHeight(2)
    tab1_container.addWidget(line_above_buttons)

    return tab1, get_trace_color, get_marker_color, get_background_color, get_text_color, get_axis_color, get_trace_width, get_marker_size

####################################################################################################
#--------- Tab2 -----------------------------------------------------------------------------------#
####################################################################################################

def create_edit_tab2(self, tabs, nano_window):

    ui_dir = os.path.dirname(os.path.dirname(__file__))  
    ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

    settings = QSettings(ruta_ini, QSettings.IniFormat)

    trace_color2 = settings.value("Graphic2/TraceColor", "red")
    marker_color2 = settings.value("Graphic2/MarkerColor", "red")
    brackground_color_graphics2 = settings.value("Graphic2/BackgroundColor", "red")
    text_color2 = settings.value("Graphic2/TextColor", "red")
    axis_color2 = settings.value("Graphic2/AxisColor", "red")

    line_width2 = int(settings.value("Graphic2/TraceWidth", 2))
    marker_size2 = int(settings.value("Graphic2/MarkerWidth", 6))

    graph_type2 = settings.value("Tab2/GraphType2", "Smith Diagram")
    s_param2 = settings.value("Tab2/SParameter", "S11")

    index = int(settings.value("Cursor2/index", 0))

####################################################################################################
#--------- Tab2 -----------------------------------------------------------------------------------#
####################################################################################################

    tab2 = QWidget()
    tab2_container = QVBoxLayout(tab2)
    tab2_container.setContentsMargins(0, 0, 0, 0)
    tab2_container.setSpacing(0)

    # Línea arriba
    line_tab = QFrame()
    line_tab.setFixedHeight(2)
    line_tab.setObjectName("separatorLine")
    tab2_container.addWidget(line_tab)

    tab2_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

####################################################################################################
#--------- Left Data ------------------------------------------------------------------------------#
####################################################################################################

    # Layout principal
    layout_container = QWidget()
    layout = QHBoxLayout(layout_container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignVCenter)
    tab2_container.addWidget(layout_container)

    # LayoutV
    layout_container_V = QWidget()
    layoutV = QVBoxLayout(layout_container_V)
    layoutV.setContentsMargins(0, 0, 0, 0)
    layoutV.setSpacing(20)
    layoutV.setAlignment(Qt.AlignHCenter)
    tab2_container.addWidget(layout_container_V)
    
    # --- Left Trace GroupBox ---
    left_group_trace = QGroupBox(" Edit Trace ")
    left_group_trace.setStyleSheet(groupbox_style)
    left_layout = QVBoxLayout(left_group_trace)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setSpacing(20)
    left_layout.setContentsMargins(10, 10, 10, 5)

    # Trace color
    trace_layout = QHBoxLayout()
    lbl_trace = QLabel("Trace color:")
    lbl_trace.setStyleSheet("font-size: 11pt;")
    btn_trace = QFrame()
    btn_trace.setFixedSize(26, 26)
    btn_trace.setStyleSheet(f"background-color: {trace_color2}; border: 1px solid white; border-radius: 6px;")
    trace_layout.addWidget(lbl_trace)
    trace_layout.addWidget(btn_trace, alignment=Qt.AlignVCenter)
    left_layout.addLayout(trace_layout)

    # Trace width
    trace_layout = QHBoxLayout()
    lbl_line = QLabel("Trace width (all):")
    lbl_line.setStyleSheet("font-size: 11pt;")
    spin_line_tab2 = QSpinBox()
    spin_line_tab2.setRange(1, 10)
    spin_line_tab2.setValue(line_width2)
    spin_line_tab2.setStyle(QApplication.style())
    spin_line_tab2.setAlignment(Qt.AlignCenter)
    spin_line_tab2.setFrame(True)      
    spin_line_tab2.setFixedWidth(50)
    trace_layout.addWidget(lbl_line)
    trace_layout.addWidget(spin_line_tab2, alignment=Qt.AlignVCenter)
    left_layout.addLayout(trace_layout)

    # --- Left Marker GroupBox ---
    left_group_marker = QGroupBox(" Edit Markers ")
    left_group_marker.setStyleSheet(groupbox_style)
    left_layout = QVBoxLayout(left_group_marker)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setSpacing(20)
    left_layout.setContentsMargins(10, 10, 10, 5)

    # Marker color
    marker_layout = QHBoxLayout()
    lbl_marker = QLabel("Marker color:")
    lbl_marker.setStyleSheet("font-size: 11pt;")
    btn_marker = QFrame()
    btn_marker.setFixedSize(26, 26)
    btn_marker.setStyleSheet(f"background-color: {marker_color2}; border: 1px solid white; border-radius: 6px;")
    marker_layout.addWidget(lbl_marker)
    marker_layout.addWidget(btn_marker, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_layout)

    # Marker size
    marker_size_layout = QHBoxLayout()
    lbl_marker_size = QLabel("Marker size (all):")
    lbl_marker_size.setStyleSheet("font-size: 11pt;")
    spin_marker_tab2 = QSpinBox()
    spin_marker_tab2.setRange(1, 20)
    spin_marker_tab2.setValue(marker_size2)
    spin_marker_tab2.setStyle(QApplication.style())
    spin_marker_tab2.setAlignment(Qt.AlignCenter)
    spin_marker_tab2.setFrame(True)  
    spin_marker_tab2.setFixedWidth(50)
    marker_size_layout.addWidget(lbl_marker_size)
    marker_size_layout.addWidget(spin_marker_tab2, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_size_layout)

    # --- Left Graphic GroupBox ---
    left_group_graphics = QGroupBox(" Edit Graphics ")
    left_group_graphics.setStyleSheet(groupbox_style)
    left_layout = QVBoxLayout(left_group_graphics)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setSpacing(20)
    left_layout.setContentsMargins(10, 10, 10, 15)

    # --- Background Color ---
    graphic_brackground_color_layout = QHBoxLayout()
    lbl_graphic_color = QLabel("Background Color:")
    lbl_graphic_color.setStyleSheet("font-size: 11pt;")
    btn_graphic = QFrame()
    btn_graphic.setFixedSize(26, 26)
    btn_graphic.setStyleSheet(f"background-color: {brackground_color_graphics2}; border: 1px solid white; border-radius: 6px;")
    graphic_brackground_color_layout.addWidget(lbl_graphic_color)
    graphic_brackground_color_layout.addWidget(btn_graphic, alignment=Qt.AlignVCenter)
    left_layout.addLayout(graphic_brackground_color_layout)

    # --- Text Color ---
    text_color_layout = QHBoxLayout()
    lbl_text_color = QLabel("Text Color:")
    lbl_text_color.setStyleSheet("font-size: 11pt;")
    btn_text = QFrame()
    btn_text.setFixedSize(26, 26)
    btn_text.setStyleSheet(f"background-color: {text_color2}; border: 1px solid white; border-radius: 6px;")
    text_color_layout.addWidget(lbl_text_color)
    text_color_layout.addWidget(btn_text, alignment=Qt.AlignVCenter)
    left_layout.addLayout(text_color_layout)

    # --- Axis Color ---
    axis_color_layout = QHBoxLayout()
    lbl_axis_color = QLabel("Axis Color:")
    lbl_axis_color.setStyleSheet("font-size: 11pt;")
    btn_axis = QFrame()
    btn_axis.setFixedSize(26, 26)
    btn_axis.setStyleSheet(f"background-color: {axis_color2}; border: 1px solid white; border-radius: 6px;")
    axis_color_layout.addWidget(lbl_axis_color)
    axis_color_layout.addWidget(btn_axis, alignment=Qt.AlignVCenter)
    left_layout.addLayout(axis_color_layout)

####################################################################################################
#--------- Getters --------------------------------------------------------------------------------#
####################################################################################################

    def get_trace_color2():
        return btn_trace.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_marker_color2():
        return btn_marker.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_background_color2():
        return btn_graphic.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_text_color2():
        return btn_text.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_axis_color2():
        return btn_axis.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_trace_width2():
        return spin_line_tab2.value()

    def get_marker_size2():
        return spin_marker_tab2.value()

####################################################################################################
#--------- Matplotlib Graph ----------------------------------------------------------------------#
####################################################################################################

    fig, ax = plt.subplots(figsize=(4,4))
    fig.subplots_adjust(left=0.25, right=0.9, top=0.82, bottom=0.18)
    canvas = FigureCanvas(fig)
    canvas.setFixedSize(350, 350)

    # Datos dummy
    N = 101
    freqs = nano_window.freqs
    S_data = nano_window.s11 if s_param2 == "S11" else nano_window.s21

    def update_graph2(graph_type2):
        ax.clear()
        ax.legend().remove()

        fig.patch.set_facecolor(f"{get_background_color2()}")
        ax.set_facecolor(f"{get_background_color2()}")

        if graph_type2 == "Smith Diagram":  
            fig.subplots_adjust(left=0.15, right=0.9, top=0.82, bottom=0.18)
            ntw = rf.Network(frequency=freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
            ntw.plot_s_smith(ax=ax, draw_labels=True, show_legend=False)
            ax.legend([Line2D([0],[0], color=get_trace_color2())],[s_param2], loc='upper left', bbox_to_anchor=(-0.17, 1.14))

            for text in ax.texts:
                text.set_color(f"{get_axis_color2()}")
            for patch in ax.patches:
                patch.set_edgecolor(f"{get_axis_color2()}")   
                patch.set_facecolor("none")    
            ax.hlines(0, -1, 1, color=f"{get_axis_color2()}", linewidth=1.1, zorder=10)

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color2())
                    line.set_linewidth(get_trace_width2())
                    break

            # Cursor como secuencia
            cursor_graph2, = ax.plot([np.real(S_data[index])], [np.imag(S_data[index])], 'o',
                                    markersize=get_marker_size2(), color=get_marker_color2(), visible=True)

        elif graph_type2 == "Magnitude":  
            if np.any(S_data):
                magnitude_db = 20 * np.log10(np.abs(S_data))
                ax.plot(freqs/1e-6, magnitude_db, color=get_trace_color2(), label=s_param2)

            # Magnitude
            ax.set_xlabel(r"$\mathrm{Frequency\ [GHz]}$", color=f"{get_text_color2()}")
            ax.set_ylabel(r"$|%s|$" % s_param2, color=f"{get_text_color2()}")
            ax.set_title(r"$%s\ \mathrm{Magnitude}$" % s_param2, color=f"{get_text_color2()}")

            ax.tick_params(axis='x', colors=f"{get_axis_color2()}")
            ax.tick_params(axis='y', colors=f"{get_axis_color2()}")

            for side in ['left', 'right', 'top', 'bottom']:
                ax.spines[side].set_visible(True)           
                ax.spines[side].set_color(get_axis_color2())  
                ax.spines[side].set_linewidth(0.7)    
            ax.grid(True, which='both', axis='both', color=f"{get_axis_color2()}", linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color2())
                    line.set_linewidth(get_trace_width2())
                    break

            # Cursor como secuencia
            cursor_graph2, = ax.plot([freqs[index]/1e-6], [20 * np.log10(np.abs(S_data[index]))], 'o',
                                    markersize=get_marker_size2(), color=get_marker_color2(), visible=True)

        elif graph_type2 == "Phase":  
            if np.any(S_data):
                ax.plot(freqs/1e-6, np.angle(S_data) * 180 / np.pi, color=get_trace_color2(), label=s_param2)

            # Phase
            ax.set_xlabel(r"$\mathrm{Frequency\ [GHz]}$", color=f"{get_text_color2()}")
            ax.set_ylabel(r"$\phi_{%s}\ [^\circ]$" % s_param2, color=f"{get_text_color2()}")
            ax.set_title(r"$%s\ \mathrm{Phase}$" % s_param2, color=f"{get_text_color2()}")

            ax.tick_params(axis='x', colors=f"{get_axis_color2()}")
            ax.tick_params(axis='y', colors=f"{get_axis_color2()}")
            ax.yaxis.set_label_coords(-0.24, 0.5)

            for side in ['left', 'right', 'top', 'bottom']:
                ax.spines[side].set_visible(True)           
                ax.spines[side].set_color(get_axis_color2())  
                ax.spines[side].set_linewidth(0.7)    
            ax.grid(True, which='both', axis='both', color=f"{get_axis_color2()}", linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color2())
                    line.set_linewidth(get_trace_width2())
                    break

            # Cursor como secuencia
            cursor_graph2, = ax.plot([freqs[index]/1e-6], [np.angle(S_data[index]) * 180 / np.pi], 'o',
                                    markersize=get_marker_size2(), color=get_marker_color2(), visible=True)

        canvas.draw()

    update_graph2(graph_type2=graph_type2)

####################################################################################################
#--------- Events & Color Pickers ----------------------------------------------------------------#
####################################################################################################

    def update_trace_color2_event():
        color = get_trace_color2()
        for line in ax.lines:
            line.set_color(color)
        canvas.draw()

    def update_marker_color2_event():
        color = get_marker_color2()
        cursor_graph2.set_color(color)
        canvas.draw()

    def update_brackground_color_graphics2_event():
        color = get_background_color2()
        cursor_graph2.set_color(color)
        canvas.draw()

    def update_line_width2_event():
        update_graph2(graph_type2=graph_type2)

    def update_marker_size2_event():
        update_graph2(graph_type2=graph_type2)

    def pick_trace_color2(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_trace.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph2(graph_type2=graph_type2)

    def pick_marker_color2(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_marker.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph2(graph_type2=graph_type2)
            canvas.draw()

    def pick_graphic_color2(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_graphic.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph2(graph_type2=graph_type2)
            canvas.draw()

    def pick_text_color2(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_text.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph2(graph_type2=graph_type2)
            canvas.draw()

    def pick_axis_color2(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_axis.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph2(graph_type2=graph_type2)
            canvas.draw()

    btn_trace.mousePressEvent = pick_trace_color2
    btn_marker.mousePressEvent = pick_marker_color2
    btn_graphic.mousePressEvent = pick_graphic_color2
    btn_text.mousePressEvent = pick_text_color2
    btn_axis.mousePressEvent = pick_axis_color2
    spin_line_tab2.valueChanged.connect(lambda val: update_line_width2_event())
    spin_marker_tab2.valueChanged.connect(lambda val: update_marker_size2_event())

####################################################################################################
#--------- Final Layout --------------------------------------------------------------------------#
####################################################################################################

    layout.addWidget(layout_container_V, 1)

    left_group_trace.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    left_group_marker.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    left_group_graphics.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    layoutV.addWidget(left_group_trace, 1)
    layoutV.addWidget(left_group_marker, 1)
    layoutV.addWidget(left_group_graphics, 1)

    layout.addWidget(canvas, 2)

    tab2_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

    # Line above the buttons
    line_above_buttons = QFrame()
    line_above_buttons.setObjectName("separatorLine")
    line_above_buttons.setFixedHeight(2)
    tab2_container.addWidget(line_above_buttons)

    return tab2, get_trace_color2, get_marker_color2, get_background_color2, get_text_color2, get_axis_color2, get_trace_width2, get_marker_size2
