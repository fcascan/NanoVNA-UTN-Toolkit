from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout
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
        self.current_graph_index = 0  # Track which graph is displayed

        self.setWindowTitle("Export Graph Preview")
        self.setModal(True)
        self.setMinimumSize(600, 400)

        # --- Main layout container ---
        main_layout = QVBoxLayout(self)

        # --- Description label ---
        label = QLabel(
            "Graph preview is ready.\n"
            "Use the arrows below to explore all measurement views before exporting the PDF."
        )
        label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label)

        # --- Create matplotlib figure and canvas ---
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.fig.subplots_adjust(left=0.2, right=0.95, top=0.85, bottom=0.2)  # Centered layout
        self.fig.patch.set_facecolor("white")
        self.ax.set_facecolor("white")
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas, alignment=Qt.AlignCenter)

        # --- Initial plot ---
        self._plot_graph(self.current_graph_index)

        # --- Navigation buttons (Previous / Next) ---
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("← Previous")
        self.next_button = QPushButton("Next →")
        self.prev_button.clicked.connect(self._show_previous_graph)
        self.next_button.clicked.connect(self._show_next_graph)
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        # --- Export PDF button ---
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

        # --- Initialize navigation button states ---
        self._update_nav_buttons()

    # --- Draws one of the five measurement preview graphs ---
    def _plot_graph(self, index):
        """
        Plot one of the five measurement graphs inside the canvas.
        Each plot is centered and includes a grid for clarity.
        """
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("white")
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.18)  # Balanced margins

        freqs = self.freqs if self.freqs is not None else np.linspace(1e6, 1e8, 100)
        s11 = self.s11_data if self.s11_data is not None else np.exp(1j * np.linspace(0, 2*np.pi, 100))
        s21 = self.s21_data if self.s21_data is not None else 20 * np.log10(np.abs(np.sin(freqs / 1e8 * np.pi)))

        if index == 0:

            self.fig.subplots_adjust(left=0.1, right=0.9, top=0.82, bottom=0.18)

            # --- Smith Chart (S11) ---
            ax.set_title("Smith Chart - S11", fontsize=12, weight="bold", pad=20)
            rf.plotting.smith(ax=ax, smithR=1)
            gamma = s11
            ax.plot(np.real(gamma), np.imag(gamma), color="red", linewidth=1.2)

            # Force equal aspect and centered axes
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlim(-1.1, 1.1)
            ax.set_ylim(-1.1, 1.1)
            ax.set_xticks([])
            ax.set_yticks([])

            ax.plot([-1, 1], [0, 0], color="black", linewidth=1)  # Real axis

            # Center title precisely
            ax.title.set_position([0.5, 1.03])
        elif index == 1:
            # --- Magnitude |S11| ---
            ax.plot(freqs, 20 * np.log10(np.abs(s11)), color="red", linewidth=1.3)
            ax.set_title("Magnitude |S11| (dB)", fontsize=12, weight="bold", pad=12)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("|S11| (dB)")
            ax.grid(True, linestyle="--", alpha=0.6)
        elif index == 2:
            # --- Phase S11 ---
            ax.plot(freqs, np.angle(s11, deg=True), color="red", linewidth=1.3)
            ax.set_title("Phase S11 (°)", fontsize=12, weight="bold", pad=12)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("Phase (°)")
            ax.grid(True, linestyle="--", alpha=0.6)
        elif index == 3:
            # --- Magnitude |S21| ---
            ax.plot(freqs, s21, color="blue", linewidth=1.3)
            ax.set_title("Magnitude |S21| (dB)", fontsize=12, weight="bold", pad=12)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("|S21| (dB)")
            ax.grid(True, linestyle="--", alpha=0.6)
        elif index == 4:
            # --- Phase S21 ---
            phase_s21 = np.angle(np.exp(1j * freqs / 1e7), deg=True)
            ax.plot(freqs, phase_s21, color="blue", linewidth=1.3)
            ax.set_title("Phase S21 (°)", fontsize=12, weight="bold", pad=12)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("Phase (°)")
            ax.grid(True, linestyle="--", alpha=0.6)

        self.canvas.draw()


    # --- Navigation controls ---
    def _show_next_graph(self):
        """Show the next graph in sequence."""
        if self.current_graph_index < 4:
            self.current_graph_index += 1
            self._plot_graph(self.current_graph_index)
            self._update_nav_buttons()

    def _show_previous_graph(self):
        """Show the previous graph in sequence."""
        if self.current_graph_index > 0:
            self.current_graph_index -= 1
            self._plot_graph(self.current_graph_index)
            self._update_nav_buttons()

    def _update_nav_buttons(self):
        """Enable, disable, or hide navigation buttons depending on graph position."""
        if self.current_graph_index == 0:
            self.prev_button.hide()
            self.next_button.show()
        elif self.current_graph_index == 4:
            self.next_button.hide()
            self.prev_button.show()
        else:
            self.prev_button.show()
            self.next_button.show()

    # --- PDF generation ---
    def _generate_pdf(self):
        """Generate final PDF report using LaTeX exporter."""
        try:
            exporter = LatexExporter()
            if not self.output_path:
                QMessageBox.warning(self, "Missing Path", "No output path specified.")
                return

            logger.info(f"Starting LaTeX PDF export for {self.measurement_name}")
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
