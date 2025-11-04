""" 

Graph Preview Export Dialog for NanoVNA Measurements
Provides an interactive preview of S-parameter graphs with navigation
and PDF export functionality using Matplotlib and PySide6. 

"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QWidget
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import skrf as rf
import logging

logger = logging.getLogger(__name__)

class GraphPreviewExportDialog(QDialog):
    def __init__(self, parent=None, freqs=None, s11_data=None, s21_data=None,
                 measurement_name=None, output_path=None):
        super().__init__(parent)
        self.freqs = freqs
        self.s11_data = s11_data
        self.s21_data = s21_data
        self.measurement_name = measurement_name
        self.output_path = output_path
        self.current_graph_index = 0

        self.setWindowTitle("Export Graph Preview")
        self.setModal(True)
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout(self)

        label = QLabel(
            "Graph preview is ready.\n"
            "Use the arrows below to explore all measurement views before exporting the PDF."
        )
        label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label)

        # --- Create figure and canvas ---
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.fig.patch.set_facecolor("white")
        self.ax.set_facecolor("white")
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.18)
        self.canvas = FigureCanvas(self.fig)

        # --- Canvas container with overlay buttons ---
        self.canvas_container = QWidget()
        self.canvas_container.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(self.canvas_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        # --- Navigation buttons ---
        self.prev_button = QPushButton("← Previous")
        self.next_button = QPushButton("Next →")

        btn_style = """
            QPushButton {
                background-color: rgba(245, 245, 245, 0.9);
                border: 1px solid #777;
                border-radius: 5px;
                font-weight: bold;
                color: #333;
                min-width: 70px;
                max-width: 70px;
                min-height: 20px;
                max-height: 20px;   
                padding: 2px 4px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.95);
            }
        """
        self.prev_button.setStyleSheet(btn_style)
        self.next_button.setStyleSheet(btn_style)
        self.prev_button.setParent(self.canvas_container)
        self.next_button.setParent(self.canvas_container)
        self.prev_button.raise_()
        self.next_button.raise_()

        # --- Handle resize for positioning ---
        self.canvas_container.resizeEvent = self._on_resize_canvas

        # --- Connections ---
        self.prev_button.clicked.connect(self._show_previous_graph)
        self.next_button.clicked.connect(self._show_next_graph)

        main_layout.addWidget(self.canvas_container, alignment=Qt.AlignCenter)

        # --- Export button ---
        self.export_button = QPushButton("Generate PDF Report")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.export_button.clicked.connect(self._generate_pdf)
        main_layout.addWidget(self.export_button, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self._plot_graph(self.current_graph_index)
        self._update_nav_buttons()

    def _on_resize_canvas(self, event):
        """Reposition navigation buttons with padding."""
        padding = 15
        button_y = self.canvas_container.height() - self.prev_button.height() - padding
        self.prev_button.move(padding, button_y)
        self.next_button.move(self.canvas_container.width() - self.next_button.width() - padding, button_y)
        QWidget.resizeEvent(self.canvas_container, event)

    def _plot_graph(self, index):
        """Plot one of the five measurement graphs."""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("white")
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.18)

        freqs = self.freqs if self.freqs is not None else np.linspace(1e6, 1e8, 100)
        s11 = self.s11_data if self.s11_data is not None else np.exp(1j * np.linspace(0, 2*np.pi, 100))
        s21 = self.s21_data if self.s21_data is not None else 20 * np.log10(np.abs(np.sin(freqs / 1e8 * np.pi)))

        if index == 0:
            ax.set_title("Smith Chart - S11", fontsize=12, weight="bold", pad=20)
            rf.plotting.smith(ax=ax, smithR=1)
            self.fig.subplots_adjust(left=0.08, right=0.95, top=0.9, bottom=0.18)

            gamma = s11
            ax.plot(np.real(gamma), np.imag(gamma), color="red", linewidth=1.2)
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlim(-1.1, 1.1)
            ax.set_ylim(-1.1, 1.1)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.plot([-1, 1], [0, 0], color="black", linewidth=1)
            ax.title.set_position([0.48, 0.9])
        elif index == 1:
            ax.plot(freqs, 20 * np.log10(np.abs(s11)), color="red", linewidth=1.3)
            ax.set_title("Magnitude |S11| (dB)", fontsize=12, weight="bold", pad=12)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("|S11| (dB)")
            ax.grid(True, linestyle="--", alpha=0.6)
        elif index == 2:
            ax.plot(freqs, np.angle(s11, deg=True), color="red", linewidth=1.3)
            ax.set_title("Phase S11 (°)", fontsize=12, weight="bold", pad=12)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("Phase (°)")
            ax.grid(True, linestyle="--", alpha=0.6)
        elif index == 3:
            ax.plot(freqs, s21, color="blue", linewidth=1.3)
            ax.set_title("Magnitude |S21| (dB)", fontsize=12, weight="bold", pad=12)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("|S21| (dB)")
            ax.grid(True, linestyle="--", alpha=0.6)
        elif index == 4:
            phase_s21 = np.angle(np.exp(1j * freqs / 1e7), deg=True)
            ax.plot(freqs, phase_s21, color="blue", linewidth=1.3)
            ax.set_title("Phase S21 (°)", fontsize=12, weight="bold", pad=12)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("Phase (°)")
            ax.grid(True, linestyle="--", alpha=0.6)

        self.canvas.draw()

    def _show_next_graph(self):
        if self.current_graph_index < 4:
            self.current_graph_index += 1
            self._plot_graph(self.current_graph_index)
            self._update_nav_buttons()

    def _show_previous_graph(self):
        if self.current_graph_index > 0:
            self.current_graph_index -= 1
            self._plot_graph(self.current_graph_index)
            self._update_nav_buttons()

    def _update_nav_buttons(self):
        """Hide or show navigation buttons appropriately."""
        self.prev_button.setVisible(self.current_graph_index > 0)
        self.next_button.setVisible(self.current_graph_index < 4)

    def _generate_pdf(self):
        try:
            from NanoVNA_UTN_Toolkit.exporters.latex_exporter import LatexExporter
            exporter = LatexExporter()
            if not self.output_path:
                QMessageBox.warning(self, "Missing Path", "No output path specified.")
                return
            success = exporter.export_to_pdf(
                freqs=self.freqs,
                s11_data=self.s11_data,
                s21_data=self.s21_data,
                measurement_name=self.measurement_name,
                output_path=self.output_path
            )
            if success:
                QMessageBox.information(self, "Export Complete",
                                        f"PDF successfully created at:\n{self.output_path}")
                self.accept()
            else:
                QMessageBox.warning(self, "Export Failed",
                                    "PDF export failed. Please check the logs for details.")
        except Exception as e:
            logger.exception("PDF export failed")
            QMessageBox.critical(self, "Export Failed",
                                 f"Error creating PDF:\n{str(e)}")
