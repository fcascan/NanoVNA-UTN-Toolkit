import numpy as np
import skrf as rf
import os
import logging
import matplotlib
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QSizePolicy, QLineEdit, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.patches import Circle
from matplotlib.widgets import Slider
from PySide6.QtCore import Qt
from matplotlib.lines import Line2D

import matplotlib.pyplot as plt

plt.rcParams['mathtext.fontset'] = 'cm'   # Fuente Computer Modern
plt.rcParams['text.usetex'] = False       # No requiere LaTeX externo
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['font.family'] = 'serif'     # Coincide con el estilo de LaTeX
plt.rcParams['mathtext.rm'] = 'serif'     # Números y texto coherentes
 
from PySide6.QtCore import QObject, QEvent, QSettings

from PySide6.QtGui import QDoubleValidator

def format_frequency_smart(freq_hz):
    """Format frequency in the most appropriate unit (Hz, kHz, MHz, GHz)."""
    if freq_hz >= 1e9:
        return f"{freq_hz/1e9:.3f} GHz"
    elif freq_hz >= 1e6:
        return f"{freq_hz/1e6:.3f} MHz"
    elif freq_hz >= 1e3:
        return f"{freq_hz/1e3:.3f} kHz"
    else:
        return f"{freq_hz:.1f} Hz"

def format_frequency_smart_split(freq_hz):
    """Format frequency and return (value, unit) tuple."""
    if freq_hz >= 1e9:
        return f"{freq_hz/1e9:.3f}", "GHz"
    elif freq_hz >= 1e6:
        return f"{freq_hz/1e6:.3f}", "MHz"
    elif freq_hz >= 1e3:
        return f"{freq_hz/1e3:.3f}", "kHz"
    else:
        return f"{freq_hz:.1f}", "Hz"

def parse_frequency_input(text):
    """Parse frequency input with units and return value in Hz."""
    text = text.strip().replace(",", ".")
    
    # Extract numeric part and unit
    import re
    match = re.match(r'(\d+\.?\d*)\s*([a-zA-Z]*)', text)
    if not match:
        return None
        
    value = float(match.group(1))
    unit = match.group(2).lower()
    
    # Convert to Hz based on unit
    if unit.startswith('g'):  # GHz
        return value * 1e9
    elif unit.startswith('m'):  # MHz
        return value * 1e6
    elif unit.startswith('k'):  # kHz
        return value * 1e3
    else:  # Hz or no unit (assume MHz for backward compatibility)
        if unit == '' or unit.startswith('h'):
            return value * 1e6 if unit == '' else value
        return value

#############################################################################################
# =================== LEFT PANEL ========================================================= #
#############################################################################################

def create_left_panel(window, S_data, freqs, settings, graph_type="Smith Diagram", s_param="S11",
                      tracecolor="red", markercolor="red", marker2color="red", linewidth=2,
                      markersize=5, marker2size=5, marker_visible=True, marker_visible_2=False):

    brackground_color_graphics = settings.value("Graphic1/BackgroundColor", "red")
    text_color = settings.value("Graphic1/TextColor", "red")
    axis_color = settings.value("Graphic1/AxisColor", "red")
                      
    freqs = freqs if freqs is not None else np.linspace(1e6, 100e6, 101)

    if S_data is None:
        phase = -2*np.pi*freqs/1e8
        S_data = 0.5 * np.exp(1j*phase)
    
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setContentsMargins(10,10,10,10)
    left_layout.setSpacing(10)

    # --- Figura ---
    if graph_type == "Smith Diagram":
        # Use consolidated Smith chart functionality
        from ...utils.smith_chart_utils import SmithChartConfig, SmithChartManager
        
        # Create custom config to match original settings
        config = SmithChartConfig()
        config.background_color = brackground_color_graphics
        config.axis_color = axis_color
        config.text_color = axis_color
        config.trace_color = tracecolor
        config.marker_color = markercolor
        config.linewidth = linewidth
        config.markersize = markersize
        config.marker_visible = marker_visible
        config.marker_visible_2 = marker_visible_2
        
        # Create Smith chart with custom configuration
        manager = SmithChartManager(config)
        fig, ax, canvas, cursor_graph, cursor_graph_2 = manager.create_graphics_panel_smith_chart(
            s_data=S_data,
            freqs=freqs,
            s_param=s_param,
            figsize=(10, 10),
            container_layout=left_layout,
            trace_color=tracecolor,
            marker_color=markercolor,
            marker2_color=marker2color
        )

    elif graph_type == "Magnitude":

        fig, ax = plt.subplots(figsize=(4,3))
        fig.subplots_adjust(left=0.22, right=0.8, top=0.8, bottom=0.22)

        fig.patch.set_facecolor(f"{brackground_color_graphics}")
        ax.set_facecolor(f"{brackground_color_graphics}")

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(canvas)

        ax.plot(freqs*1e-6, np.abs(S_data), color=tracecolor, marker='.', linestyle='-', linewidth=linewidth, zorder=2)

        ax.set_xlabel(r"$\mathrm{Frequency\ [MHz]}$", color=text_color)
        ax.set_ylabel(r"$|%s|$" % s_param, color=text_color)
        ax.set_title(r"$%s\ \mathrm{Magnitude}$" % s_param, color=text_color)

        # Set X-axis limits with margins to match actual frequency range of the sweep
        freq_start = freqs[0]*1e-6
        freq_end = freqs[-1]*1e-6
        freq_range = freq_end - freq_start
        margin = freq_range * 0.05  # 5% margin on each side
        ax.set_xlim(freq_start - margin, freq_end + margin)
        # Set Y-axis limits with margins to provide visual spacing
        magnitude_data = np.abs(S_data)
        y_min = np.min(magnitude_data)
        y_max = np.max(magnitude_data)
        y_range = y_max - y_min
        y_margin = y_range * 0.05  # 5% margin on each side
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        ax.autoscale(False)  # Prevent matplotlib from overriding our xlim/ylim settings
        ax.tick_params(axis='x', colors=f"{axis_color}")
        ax.tick_params(axis='y', colors=f"{axis_color}")

        for spine in ax.spines.values():
            spine.set_color("white")
            
        ax.grid(True, which='both', axis='both', color='white', linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)

        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)
        cursor_graph_2, = ax.plot([], [], 'o', markersize=marker2size, color=marker2color, visible=False)

    elif graph_type == "Phase":

        fig, ax = plt.subplots(figsize=(4,3))
        fig.subplots_adjust(left=0.22, right=0.8, top=0.8, bottom=0.22)

        fig.patch.set_facecolor(f"{brackground_color_graphics}")
        ax.set_facecolor(f"{brackground_color_graphics}")

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(canvas)

        ax.plot(freqs*1e-6, np.angle(S_data, deg=True), color=tracecolor, marker='.', linestyle='-', linewidth=linewidth)

        ax.set_xlabel(r"$\mathrm{Frequency\ [MHz]}$", color=text_color)
        ax.set_ylabel(r"$\phi_{%s}\ [^\circ]$" % s_param, color=f"{text_color}")
        ax.set_title(r"$%s\ \mathrm{Phase}$" % s_param, color=text_color)

        # Set X-axis limits with margins to match actual frequency range of the sweep
        freq_start = freqs[0]*1e-6
        freq_end = freqs[-1]*1e-6
        freq_range = freq_end - freq_start
        margin = freq_range * 0.05  # 5% margin on each side
        ax.set_xlim(freq_start - margin, freq_end + margin)
        # Set Y-axis limits with margins to provide visual spacing
        phase_data = np.angle(S_data, deg=True)
        y_min = np.min(phase_data)
        y_max = np.max(phase_data)
        y_range = y_max - y_min
        y_margin = y_range * 0.05  # 5% margin on each side
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        ax.autoscale(False)  # Prevent matplotlib from overriding our xlim/ylim settings
        ax.tick_params(axis='x', colors=f"{axis_color}")
        ax.tick_params(axis='y', colors=f"{axis_color}")

        for spine in ax.spines.values():
            spine.set_color("white")
            
        ax.grid(True, which='both', axis='both', color='white', linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)

        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)
        cursor_graph_2, = ax.plot([], [], 'o', markersize=marker2size, color=marker2color, visible=False)

    else:
        raise ValueError(f"Unknown graph_type: {graph_type}")

    # --- Info panel (left side reorganized) ---
    info_panel = QWidget()
    info_layout = QVBoxLayout(info_panel)
    info_layout.setSpacing(10)
    info_layout.setContentsMargins(0, 0, 0, 0)

    # --- Top QGroupBox with title ---
    box_top = QGroupBox("S-Parameter Details")
    layout_top = QHBoxLayout(box_top)
    layout_top.setSpacing(20)
    layout_top.setContentsMargins(12, 8, 12, 8)  # márgenes equilibrados

    # --- Sub-layout centrado para los 4 bloques ---
    center_layout = QHBoxLayout()
    center_layout.setSpacing(15)  # espacio entre columnas
    center_layout.setAlignment(Qt.AlignCenter)  # todo centrado en el box

    # --- Column 1: Frequency ---
    col_left = QVBoxLayout()
    col_left.setSpacing(5)
    col_left.setAlignment(Qt.AlignVCenter)

    hbox_freq = QHBoxLayout()
    hbox_freq.setAlignment(Qt.AlignLeft)
    hbox_freq.setContentsMargins(0, 0, 0, 0)

    lbl_text = QLabel("Frequency:")
    lbl_text.setStyleSheet("font-size:14px;")
    lbl_text.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    hbox_freq.addWidget(lbl_text)

    initial_freq_value, initial_freq_unit = format_frequency_smart_split(freqs[0])
    edit_value = QLineEdit(initial_freq_value)

    def limit_frequency_input(text, max_digits=6, max_decimals=3, allow_dashes=False):
        if text == "--":   # allow placeholder
            return text
        filtered = "".join(c for c in text if c.isdigit() or c == ".")
        if filtered.count(".") > 1:
            parts = filtered.split(".", 1)
            filtered = parts[0] + "." + "".join(parts[1:]).replace(".", "")
        if "." in filtered:
            integer_part, decimal_part = filtered.split(".", 1)
            integer_part = integer_part[:max_digits]
            decimal_part = decimal_part[:max_decimals]
            filtered = integer_part + "." + decimal_part
        else:
            filtered = filtered[:max_digits]
        return filtered

    def on_text_changed():
        new_text = limit_frequency_input(edit_value.text(), 3, 3)
        if new_text != edit_value.text():
            edit_value.setText(new_text)
        text_width = edit_value.fontMetrics().horizontalAdvance(edit_value.text())
        min_width = max(text_width + 10, 40)
        edit_value.setFixedWidth(min_width)

    edit_value.textChanged.connect(on_text_changed)
    edit_value.setStyleSheet("font-size:14px; border:none; background:transparent;")
    edit_value.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    text_width = edit_value.fontMetrics().horizontalAdvance(edit_value.text())
    min_width = max(text_width + 10, 40)
    edit_value.setFixedWidth(min_width)
    hbox_freq.addWidget(edit_value)

    lbl_unit = QLabel(initial_freq_unit)
    lbl_unit.setStyleSheet("font-size:14px;")
    lbl_unit.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    lbl_unit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    hbox_freq.addWidget(lbl_unit)

    col_left.addLayout(hbox_freq)

    # --- Column 2: S11 real + imag ---
    label_val = QLabel(f"{s_param}: -- + j--")
    label_val.setStyleSheet("font-size:14px; padding:1px;")
    label_val.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_s11 = QVBoxLayout()
    col_s11.setSpacing(5)
    col_s11.setAlignment(Qt.AlignVCenter)
    col_s11.addWidget(label_val)

    # --- Column 3: |S11| ---
    label_mag = QLabel(f"|{s_param}|: --")
    label_mag.setStyleSheet("font-size:14px; padding:1px;")
    label_mag.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_mag = QVBoxLayout()
    col_mag.setSpacing(5)
    col_mag.setAlignment(Qt.AlignVCenter)
    col_mag.addWidget(label_mag)

    # --- Column 4: Phase ---
    label_phase = QLabel("Phase: --")
    label_phase.setStyleSheet("font-size:14px; padding:1px;")
    label_phase.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_phase = QVBoxLayout()
    col_phase.setSpacing(5)
    col_phase.setAlignment(Qt.AlignVCenter)
    col_phase.addWidget(label_phase)

    # --- Agregar columnas al layout centrado con separadores ---
    center_layout.addLayout(col_left)
    
    label_sep = QLabel("-")
    center_layout.addWidget(label_sep)

    center_layout.addLayout(col_s11)

    label_sep = QLabel("-")
    center_layout.addWidget(label_sep)

    center_layout.addLayout(col_mag)

    label_sep = QLabel("-")
    center_layout.addWidget(label_sep)

    center_layout.addLayout(col_phase)

    # --- Agregar layout centrado al top box ---
    layout_top.addLayout(center_layout)

    # --- Bottom QGroupBox ---
    box_bottom = QGroupBox("DUT Parameters")
    layout_bottom = QHBoxLayout(box_bottom)
    layout_bottom.setSpacing(40)  # aumenta separación entre labels
    layout_bottom.setContentsMargins(10, 8, 10, 8)
    layout_bottom.setAlignment(Qt.AlignCenter)  # centra todo el conjunto

    # --- Labels dentro del box_bottom ---
    label_z = QLabel("Zin (Z0): -- + j--")
    label_z.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_z.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom.addWidget(label_z)

    label_sep = QLabel("-")
    layout_bottom.addWidget(label_sep)

    label_il = QLabel("IL: -- dB")
    label_il.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_il.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom.addWidget(label_il)

    label_sep = QLabel("-")
    layout_bottom.addWidget(label_sep)

    label_vswr = QLabel("VSWR: --")
    label_vswr.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_vswr.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom.addWidget(label_vswr)

    # --- Agregar box_bottom al layout principal ---
    info_layout.addWidget(box_top)
    info_layout.addWidget(box_bottom)  

    # Add to external layout
    left_layout.addWidget(info_panel)

    # --- Labels dictionary ---
    labels_dict = {
        "val": label_val,
        "mag": label_mag,
        "phase": label_phase,
        "z": label_z,
        "il": label_il,
        "vswr": label_vswr,
        "freq": edit_value,
        "unit": lbl_unit
    }

    # --- Info panel (left side reorganized) duplicate for marker 2 ---
    info_panel_2 = QWidget()
    info_layout_2 = QVBoxLayout(info_panel_2)
    info_layout_2.setSpacing(10)
    info_layout_2.setContentsMargins(0, 0, 0, 0)

    # --- Top QGroupBox with title ---
    box_top_2 = QGroupBox("S-Parameter Details 2")
    layout_top_2 = QHBoxLayout(box_top_2)
    layout_top_2.setSpacing(20)
    layout_top_2.setContentsMargins(12, 8, 12, 8)

    center_layout_2 = QHBoxLayout()
    center_layout_2.setSpacing(15)
    center_layout_2.setAlignment(Qt.AlignCenter)

    # --- Column 1: Frequency ---
    col_left_2 = QVBoxLayout()
    col_left_2.setSpacing(5)
    col_left_2.setAlignment(Qt.AlignVCenter)

    hbox_freq_2 = QHBoxLayout()
    hbox_freq_2.setAlignment(Qt.AlignLeft)
    hbox_freq_2.setContentsMargins(0, 0, 0, 0)

    lbl_text_2 = QLabel("Frequency:")
    lbl_text_2.setStyleSheet("font-size:14px;")
    lbl_text_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    hbox_freq_2.addWidget(lbl_text_2)

    initial_freq_value_2, initial_freq_unit_2 = format_frequency_smart_split(freqs[0])
    edit_value_2 = QLineEdit(initial_freq_value_2)

    def on_text_changed_2():
        new_text = limit_frequency_input(edit_value_2.text(), 3, 3)
        if new_text != edit_value_2.text():
            edit_value_2.setText(new_text)
        text_width = edit_value_2.fontMetrics().horizontalAdvance(edit_value_2.text())
        min_width = max(text_width + 10, 40)
        edit_value_2.setFixedWidth(min_width)

    edit_value_2.textChanged.connect(on_text_changed_2)
    edit_value_2.setStyleSheet("font-size:14px; border:none; background:transparent;")
    edit_value_2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    text_width = edit_value_2.fontMetrics().horizontalAdvance(edit_value_2.text())
    min_width = max(text_width + 10, 40)
    edit_value_2.setFixedWidth(min_width)
    hbox_freq_2.addWidget(edit_value_2)

    lbl_unit_2 = QLabel(initial_freq_unit_2)
    lbl_unit_2.setStyleSheet("font-size:14px;")
    lbl_unit_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    lbl_unit_2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    hbox_freq_2.addWidget(lbl_unit_2)

    col_left_2.addLayout(hbox_freq_2)

    # --- Column 2: S11 real + imag ---
    label_val_2 = QLabel(f"{s_param}: -- + j--")
    label_val_2.setStyleSheet("font-size:14px; padding:1px;")
    label_val_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_s11_2 = QVBoxLayout()
    col_s11_2.setSpacing(5)
    col_s11_2.setAlignment(Qt.AlignVCenter)
    col_s11_2.addWidget(label_val_2)

    # --- Column 3: |S11| ---
    label_mag_2 = QLabel(f"|{s_param}|: --")
    label_mag_2.setStyleSheet("font-size:14px; padding:1px;")
    label_mag_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_mag_2 = QVBoxLayout()
    col_mag_2.setSpacing(5)
    col_mag_2.setAlignment(Qt.AlignVCenter)
    col_mag_2.addWidget(label_mag_2)

    # --- Column 4: Phase ---
    label_phase_2 = QLabel("Phase: --")
    label_phase_2.setStyleSheet("font-size:14px; padding:1px;")
    label_phase_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_phase_2 = QVBoxLayout()
    col_phase_2.setSpacing(5)
    col_phase_2.setAlignment(Qt.AlignVCenter)
    col_phase_2.addWidget(label_phase_2)

    # --- Agregar columnas al layout centrado ---
    center_layout_2.addLayout(col_left_2)

    label_sep_2 = QLabel("-")
    center_layout_2.addWidget(label_sep_2)

    center_layout_2.addLayout(col_s11_2)

    label_sep_2 = QLabel("-")
    center_layout_2.addWidget(label_sep_2)

    center_layout_2.addLayout(col_mag_2)

    label_sep_2 = QLabel("-")
    center_layout_2.addWidget(label_sep_2)

    center_layout_2.addLayout(col_phase_2)

    layout_top_2.addLayout(center_layout_2)

    # --- Bottom QGroupBox ---
    box_bottom_2 = QGroupBox("DUT Parameters 2")
    layout_bottom_2 = QHBoxLayout(box_bottom_2)
    layout_bottom_2.setSpacing(40)
    layout_bottom_2.setContentsMargins(10, 8, 10, 8)
    layout_bottom_2.setAlignment(Qt.AlignCenter)

    label_z_2 = QLabel("Zin (Z0): -- + j--")
    label_z_2.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_z_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom_2.addWidget(label_z_2)

    label_sep_2 = QLabel("-")
    layout_bottom_2.addWidget(label_sep_2)

    label_il_2 = QLabel("IL: -- dB")
    label_il_2.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_il_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom_2.addWidget(label_il_2)

    label_sep_2 = QLabel("-")
    layout_bottom_2.addWidget(label_sep_2)

    label_vswr_2 = QLabel("VSWR: --")
    label_vswr_2.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_vswr_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom_2.addWidget(label_vswr_2)

    # --- Agregar box_bottom al layout principal ---
    info_layout_2.addWidget(box_top_2)
    info_layout_2.addWidget(box_bottom_2)

    left_layout.addWidget(info_panel_2)

    # --- Labels dictionary 2 ---
    labels_dict_2 = {
        "val": label_val_2,
        "mag": label_mag_2,
        "phase": label_phase_2,
        "z": label_z_2,
        "il": label_il_2,
        "vswr": label_vswr_2,
        "freq": edit_value_2,
        "unit": lbl_unit_2
    }

    info_panel_2.hide()

    def update_cursor(index, from_slider=False):
        import os
        from PySide6.QtCore import QSettings

        val_complex = S_data[index]
        magnitude = abs(val_complex)
        phase_deg = np.angle(val_complex, deg=True)

        # === Leer modo de unidad desde Graphic1 en el INI ===
        actual_dir = os.path.dirname(os.path.dirname(__file__))
        ruta_ini = os.path.join(actual_dir, "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        unit_mode = settings.value("Graphic1/db_times", "dB")

        # === Actualizar cursor según graph_type y unidad ===
        if graph_type == "Smith Diagram":
            cursor_graph.set_data([np.real(val_complex)], [np.imag(val_complex)])

        elif graph_type == "Magnitude":
            if unit_mode == "dB":
                mag_value = 20 * np.log10(magnitude)
            elif unit_mode == "Power ratio":
                mag_value = magnitude ** 2
            elif unit_mode == "Voltage ratio":
                mag_value = magnitude
            else:
                mag_value = magnitude

            cursor_graph.set_xdata([freqs[index] * 1e-6])
            cursor_graph.set_ydata([mag_value])

        elif graph_type == "Phase":
            cursor_graph.set_data([freqs[index] * 1e-6], [phase_deg])

        # === Actualizar labels ===
        freq_value, freq_unit = format_frequency_smart_split(freqs[index])
        edit_value.setText(freq_value)

        text_width = edit_value.fontMetrics().horizontalAdvance(edit_value.text())
        edit_value.setFixedWidth(max(text_width + 10, 50))

        labels_dict["unit"].setText(freq_unit)
        labels_dict["val"].setText(
            f"{s_param}: {np.real(val_complex):.3f} {'+' if np.imag(val_complex) >= 0 else '-'} j{abs(np.imag(val_complex)):.3f}"
        )
        labels_dict["mag"].setText(f"|{s_param}|: {magnitude:.3f}")
        labels_dict["phase"].setText(f"Phase: {phase_deg:.2f}°")

        z = (1 + val_complex) / (1 - val_complex)
        labels_dict["z"].setText(f"Z: {np.real(z):.2f} + j{np.imag(z):.2f}")

        il_db = -20 * np.log10(magnitude)
        labels_dict["il"].setText(f"IL: {il_db:.2f} dB")

        vswr_val = (1 + magnitude) / (1 - magnitude) if magnitude < 1 else np.inf
        labels_dict["vswr"].setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")

        fig.canvas.draw_idle()

        if not from_slider:
            slider.set_val(index)

        edit_value.clearFocus()

        settings.setValue("Cursor_1_1/index", index)

    def update_cursor_2(index, from_slider=False):
        import os
        from PySide6.QtCore import QSettings

        val_complex = S_data[index]
        magnitude = abs(val_complex)
        phase_deg = np.angle(val_complex, deg=True)

        actual_dir = os.path.dirname(os.path.dirname(__file__))
        ruta_ini = os.path.join(actual_dir, "graphics_windows", "ini", "config.ini")
        settings = QSettings(ruta_ini, QSettings.IniFormat)

        unit_mode = settings.value("Graphic1/db_times", "dB")

        # === Actualizar cursor según graph_type y unidad ===
        if graph_type == "Smith Diagram":
            cursor_graph_2.set_data([np.real(val_complex)], [np.imag(val_complex)])
        elif graph_type == "Magnitude":
            if unit_mode == "dB":
                mag_value = 20 * np.log10(magnitude)
            elif unit_mode == "Power ratio":
                mag_value = magnitude ** 2
            elif unit_mode == "Voltage ratio":
                mag_value = magnitude
            else:
                mag_value = magnitude
            cursor_graph_2.set_xdata([freqs[index] * 1e-6])
            cursor_graph_2.set_ydata([mag_value])
        elif graph_type == "Phase":
            cursor_graph_2.set_data([freqs[index] * 1e-6], [phase_deg])

        # === Actualizar labels del panel 2 ===
        freq_value, freq_unit = format_frequency_smart_split(freqs[index])
        edit_value_2.setText(freq_value)
        text_width = edit_value_2.fontMetrics().horizontalAdvance(edit_value_2.text())
        edit_value_2.setFixedWidth(max(text_width + 10, 50))

        labels_dict_2["unit"].setText(freq_unit)
        labels_dict_2["val"].setText(
            f"{s_param}: {np.real(val_complex):.3f} {'+' if np.imag(val_complex) >= 0 else '-'} j{abs(np.imag(val_complex)):.3f}"
        )
        labels_dict_2["mag"].setText(f"|{s_param}|: {magnitude:.3f}")
        labels_dict_2["phase"].setText(f"Phase: {phase_deg:.2f}°")

        z = (1 + val_complex) / (1 - val_complex)
        labels_dict_2["z"].setText(f"Z: {np.real(z):.2f} + j{np.imag(z):.2f}")

        il_db = -20 * np.log10(magnitude)
        labels_dict_2["il"].setText(f"IL: {il_db:.2f} dB")

        vswr_val = (1 + magnitude) / (1 - magnitude) if magnitude < 1 else np.inf
        labels_dict_2["vswr"].setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")

        fig.canvas.draw_idle()

        if not from_slider:
            slider_2.set_val(index)

        edit_value_2.clearFocus()
        settings.setValue("Cursor_2_1/index", index)


    # --- Slider ---

    if fig is not None:
        slider_ax = fig.add_axes([0.25,0.04,0.5,0.03], facecolor='lightgray')
        slider = Slider(slider_ax, '', 0, len(freqs)-1, valinit=0, valstep=1)
        slider.vline.set_visible(False)
        slider.label.set_visible(False)
        slider.valtext.set_visible(False)  # Hide the value text
        slider.on_changed(lambda val: update_cursor(int(val), from_slider=True))

        slider_ax_2 = fig.add_axes([0.55,0.04,0.35,0.03], facecolor='lightgray')
        slider_2 = Slider(slider_ax_2, '', 0, len(freqs)-1, valinit=0, valstep=1)
        slider_2.vline.set_visible(False)
        slider_2.label.set_visible(False)
        slider_2.valtext.set_visible(False)  # Hide the value text
        slider_2.ax.set_visible(False)
    
    def freq_edited():
        try:
            freq_hz = parse_frequency_input(edit_value.text())
            if freq_hz is not None:
                index = np.argmin(np.abs(freqs - freq_hz))
                update_cursor(index)
            edit_value.clearFocus()
        except:
            pass
    edit_value.editingFinished.connect(freq_edited)

    # --- Cursor draggable ---
    dragging_1 = {"active": False}
    dragging_2 = {"active": False}

    def on_pick(event):
        if event.artist == cursor_graph:
            dragging_1["active"] = True
        elif event.artist == cursor_graph_2:
            dragging_2["active"] = True

    def on_release(event):
        dragging_1["active"] = False
        dragging_2["active"] = False

    def on_motion(event):
        if event.inaxes != ax:
            return

        if dragging_1["active"]:
            if graph_type in ["Magnitude", "Phase"]:
                mouse_x = event.xdata
                index = np.argmin(np.abs(freqs*1e-6 - mouse_x))
                update_cursor(index)
            else:
                mouse_point = complex(event.xdata, event.ydata)
                distances = np.abs(S_data - mouse_point)
                index = np.argmin(distances)
                update_cursor(index)

        elif dragging_2["active"]:
            if graph_type in ["Magnitude", "Phase"]:
                mouse_x = event.xdata
                index = np.argmin(np.abs(freqs*1e-6 - mouse_x))
                update_cursor_2(index)
            else:
                mouse_point = complex(event.xdata, event.ydata)
                distances = np.abs(S_data - mouse_point)
                index = np.argmin(distances)
                update_cursor_2(index)

    # --- Conectar eventos ---
    cursor_graph.set_picker(5)
    cursor_graph_2.set_picker(5)

    canvas.mpl_connect("pick_event", on_pick)
    canvas.mpl_connect("button_release_event", on_release)
    canvas.mpl_connect("motion_notify_event", on_motion)

    # Function to update data references for new sweep data
    def update_data_references(new_s_data, new_freqs):
        nonlocal S_data, freqs
        S_data = new_s_data
        freqs = new_freqs
        # Update freq_edited function to use new freqs
        def freq_edited():
            try:
                freq_hz = parse_frequency_input(edit_value.text())
                if freq_hz is not None:
                    index = np.argmin(np.abs(freqs - freq_hz))
                    update_cursor(index)
                edit_value.clearFocus()
            except:
                pass
        edit_value.editingFinished.disconnect()
        edit_value.editingFinished.connect(freq_edited)

    def update_data_references_2(new_s_data, new_freqs):
        nonlocal S_data, freqs
        S_data = new_s_data
        freqs = new_freqs
        # Update freq_edited function to use new freqs
        def freq_edited():
            try:
                freq_hz = parse_frequency_input(edit_value.text())
                if freq_hz is not None:
                    index = np.argmin(np.abs(freqs - freq_hz))
                    update_cursor_2(index)
                edit_value.clearFocus()
            except:
                pass
        edit_value.editingFinished.disconnect()
        edit_value.editingFinished.connect(freq_edited)

    return left_panel, info_panel, info_panel_2, fig, ax, canvas, slider, slider_2, cursor_graph, cursor_graph_2, labels_dict, labels_dict_2, update_cursor, update_cursor_2, update_data_references

#############################################################################################
# =================== RIGHT PANEL ========================================================= #
#############################################################################################

def create_right_panel(window, settings, S_data=None, freqs=None, graph_type="Smith Diagram", s_param="S11",
                       tracecolor="red", markercolor="red", marker2color="red", linewidth=2, markersize=5, marker2size=5, marker_visible=True):

    brackground_color_graphics = settings.value("Graphic2/BackgroundColor", "red")
    text_color = settings.value("Graphic2/TextColor", "red")
    axis_color = settings.value("Graphic2/AxisColor", "red")

    freqs = freqs if freqs is not None else np.linspace(1e6, 100e6, 101)
    
    if S_data is None:
        phase = -2*np.pi*freqs/1e8
        S_data = 0.5 * np.exp(1j*phase)

    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setAlignment(Qt.AlignTop)
    right_layout.setContentsMargins(10,10,10,10)
    right_layout.setSpacing(10)

    # --- Figura ---
    if graph_type == "Smith Diagram":
        # Use consolidated Smith chart functionality
        from ...utils.smith_chart_utils import SmithChartConfig, SmithChartManager
        
        # Create custom config to match original settings
        config = SmithChartConfig()
        config.background_color = brackground_color_graphics
        config.axis_color = axis_color
        config.text_color = axis_color
        config.trace_color = tracecolor
        config.marker_color = markercolor
        config.linewidth = linewidth
        config.markersize = markersize
        config.marker_visible = marker_visible
        
        # Create Smith chart with custom configuration
        manager = SmithChartManager(config)
        fig, ax, canvas, cursor_graph, cursor_graph_2 = manager.create_graphics_panel_smith_chart(
            s_data=S_data,
            freqs=freqs,
            s_param=s_param,
            figsize=(5, 5),
            container_layout=right_layout,
            trace_color=tracecolor,
            marker_color=markercolor
        )

    elif graph_type == "Magnitude":
        fig, ax = plt.subplots(figsize=(4,3))
        fig.subplots_adjust(left=0.22, right=0.8, top=0.8, bottom=0.22)

        fig.patch.set_facecolor(f"{brackground_color_graphics}")
        ax.set_facecolor(f"{brackground_color_graphics}")

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(canvas)

        ax.plot(freqs*1e-6, np.abs(S_data), color=tracecolor, marker='.', linestyle='-', linewidth=linewidth)

        ax.set_xlabel(r"$\mathrm{Frequency\ [MHz]}$", color=text_color)
        ax.set_ylabel(r"$|%s|$" % s_param, color=text_color)
        ax.set_title(r"$%s\ \mathrm{Magnitude}$" % s_param, color=text_color)

        # Set X-axis limits with margins to match actual frequency range of the sweep
        freq_start = freqs[0]*1e-6
        freq_end = freqs[-1]*1e-6
        freq_range = freq_end - freq_start
        margin = freq_range * 0.05  # 5% margin on each side
        ax.set_xlim(freq_start - margin, freq_end + margin)
        # Set Y-axis limits with margins to provide visual spacing
        magnitude_data = np.abs(S_data)
        y_min = np.min(magnitude_data)
        y_max = np.max(magnitude_data)
        y_range = y_max - y_min
        y_margin = y_range * 0.05  # 5% margin on each side
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        ax.autoscale(False)  # Prevent matplotlib from overriding our xlim/ylim settings
        ax.tick_params(axis='x', colors=f"{axis_color}")
        ax.tick_params(axis='y', colors=f"{axis_color}")

        for spine in ax.spines.values():
            spine.set_color("white")
            
        ax.grid(True, which='both', axis='both', color='white', linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)

        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)
        cursor_graph_2, = ax.plot([], [], 'o', markersize=marker2size, color=marker2color, visible=False)

    elif graph_type == "Phase":
        fig, ax = plt.subplots(figsize=(4,3))
        fig.subplots_adjust(left=0.22, right=0.8, top=0.8, bottom=0.22)

        fig.patch.set_facecolor(f"{brackground_color_graphics}")
        ax.set_facecolor(f"{brackground_color_graphics}")

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(canvas)

        ax.plot(freqs*1e-6, np.angle(S_data, deg=True), color=tracecolor, marker='.', linestyle='-', linewidth=linewidth)

        ax.set_xlabel(r"$\mathrm{Frequency\ [MHz]}$", color=f"{text_color}")
        ax.set_ylabel(r"$\phi_{%s}\ [^\circ]$" % s_param, color=f"{text_color}")
        ax.set_title(r"$\mathrm{%s\ Phase}$" % s_param, color=f"{text_color}")

        # Set X-axis limits with margins to match actual frequency range of the sweep
        freq_start = freqs[0]*1e-6
        freq_end = freqs[-1]*1e-6
        freq_range = freq_end - freq_start
        margin = freq_range * 0.05  # 5% margin on each side
        ax.set_xlim(freq_start - margin, freq_end + margin)
        # Set Y-axis limits with margins to provide visual spacing
        phase_data = np.angle(S_data, deg=True)
        y_min = np.min(phase_data)
        y_max = np.max(phase_data)
        y_range = y_max - y_min
        y_margin = y_range * 0.05  # 5% margin on each side
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        ax.autoscale(False)  # Prevent matplotlib from overriding our xlim/ylim settings
        ax.tick_params(axis='x', colors=f"{axis_color}")
        ax.tick_params(axis='y', colors=f"{axis_color}")

        for spine in ax.spines.values():
            spine.set_color("white")
            
        ax.grid(True, which='both', axis='both', color='white', linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)
        
        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)
        cursor_graph_2, = ax.plot([], [], 'o', markersize=marker2size, color=marker2olor, visible=False)

    # --- Info panel (Right side reorganized) ---
    info_panel = QWidget()
    info_layout = QVBoxLayout(info_panel)
    info_layout.setSpacing(10)
    info_layout.setContentsMargins(0, 0, 0, 0)

    # --- Top QGroupBox with title ---
    box_top = QGroupBox("S-Parameter Details")
    layout_top = QHBoxLayout(box_top)
    layout_top.setSpacing(20)
    layout_top.setContentsMargins(12, 8, 12, 8)  # márgenes equilibrados

    # --- Sub-layout centrado para los 4 bloques ---
    center_layout = QHBoxLayout()
    center_layout.setSpacing(15)  # espacio entre columnas
    center_layout.setAlignment(Qt.AlignCenter)  # todo centrado en el box

    # --- Column 1: Frequency ---
    col_left = QVBoxLayout()
    col_left.setSpacing(5)
    col_left.setAlignment(Qt.AlignVCenter)

    hbox_freq = QHBoxLayout()
    hbox_freq.setAlignment(Qt.AlignLeft)
    hbox_freq.setContentsMargins(0, 0, 0, 0)

    lbl_text = QLabel("Frequency:")
    lbl_text.setStyleSheet("font-size:14px;")
    lbl_text.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    hbox_freq.addWidget(lbl_text)

    initial_freq_value, initial_freq_unit = format_frequency_smart_split(freqs[0])
    edit_value = QLineEdit(initial_freq_value)

    def limit_frequency_input(text, max_digits=6, max_decimals=3, allow_dashes=False):
        if text == "--":  # allow dashes
            return text
        filtered = "".join(c for c in text if c.isdigit() or c == ".")
        if filtered.count(".") > 1:
            parts = filtered.split(".", 1)
            filtered = parts[0] + "." + "".join(parts[1:]).replace(".", "")
        if "." in filtered:
            integer_part, decimal_part = filtered.split(".", 1)
            integer_part = integer_part[:max_digits]
            decimal_part = decimal_part[:max_decimals]
            filtered = integer_part + "." + decimal_part
        else:
            filtered = filtered[:max_digits]
        return filtered

    def on_text_changed():
        new_text = limit_frequency_input(edit_value.text(), 3, 3, allow_dashes=True)
        if new_text != edit_value.text():
            edit_value.setText(new_text)
        if new_text != edit_value.text():
            edit_value.setText(new_text)
        text_width = edit_value.fontMetrics().horizontalAdvance(edit_value.text())
        min_width = max(text_width + 10, 40)
        edit_value.setFixedWidth(min_width)

    edit_value.textChanged.connect(on_text_changed)
    edit_value.setStyleSheet("font-size:14px; border:none; background:transparent;")
    edit_value.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    text_width = edit_value.fontMetrics().horizontalAdvance(edit_value.text())
    min_width = max(text_width + 10, 40)
    edit_value.setFixedWidth(min_width)
    hbox_freq.addWidget(edit_value)

    lbl_unit = QLabel(initial_freq_unit)
    lbl_unit.setStyleSheet("font-size:14px;")
    lbl_unit.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    lbl_unit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    hbox_freq.addWidget(lbl_unit)

    col_left.addLayout(hbox_freq)

    # --- Column 2: S11 real + imag ---
    label_val = QLabel(f"{s_param}: -- + j--")
    label_val.setStyleSheet("font-size:14px; padding:1px;")
    label_val.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_s11 = QVBoxLayout()
    col_s11.setSpacing(5)
    col_s11.setAlignment(Qt.AlignVCenter)
    col_s11.addWidget(label_val)

    # --- Column 3: |S11| ---
    label_mag = QLabel(f"|{s_param}|: --")
    label_mag.setStyleSheet("font-size:14px; padding:1px;")
    label_mag.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_mag = QVBoxLayout()
    col_mag.setSpacing(5)
    col_mag.setAlignment(Qt.AlignVCenter)
    col_mag.addWidget(label_mag)

    # --- Column 4: Phase ---
    label_phase = QLabel("Phase: --")
    label_phase.setStyleSheet("font-size:14px; padding:1px;")
    label_phase.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_phase = QVBoxLayout()
    col_phase.setSpacing(5)
    col_phase.setAlignment(Qt.AlignVCenter)
    col_phase.addWidget(label_phase)

    # --- Agregar columnas al layout centrado con separadores ---
    center_layout.addLayout(col_left)

    label_sep = QLabel("-")
    center_layout.addWidget(label_sep)

    center_layout.addLayout(col_s11)

    label_sep = QLabel("-")
    center_layout.addWidget(label_sep)

    center_layout.addLayout(col_mag)
    
    label_sep = QLabel("-")
    center_layout.addWidget(label_sep)
    
    center_layout.addLayout(col_phase)

    # --- Add Layout ---
    layout_top.addLayout(center_layout)

    # --- Bottom QGroupBox ---
    box_bottom = QGroupBox("DUT Parameters")
    layout_bottom = QHBoxLayout(box_bottom)
    layout_bottom.setSpacing(40) 
    layout_bottom.setContentsMargins(10, 8, 10, 8)
    layout_bottom.setAlignment(Qt.AlignCenter)  

    # --- Labels dentro del box_bottom ---
    label_z = QLabel("Zin (Z0): -- + j--")
    label_z.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_z.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom.addWidget(label_z)

    label_sep = QLabel("-")
    layout_bottom.addWidget(label_sep)

    label_il = QLabel("IL: -- dB")
    label_il.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_il.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom.addWidget(label_il)

    label_sep = QLabel("-")
    layout_bottom.addWidget(label_sep)

    label_vswr = QLabel("VSWR: --")
    label_vswr.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_vswr.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom.addWidget(label_vswr)

    info_layout.addWidget(box_top)
    info_layout.addWidget(box_bottom) 

    # Add to external layout
    right_layout.addWidget(info_panel)

    # --- Labels dictionary ---
    labels_dict = {
        "val": label_val,
        "mag": label_mag,
        "phase": label_phase,
        "z": label_z,
        "il": label_il,
        "vswr": label_vswr,
        "freq": edit_value,
        "unit": lbl_unit
    }

    # --- Info panel (Right side reorganized) duplicate for marker 2 ---
    info_panel_2 = QWidget()
    info_layout_2 = QVBoxLayout(info_panel_2)
    info_layout_2.setSpacing(10)
    info_layout_2.setContentsMargins(0, 0, 0, 0)

    # --- Top QGroupBox with title ---
    box_top_2 = QGroupBox("S-Parameter Details 2")
    layout_top_2 = QHBoxLayout(box_top_2)
    layout_top_2.setSpacing(20)
    layout_top_2.setContentsMargins(12, 8, 12, 8)

    center_layout_2 = QHBoxLayout()
    center_layout_2.setSpacing(15)
    center_layout_2.setAlignment(Qt.AlignCenter)

    # --- Column 1: Frequency ---
    col_left_2 = QVBoxLayout()
    col_left_2.setSpacing(5)
    col_left_2.setAlignment(Qt.AlignVCenter)

    hbox_freq_2 = QHBoxLayout()
    hbox_freq_2.setAlignment(Qt.AlignLeft)
    hbox_freq_2.setContentsMargins(0, 0, 0, 0)

    lbl_text_2 = QLabel("Frequency:")
    lbl_text_2.setStyleSheet("font-size:14px;")
    lbl_text_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    hbox_freq_2.addWidget(lbl_text_2)

    initial_freq_value_2, initial_freq_unit_2 = format_frequency_smart_split(freqs[0])
    edit_value_2 = QLineEdit(initial_freq_value_2)

    def on_text_changed_2():
        new_text = limit_frequency_input(edit_value_2.text(), 3, 3, allow_dashes=True)
        if new_text != edit_value_2.text():
            edit_value_2.setText(new_text)
        text_width = edit_value_2.fontMetrics().horizontalAdvance(edit_value_2.text())
        min_width = max(text_width + 10, 40)
        edit_value_2.setFixedWidth(min_width)

    edit_value_2.textChanged.connect(on_text_changed_2)
    edit_value_2.setStyleSheet("font-size:14px; border:none; background:transparent;")
    edit_value_2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    text_width = edit_value_2.fontMetrics().horizontalAdvance(edit_value_2.text())
    min_width = max(text_width + 10, 40)
    edit_value_2.setFixedWidth(min_width)
    hbox_freq_2.addWidget(edit_value_2)

    lbl_unit_2 = QLabel(initial_freq_unit_2)
    lbl_unit_2.setStyleSheet("font-size:14px;")
    lbl_unit_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    lbl_unit_2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    hbox_freq_2.addWidget(lbl_unit_2)

    col_left_2.addLayout(hbox_freq_2)

    # --- Column 2: S11 real + imag ---
    label_val_2 = QLabel(f"{s_param}: -- + j--")
    label_val_2.setStyleSheet("font-size:14px; padding:1px;")
    label_val_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_s11_2 = QVBoxLayout()
    col_s11_2.setSpacing(5)
    col_s11_2.setAlignment(Qt.AlignVCenter)
    col_s11_2.addWidget(label_val_2)

    # --- Column 3: |S11| ---
    label_mag_2 = QLabel(f"|{s_param}|: --")
    label_mag_2.setStyleSheet("font-size:14px; padding:1px;")
    label_mag_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_mag_2 = QVBoxLayout()
    col_mag_2.setSpacing(5)
    col_mag_2.setAlignment(Qt.AlignVCenter)
    col_mag_2.addWidget(label_mag_2)

    # --- Column 4: Phase ---
    label_phase_2 = QLabel("Phase: --")
    label_phase_2.setStyleSheet("font-size:14px; padding:1px;")
    label_phase_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    col_phase_2 = QVBoxLayout()
    col_phase_2.setSpacing(5)
    col_phase_2.setAlignment(Qt.AlignVCenter)
    col_phase_2.addWidget(label_phase_2)

    # --- Agregar columnas al layout centrado ---
    center_layout_2.addLayout(col_left_2)

    label_sep_2 = QLabel("-")
    center_layout_2.addWidget(label_sep_2)

    center_layout_2.addLayout(col_s11_2)

    label_sep_2 = QLabel("-")
    center_layout_2.addWidget(label_sep_2)

    center_layout_2.addLayout(col_mag_2)

    label_sep_2 = QLabel("-")
    center_layout_2.addWidget(label_sep_2)

    center_layout_2.addLayout(col_phase_2)

    layout_top_2.addLayout(center_layout_2)

    # --- Bottom QGroupBox ---
    box_bottom_2 = QGroupBox("DUT Parameters 2")
    layout_bottom_2 = QHBoxLayout(box_bottom_2)
    layout_bottom_2.setSpacing(40)
    layout_bottom_2.setContentsMargins(10, 8, 10, 8)
    layout_bottom_2.setAlignment(Qt.AlignCenter)

    label_z_2 = QLabel("Zin (Z0): -- + j--")
    label_z_2.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_z_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom_2.addWidget(label_z_2)

    label_sep_2 = QLabel("-")
    layout_bottom_2.addWidget(label_sep_2)

    label_il_2 = QLabel("IL: -- dB")
    label_il_2.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_il_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom_2.addWidget(label_il_2)

    label_sep_2 = QLabel("-")
    layout_bottom_2.addWidget(label_sep_2)

    label_vswr_2 = QLabel("VSWR: --")
    label_vswr_2.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")
    label_vswr_2.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    layout_bottom_2.addWidget(label_vswr_2)

    info_layout_2.addWidget(box_top_2)
    info_layout_2.addWidget(box_bottom_2)

    right_layout.addWidget(info_panel_2)

    # --- Labels dictionary 2 ---
    labels_dict_2 = {
        "val": label_val_2,
        "mag": label_mag_2,
        "phase": label_phase_2,
        "z": label_z_2,
        "il": label_il_2,
        "vswr": label_vswr_2,
        "freq": edit_value_2,
        "unit": lbl_unit_2
    }

    info_panel_2.hide()

    def update_cursor(index, from_slider=False):
        val_complex = S_data[index]
        magnitude = abs(val_complex)
        phase_deg = np.angle(val_complex, deg=True)

        if graph_type == "Smith Diagram":
            cursor_graph.set_data([np.real(val_complex)], [np.imag(val_complex)])
        elif graph_type == "Magnitude":
            cursor_graph.set_data([freqs[index]*1e-6], [magnitude])
        elif graph_type == "Phase":
            cursor_graph.set_data([freqs[index]*1e-6], [phase_deg])

        freq_value, freq_unit = format_frequency_smart_split(freqs[index])
        edit_value.setText(f"  {freq_value}")

        # Update field width when frequency changes from slider
        text_width = edit_value.fontMetrics().horizontalAdvance(edit_value.text())
        min_width = max(text_width + 10, 50)
        edit_value.setFixedWidth(min_width)
        labels_dict["unit"].setText(freq_unit)

        labels_dict["val"].setText(f"{s_param}: {np.real(val_complex):.3f} {'+' if np.imag(val_complex)>=0 else '-'} j{abs(np.imag(val_complex)):.3f}")
        labels_dict["mag"].setText(f"|{s_param}|: {magnitude:.3f}")
        labels_dict["phase"].setText(f"Phase: {phase_deg:.2f}°")
        z = (1 + val_complex)/(1 - val_complex)
        labels_dict["z"].setText(f"Z: {np.real(z):.2f} + j{np.imag(z):.2f}")
        il_db = -20*np.log10(magnitude)
        labels_dict["il"].setText(f"IL: {il_db:.2f} dB")
        vswr_val = (1 + magnitude)/(1 - magnitude) if magnitude < 1 else np.inf
        labels_dict["vswr"].setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")
        fig.canvas.draw_idle()

        if not from_slider:
            slider.set_val(index)

        edit_value.clearFocus()

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        settings.setValue("Cursor_1_2/index", index)

    def update_cursor_2(index, from_slider=False):
        import os
        from PySide6.QtCore import QSettings

        val_complex = S_data[index]
        magnitude = abs(val_complex)
        phase_deg = np.angle(val_complex, deg=True)

        actual_dir = os.path.dirname(os.path.dirname(__file__))
        ruta_ini = os.path.join(actual_dir, "graphics_windows", "ini", "config.ini")
        settings = QSettings(ruta_ini, QSettings.IniFormat)

        unit_mode = settings.value("Graphic1/db_times", "dB")

        # === Actualizar cursor según graph_type y unidad ===
        if graph_type == "Smith Diagram":
            cursor_graph_2.set_data([np.real(val_complex)], [np.imag(val_complex)])
        elif graph_type == "Magnitude":
            if unit_mode == "dB":
                mag_value = 20 * np.log10(magnitude)
            elif unit_mode == "Power ratio":
                mag_value = magnitude ** 2
            elif unit_mode == "Voltage ratio":
                mag_value = magnitude
            else:
                mag_value = magnitude
            cursor_graph_2.set_xdata([freqs[index] * 1e-6])
            cursor_graph_2.set_ydata([mag_value])
        elif graph_type == "Phase":
            cursor_graph_2.set_data([freqs[index] * 1e-6], [phase_deg])

        # === Actualizar labels del panel 2 ===
        freq_value, freq_unit = format_frequency_smart_split(freqs[index])
        edit_value_2.setText(freq_value)

        text_width = edit_value_2.fontMetrics().horizontalAdvance(edit_value_2.text())
        edit_value_2.setFixedWidth(max(text_width + 10, 50))

        labels_dict_2["unit"].setText(freq_unit)
        labels_dict_2["val"].setText(
            f"{s_param}: {np.real(val_complex):.3f} {'+' if np.imag(val_complex) >= 0 else '-'} j{abs(np.imag(val_complex)):.3f}"
        )
        labels_dict_2["mag"].setText(f"|{s_param}|: {magnitude:.3f}")
        labels_dict_2["phase"].setText(f"Phase: {phase_deg:.2f}°")

        z = (1 + val_complex) / (1 - val_complex)
        labels_dict_2["z"].setText(f"Z: {np.real(z):.2f} + j{np.imag(z):.2f}")

        il_db = -20 * np.log10(magnitude)
        labels_dict_2["il"].setText(f"IL: {il_db:.2f} dB")

        vswr_val = (1 + magnitude) / (1 - magnitude) if magnitude < 1 else np.inf
        labels_dict_2["vswr"].setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")

        fig.canvas.draw_idle()

        if not from_slider:
            slider_2.set_val(index)

        edit_value_2.clearFocus()
        settings.setValue("Cursor_2_2/index", index)


    # --- Slider ---
    slider_ax = fig.add_axes([0.25,0.04,0.5,0.03], facecolor='lightgray')
    slider = Slider(slider_ax, '', 0, len(freqs)-1, valinit=0, valstep=1)
    slider.vline.set_visible(False)
    slider.label.set_visible(False)
    slider.valtext.set_visible(False)  # Hide the value text
    slider.on_changed(lambda val: update_cursor(int(val), from_slider=True))

    slider_ax_2 = fig.add_axes([0.55,0.04,0.35,0.03], facecolor='lightgray')
    slider_2 = Slider(slider_ax_2, '', 0, len(freqs)-1, valinit=0, valstep=1)
    slider_2.vline.set_visible(False)
    slider_2.label.set_visible(False)
    slider_2.valtext.set_visible(False)  # Hide the value text
    slider_2.ax.set_visible(False)

    # --- Conectar edición manual ---
    def freq_edited():
        try:
            freq_hz = parse_frequency_input(edit_value.text())
            if freq_hz is not None:
                index = np.argmin(np.abs(freqs - freq_hz))
                update_cursor(index)
            edit_value.clearFocus()
        except:
            pass
    edit_value.editingFinished.connect(freq_edited)

    # --- Inicializar ---
    update_cursor(0)

    # --- Cursor draggable ---
    dragging_1 = {"active": False}
    dragging_2 = {"active": False}

    def on_pick(event):
        if event.artist == cursor_graph:
            dragging_1["active"] = True
        elif event.artist == cursor_graph_2:
            dragging_2["active"] = True

    def on_release(event):
        dragging_1["active"] = False
        dragging_2["active"] = False

    def on_motion(event):
        if event.inaxes != ax:
            return

        if dragging_1["active"]:
            if graph_type in ["Magnitude", "Phase"]:
                mouse_x = event.xdata
                index = np.argmin(np.abs(freqs*1e-6 - mouse_x))
                update_cursor(index)
            else:
                mouse_point = complex(event.xdata, event.ydata)
                distances = np.abs(S_data - mouse_point)
                index = np.argmin(distances)
                update_cursor(index)

        elif dragging_2["active"]:
            if graph_type in ["Magnitude", "Phase"]:
                mouse_x = event.xdata
                index = np.argmin(np.abs(freqs*1e-6 - mouse_x))
                update_cursor_2(index)
            else:
                mouse_point = complex(event.xdata, event.ydata)
                distances = np.abs(S_data - mouse_point)
                index = np.argmin(distances)
                update_cursor_2(index)

    # --- Conectar eventos ---
    cursor_graph.set_picker(5)
    cursor_graph_2.set_picker(5)

    canvas.mpl_connect("pick_event", on_pick)
    canvas.mpl_connect("button_release_event", on_release)
    canvas.mpl_connect("motion_notify_event", on_motion)
    
    # Function to update data references for new sweep data
    def update_data_references(new_s_data, new_freqs):
        nonlocal S_data, freqs
        S_data = new_s_data
        freqs = new_freqs

    return right_panel, info_panel, info_panel_2, fig, ax, canvas, slider, slider_2, cursor_graph, cursor_graph_2, labels_dict, labels_dict_2, update_cursor, update_cursor_2, update_data_references