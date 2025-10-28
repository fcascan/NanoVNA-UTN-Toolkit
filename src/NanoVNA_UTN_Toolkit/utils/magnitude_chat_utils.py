"""
Magnitude Plot utilities for NanoVNA toolkit.

This module consolidates all magnitude plot-related functionality that was previously
duplicated across multiple files (wizard_windows.py, graphics_window.py, graphics_utils.py, etc.).
"""

import logging
import numpy as np
import skrf as rf
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QSizePolicy
import matplotlib.pyplot as plt
from typing import Optional, Dict, Tuple, List, Any

import matplotlib.pyplot as plt

plt.rcParams['mathtext.fontset'] = 'cm'   # Fuente Computer Modern
plt.rcParams['text.usetex'] = False       # No requiere LaTeX externo
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['font.family'] = 'serif'     # Coincide con el estilo de LaTeX
plt.rcParams['mathtext.rm'] = 'serif'     # Números y texto coherentes


class MagnitudeChartConfig:
    """Configuration class for magnitude chart styling and behavior."""
    
    def __init__(self):
        # Colors
        self.background_color = "#3a3a3a"
        self.axis_color = "white"
        self.text_color = "white"
        self.trace_color = "blue"
        self.marker_color = "red"
        
        # Line styling
        self.linewidth = 2
        self.markersize = 6
        self.marker_visible = True


class MagnitudeChartBuilder:
    """Builder class for creating and customizing magnitude charts (|S21| vs frequency)."""
    
    def __init__(self, config=None):
        self.config = config if config else MagnitudeChartConfig()
        self.ax = None
        self.fig = None
        self.canvas = None

    def setup_figure(self, figsize=(6, 4), layout_params=None):
        if layout_params is None:
            layout_params = {'left': 0.15, 'right': 0.95, 'top': 0.9, 'bottom': 0.15}

        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.tick_params(axis='x', colors=self.config.axis_color)
        self.ax.tick_params(axis='y', colors=self.config.axis_color)
        self.ax.xaxis.label.set_color(self.config.text_color)
        self.ax.yaxis.label.set_color(self.config.text_color)
        self.ax.title.set_color(self.config.text_color)
        self.fig.patch.set_facecolor(self.config.background_color)
        self.ax.set_facecolor(self.config.background_color)
        self.ax.grid(True, linestyle="--", alpha=0.5)

        self.ax.set_xlabel(r"$\mathrm{Frequency\ (Hz)}$")
        self.ax.set_ylabel(r"$|S_{21}|\ (\mathrm{dB})$")
        self.ax.set_title(r"$\mathrm{Magnitude}$")

        self.fig.tight_layout()

        def on_resize(event):
            self.fig.tight_layout()
            self.canvas.draw_idle()

        self.fig.canvas.mpl_connect("resize_event", on_resize)

        return self.fig, self.ax

    def create_canvas(self):
        """Create Qt canvas for the figure."""
        if self.fig is None:
            raise ValueError("Figure must be created first using setup_figure()")
        self.canvas = FigureCanvas(self.fig)
        return self.canvas

    def plot_measurement_data(self, freqs, s_data, label=None, color=None, in_dB=False):
        """Plot measurement data as magnitude vs frequency."""
        if self.ax is None:
            raise ValueError("Axis must be created first using setup_figure()")
        
        color = color or self.config.trace_color
        magnitude = np.abs(s_data)
        if in_dB:
            magnitude = 20 * np.log10(magnitude + 1e-12)
        
        self.ax.plot(freqs, magnitude, '-', color=color, linewidth=self.config.linewidth, label=label)
        if label:
            self.ax.legend()
        return self.ax

    def add_cursor_marker(self, visible=None, color=None, size=None):
        """Add a cursor marker for interactive use."""
        visible = visible if visible is not None else self.config.marker_visible
        color = color or self.config.marker_color
        size = size or self.config.markersize
        if self.ax is None:
            return None
        cursor, = self.ax.plot([], [], 'o', markersize=size, color=color, visible=visible)
        return cursor

    def clear_and_redraw(self):
        """Clear axis for new plot."""
        if self.ax:
            self.ax.clear()
    
    def refresh_canvas(self):
        """Refresh the canvas display."""
        if self.canvas:
            self.canvas.draw()


class MagnitudeChartManager:
    """High-level manager for magnitude chart operations."""
    
    def __init__(self, config=None):
        self.config = config if config else MagnitudeChartConfig()
        self.builder = MagnitudeChartBuilder(self.config)

    # ============================================================
    # Wizard charts
    # ============================================================
    def create_wizard_magnitude_chart(self, start_freq, stop_freq, num_points, figsize=(6, 4), container_layout=None):
        """Create magnitude chart for calibration wizard."""
        fig, ax = self.builder.setup_figure(figsize=figsize)
        freqs = np.linspace(start_freq, stop_freq, num_points)
        ax.plot(freqs, np.zeros(num_points), color="gray", alpha=0.3)
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
        
        canvas = self.builder.create_canvas()
        if container_layout:
            container_layout.addWidget(canvas)
        return fig, ax, canvas

    def apply_axis_style(self, ax):
        """Apply consistent styling to the given axis."""
        ax.set_facecolor(self.config.background_color)
        ax.tick_params(axis='x', colors=self.config.axis_color)
        ax.tick_params(axis='y', colors=self.config.axis_color)
        ax.xaxis.label.set_color(self.config.text_color)
        ax.yaxis.label.set_color(self.config.text_color)
        ax.title.set_color(self.config.text_color)
        ax.grid(True, linestyle="--", alpha=0.5)

    def update_wizard_measurement(self, ax, freqs, s21_data, standard_name, canvas=None, color_map=None, in_dB=False):
        if color_map is None:
            color_map = {'thru': 'blue', 'open': 'orange', 'short': 'red', 'load': 'green'}

        try:
            ax.clear()  # borra todo

            self.apply_axis_style(ax)  # reaplica estilos

            # Etiquetas y título dinámico
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("|S21| (dB)" if in_dB else "|S21| (times)")
            ax.set_title(f"{standard_name.upper()} – Magnitude vs Frequency")  # título dinámico

            color = color_map.get(standard_name.lower(), self.config.trace_color)
            magnitude = np.abs(s21_data)
            magnitude = 20 * np.log10(magnitude + 1e-12)

            ax.plot(freqs, magnitude, '-', color=color, linewidth=self.config.linewidth)
            legend_line = Line2D([0], [0], color=color)
            ax.legend([legend_line], [standard_name.upper()], loc='upper right', frameon=True)

            if canvas:
                canvas.draw()

            logging.info(f"[MagnitudeChartManager] Updated magnitude plot for {standard_name}")

        except Exception as e:
            logging.error(f"[MagnitudeChartManager] Error updating magnitude measurement: {e}")


    # ============================================================
    # Graphics panel charts
    # ============================================================
    def create_graphics_panel_magnitude_chart(self, s_data, freqs, s_param="S21", figsize=(6, 4),
                                              container_layout=None, trace_color=None, marker_color=None, in_dB=False):
        """Create magnitude chart for graphics panels."""
        fig, ax = self.builder.setup_figure(figsize=figsize)
        self.builder.plot_measurement_data(freqs, s_data, label=s_param, color=trace_color, in_dB=in_dB)
        cursor = self.builder.add_cursor_marker(color=marker_color)
        canvas = self.builder.create_canvas()
        if container_layout:
            container_layout.addWidget(canvas)
        return fig, ax, canvas, cursor

    # ============================================================
    # Multi-measurement support
    # ============================================================
    def show_multiple_measurements(self, ax, measurements_dict, canvas=None, color_map=None,
                                   start_freq=None, stop_freq=None, num_points=None, in_dB=False):
        """Show multiple magnitude measurements on the same chart."""
        if color_map is None:
            color_map = {name.lower(): None for name in measurements_dict.keys()}
        try:
            ax.clear()
            for standard_name, (freqs, s21_data) in measurements_dict.items():
                color = color_map.get(standard_name.lower(), self.config.trace_color)
                magnitude = np.abs(s21_data)
                if in_dB:
                    magnitude = 20 * np.log10(magnitude + 1e-12)
                ax.plot(freqs, magnitude, '-', color=color, linewidth=self.config.linewidth, label=standard_name.upper())
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("|S21| (times)" if not in_dB else "|S21| (dB)")
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend()
            if canvas:
                canvas.draw()
            logging.info(f"[MagnitudeChartManager] Displayed {len(measurements_dict)} magnitude measurements")
        except Exception as e:
            logging.error(f"[MagnitudeChartManager] Error showing multiple magnitude measurements: {e}")


# ============================================================
# Convenience functions (analogous to Smith chart)
# ============================================================
def create_simple_magnitude_chart(freqs, s_data, figsize=(6, 4), s_param="S21", in_dB=False):
    """Simple function to create a basic magnitude chart."""
    manager = MagnitudeChartManager()
    fig, ax = manager.builder.setup_figure(figsize=figsize)
    manager.builder.plot_measurement_data(freqs, s_data, label=s_param, in_dB=in_dB)
    canvas = manager.builder.create_canvas()
    return fig, ax, canvas

def update_magnitude_chart_measurement(ax, freqs, s21_data, standard_name, canvas=None, in_dB=False):
    """Simple function to update magnitude chart with measurement."""
    manager = MagnitudeChartManager()
    manager.update_wizard_measurement(ax, freqs, s21_data, standard_name, canvas, in_dB=in_dB)

def create_wizard_magnitude_chart(start_freq, stop_freq, num_points, container_layout=None, figsize=(6, 4)):
    """Simple function to create wizard magnitude chart."""
    manager = MagnitudeChartManager()
    return manager.create_wizard_magnitude_chart(start_freq, stop_freq, num_points, figsize=figsize, container_layout=container_layout)
