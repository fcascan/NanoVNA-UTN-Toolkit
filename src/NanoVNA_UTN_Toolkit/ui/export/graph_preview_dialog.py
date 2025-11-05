"""
Graph Preview Export Dialog for NanoVNA Measurements
Provides an interactive preview of S-parameter graphs with navigation
and PDF export functionality using Matplotlib and PySide6.

Each graph has independent Marker 1 and Marker 2 checkboxes.
Markers can be dragged independently for each graph.
Deactivating a marker hides its cursor immediately.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QWidget,
    QCheckBox, QHBoxLayout, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import skrf as rf
import logging
import copy

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

        self.saved_figures = []
        self.current_figure = 0

        self.current_index = 0
        self.saved_graphs = []
        self.total_graphs = 5

        # Track marker states for each graph separately
        self.graph_markers = {}  # key=index, value=[marker1_active, marker2_active]
        self.annotations = []    # active annotations for current graph
        self.markers = []        # marker Line2D objects

        self.marker_positions = {i: [None, None] for i in range(5)}
        self.marker_active = {i: [False, False] for i in range(5)}

        self.setWindowTitle("Export Graph Preview")
        self.setModal(True)
        self.setMinimumSize(700, 450)

        main_layout = QVBoxLayout(self)

        # --- Instruction label
        label = QLabel(
            "Graph preview is ready.\n"
            "Use the arrows below to explore all measurement views before exporting the PDF."
        )
        label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label)

        # --- Create figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.fig.patch.set_facecolor("white")
        self.ax.set_facecolor("white")
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.18)
        self.canvas = FigureCanvas(self.fig)

        # --- Canvas container
        self.canvas_container = QWidget()
        self.canvas_container.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(self.canvas_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        main_layout.addWidget(self.canvas_container, alignment=Qt.AlignCenter)

        # --- Previous / Next buttons
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

        # --- Marker checkboxes y frecuencia inputs
        self.marker_checkboxes = {}  # key=graph_index, value=(marker1, marker2)
        self.marker_freq_edits = {}  # key=graph_index, value=(edit1, combo1, edit2, combo2)

        for i in range(5):
            # --- Checkboxes
            marker1 = QCheckBox("Marker 1")
            marker1.setStyleSheet("color: red; font-weight: bold;")
            marker2 = QCheckBox("Marker 2")
            marker2.setStyleSheet("color: blue; font-weight: bold;")
            marker1.stateChanged.connect(lambda _, idx=i: self._update_markers(idx))
            marker2.stateChanged.connect(lambda _, idx=i: self._update_markers(idx))
            self.marker_checkboxes[i] = (marker1, marker2)

            # --- Frequency inputs para cada marker (NO fusionados, estilo blanco)
            edit1 = QLineEdit()
            edit1.setFixedWidth(80)
            edit1.setStyleSheet("background-color: white; color: black;")
            combo1 = QComboBox()
            combo1.addItems(["kHz", "MHz", "GHz"])
            combo1.setStyleSheet("background-color: white; color: black;")
            edit2 = QLineEdit()
            edit2.setFixedWidth(80)
            edit2.setStyleSheet("background-color: white; color: black;")
            combo2 = QComboBox()
            combo2.addItems(["kHz", "MHz", "GHz"])
            combo2.setStyleSheet("background-color: white; color: black;")

            # --- Conectar señales para actualizar markers
            edit1.editingFinished.connect(self._on_marker_input_changed)
            combo1.currentIndexChanged.connect(self._on_marker_input_changed)
            edit2.editingFinished.connect(self._on_marker_input_changed)
            combo2.currentIndexChanged.connect(self._on_marker_input_changed)
            # --- Guardar
            self.marker_freq_edits[i] = (edit1, combo1, edit2, combo2)

        # --- Layout para markers y sus inputs
        self.marker_layout = QHBoxLayout()
        self.marker_layout.setContentsMargins(0, 0, 0, 0)
        self.marker_layout.setSpacing(20)
        self.marker_layout.addStretch()

        marker_container = QWidget()
        marker_container_layout = QHBoxLayout(marker_container)
        marker_container_layout.setContentsMargins(0, 0, 0, 0)
        marker_container_layout.addStretch()
        marker_container_layout.addLayout(self.marker_layout)
        marker_container_layout.addStretch()

        # --- Navigation + marker layout
        nav_marker_layout = QHBoxLayout()
        nav_marker_layout.setContentsMargins(15, 5, 15, 5)
        nav_marker_layout.setSpacing(10)
        nav_marker_layout.addWidget(self.prev_button)
        nav_marker_layout.addStretch()
        nav_marker_layout.addWidget(marker_container)
        nav_marker_layout.addStretch()
        nav_marker_layout.addWidget(self.next_button)

        main_layout.addLayout(nav_marker_layout)

        # --- Export button
        self.export_button = QPushButton("Generate PDF Report")
        self.export_button.setEnabled(False)
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

        # --- Connect navigation
        self.prev_button.clicked.connect(self._show_previous_graph)
        self.next_button.clicked.connect(self._show_next_graph)

        # --- Initial plot
        self._plot_graph(self.current_graph_index)
        self._update_marker_checkboxes()
        self._update_markers()
        self._update_nav_buttons()

    def _on_marker_input_changed(self):
        self._update_markers(self.current_graph_index+1)

    # --- Update marker checkboxes + frequency edits
    def _update_marker_checkboxes(self):
        for i in reversed(range(self.marker_layout.count())):
            item = self.marker_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                else:
                    layout_item = item.layout()
                    if layout_item:
                        while layout_item.count():
                            child = layout_item.takeAt(0)
                            if child.widget():
                                child.widget().setParent(None)

        self.marker_layout.addStretch()
        marker1, marker2 = self.marker_checkboxes[self.current_graph_index]
        edit1, combo1, edit2, combo2 = self.marker_freq_edits[self.current_graph_index]

        # --- Marker 1 layout
        vbox1 = QVBoxLayout()
        vbox1.addWidget(marker1, alignment=Qt.AlignCenter)
        vbox1.addWidget(edit1, alignment=Qt.AlignCenter)
        vbox1.addWidget(combo1, alignment=Qt.AlignCenter)

        # --- Marker 2 layout
        vbox2 = QVBoxLayout()
        vbox2.addWidget(marker2, alignment=Qt.AlignCenter)
        vbox2.addWidget(edit2, alignment=Qt.AlignCenter)
        vbox2.addWidget(combo2, alignment=Qt.AlignCenter)

        self.marker_layout.addLayout(vbox1)
        self.marker_layout.addLayout(vbox2)
        self.marker_layout.addStretch()
        self.canvas.draw_idle()

    # --- Plot graph ---
    def _plot_graph(self, index):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("white")
        self.fig.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.18)

        freqs = self.freqs if self.freqs is not None else np.linspace(1e6, 1e8, 100)
        s11 = self.s11_data if self.s11_data is not None else np.exp(1j * np.linspace(0, 2*np.pi, 100))
        s21 = self.s21_data if self.s21_data is not None else 20 * np.log10(np.abs(np.sin(freqs / 1e8 * np.pi)))

        if index == 0:
            self.fig.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)

            # Set title for the Smith chart
            self.ax.set_title("Smith Chart - S11", fontsize=12, weight="bold", pad=20)
            
            # Create a temporary network just for plotting the Smith chart background with labels
            dummy_freq = rf.Frequency(1, 10, 10, unit='GHz')
            dummy_s = np.zeros((10, 1, 1), dtype=complex)
            dummy_ntw = rf.Network(frequency=dummy_freq, s=dummy_s)
            
            # Plot the Smith chart grid with labels in black, without adding legend entry
            dummy_ntw.plot_s_smith(ax=self.ax, draw_labels=True, color='black', lw=0.5, label=None)
            
            # Plot actual S11 data on top
            gamma = s11
            line, = self.ax.plot(np.real(gamma), np.imag(gamma), color="red", linewidth=1.2, label="S11")
            
            # Adjust appearance
            self.ax.set_aspect("equal", adjustable="box")
            self.ax.set_xlim(-1.1, 1.1)
            self.ax.set_ylim(-1.1, 1.1)
            self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

            # Custom legend showing only the S11 trace
            legend = self.ax.legend(
                handles=[line],
                loc="upper left",
                fontsize=9,
                facecolor="white",
                edgecolor="black",
                framealpha=1,
                title=None
            )
            legend.set_draggable(True)


        elif index == 1:
            self.ax.plot(freqs, 20 * np.log10(np.abs(s11)), color="red", linewidth=1.3)
            self.ax.set_title("Magnitude |S11| (dB)", fontsize=12, weight="bold", pad=12)
            self.ax.set_xlabel("Frequency (Hz)")
            self.ax.set_ylabel("|S11| (dB)")
            self.ax.grid(True, linestyle="--", alpha=0.6)
        elif index == 2:
            self.ax.plot(freqs, np.angle(s11, deg=True), color="red", linewidth=1.3)
            self.ax.set_title("Phase S11 (°)", fontsize=12, weight="bold", pad=12)
            self.ax.set_xlabel("Frequency (Hz)")
            self.ax.set_ylabel("Phase (°)")
            self.ax.grid(True, linestyle="--", alpha=0.6)
        elif index == 3:
            self.ax.plot(freqs, 20*np.log10(np.abs(s21)), color="blue", linewidth=1.3)
            self.ax.set_title("Magnitude |S21| (dB)", fontsize=12, weight="bold", pad=12)
            self.ax.set_xlabel("Frequency (Hz)")
            self.ax.set_ylabel("|S21| (dB)")
            self.ax.grid(True, linestyle="--", alpha=0.6)
        elif index == 4:
            phase_s21 = np.angle(np.exp(1j * freqs / 1e7), deg=True)
            self.ax.plot(freqs, phase_s21, color="blue", linewidth=1.3)
            self.ax.set_title("Phase S21 (°)", fontsize=12, weight="bold", pad=12)
            self.ax.set_xlabel("Frequency (Hz)")
            self.ax.set_ylabel("Phase (°)")
            self.ax.grid(True, linestyle="--", alpha=0.6)

        self.canvas.draw()
        self._update_markers(index)

    # --- Navigation ---
    def _show_next_graph(self):
        fig_copy = copy.deepcopy(self.fig)
        self.saved_figures.append(fig_copy)

        if self.current_graph_index < self.total_graphs - 1:
            self.current_graph_index += 1
            self._plot_graph(self.current_graph_index)
            self._update_nav_buttons()
            self._update_marker_checkboxes()

        self.export_button.setEnabled(self.current_graph_index == self.total_graphs - 1)

    def _show_previous_graph(self):
        fig_copy = copy.deepcopy(self.fig)
        self.saved_figures.append(fig_copy)

        if self.current_graph_index > 0:
            self.current_graph_index -= 1
            self._plot_graph(self.current_graph_index)
            self._update_nav_buttons()
            self._update_marker_checkboxes()

        self.export_button.setEnabled(self.current_graph_index == self.total_graphs - 1)

    def _update_nav_buttons(self):
        self.prev_button.setVisible(self.current_graph_index > 0)
        self.next_button.setVisible(self.current_graph_index < 4)

    # --- Marker handling ---
    def _update_markers(self, graph_index=None):
        if graph_index is None:
            graph_index = self.current_graph_index

        ax = self.ax
        freqs = self.freqs if self.freqs is not None else np.linspace(1e6, 1e8, 100)
        s11 = self.s11_data if self.s11_data is not None else np.exp(1j * np.linspace(0, 2*np.pi, 100))
        s21 = self.s21_data if self.s21_data is not None else 20 * np.log10(np.abs(np.sin(freqs / 1e8 * np.pi)))

        marker1, marker2 = self.marker_checkboxes[graph_index]
        self.marker_active[graph_index] = [marker1.isChecked(), marker2.isChecked()]

        for ann in getattr(self, "annotations", []):
            ann.set_visible(False)
        for mk in getattr(self, "markers", []):
            mk.set_visible(False)
        self.annotations = []
        self.markers = []

        colors = ["green", "orange"]
        edits = self.marker_freq_edits[graph_index]

        for i, active in enumerate(self.marker_active[graph_index]):
            if active:
                edit, unit = (edits[0], edits[1]) if i == 0 else (edits[2], edits[3])

                try:
                    freq_val = float(edit.text())
                    unit_factor = {"kHz": 1e3, "MHz": 1e6, "GHz": 1e9}[unit.currentText()]
                    freq_val_hz = freq_val * unit_factor
                except Exception:
                    freq_val_hz = freqs[len(freqs)//3 if i == 0 else 2*len(freqs)//3]
                    freq_val = freq_val_hz / 1e6
                    unit.setCurrentText("MHz")

                idx = (np.abs(freqs - freq_val_hz)).argmin()

                if graph_index == 0:
                    x, y = np.real(s11[idx]), np.imag(s11[idx])
                elif graph_index == 1:
                    x, y = freqs[idx], 20*np.log10(np.abs(s11[idx]))
                elif graph_index == 2:
                    x, y = freqs[idx], np.angle(s11[idx], deg=True)
                elif graph_index == 3:
                    x, y = freqs[idx], 20*np.log10(np.abs(s21[idx]))
                elif graph_index == 4:
                    phase_s21 = np.angle(np.exp(1j * freqs / 1e7), deg=True)
                    x, y = freqs[idx], phase_s21[idx]

                mk_line, = ax.plot(x, y, marker='o', color=colors[i], markersize=8)

                # --- Mostrar frecuencia automáticamente en GHz si corresponde ---
                if unit.currentText() == "MHz" and freq_val >= 1000:
                    freq_val /= 1000
                    unit_display = "GHz"
                else:
                    unit_display = unit.currentText()

                freq_display = f"{freq_val:.2f} {unit_display}"

                # --- Texto del marcador ---
                if graph_index == 0:
                    text = (
                        f"Marker {i+1}\n"
                        f"Freq: {freq_display}\n"
                        f"Re: {np.real(s11[idx]):.3f}\n"
                        f"Im: {np.imag(s11[idx]):.3f}"
                    )
                elif graph_index in [1, 3]:
                    text = f"Marker {i+1}\nFreq: {freq_display}\n|S|: {y:.3f} dB"
                else:
                    text = f"Marker {i+1}\nFreq: {freq_display}\nPhase: {y:.3f}°"

                ann = ax.annotate(
                    text,
                    xy=(x, y),
                    xycoords='data',
                    bbox=dict(facecolor='white', edgecolor=colors[i], alpha=0.7),
                    color=colors[i]
                )

                self.markers.append(mk_line)
                self.annotations.append(ann)
                self.marker_positions[graph_index][i] = (x, y)

        self._enable_drag_annotations()
        self.canvas.draw()

    # --- Draggable markers ---
    def _enable_drag_annotations(self):
        drag_state = {"dragging": None, "mode": None, "corner": None}

        def detect_corner(bbox, x, y, tol=8):
            if abs(x - bbox.x1) < tol and abs(y - bbox.y1) < tol:
                return "top_right"
            return None

        def on_move_hover(event):
            if event.inaxes != self.ax:
                self.canvas.setCursor(Qt.ArrowCursor)
                return
            renderer = self.canvas.get_renderer()
            for ann in self.annotations:
                bbox = ann.get_window_extent(renderer=renderer)
                if detect_corner(bbox, event.x, event.y):
                    self.canvas.setCursor(Qt.SizeBDiagCursor)
                    return
                if bbox.contains(event.x, event.y):
                    self.canvas.setCursor(Qt.OpenHandCursor)
                    return
            self.canvas.setCursor(Qt.ArrowCursor)

        def on_press(event):
            if event.inaxes != self.ax:
                return
            renderer = self.canvas.get_renderer()
            for ann in self.annotations:
                bbox = ann.get_window_extent(renderer=renderer)
                corner = detect_corner(bbox, event.x, event.y)
                if corner:
                    drag_state.update({
                        "dragging": ann,
                        "mode": "resize",
                        "corner": corner,
                        "fontsize0": ann.get_fontsize()
                    })
                    return
                if bbox.contains(event.x, event.y):
                    idx = self.annotations.index(ann)
                    drag_state.update({
                        "dragging": ann,
                        "mode": "move",
                        "corner": None,
                        "x0": ann.xy[0],
                        "y0": ann.xy[1],
                        "press_xdata": event.xdata,
                        "press_ydata": event.ydata,
                        "idx": idx
                    })
                    return

        def on_motion(event):
            if drag_state["dragging"] is None or event.xdata is None or event.ydata is None:
                return
            ann = drag_state["dragging"]
            if drag_state["mode"] == "move":
                dx = event.xdata - drag_state["press_xdata"]
                dy = event.ydata - drag_state["press_ydata"]
                new_pos = (drag_state["x0"] + dx, drag_state["y0"] + dy)
                ann.set_position(new_pos)
                idx = drag_state["idx"]
                self.marker_positions[self.current_graph_index][idx] = new_pos
            elif drag_state["mode"] == "resize" and drag_state["corner"] == "top_right":
                renderer = self.canvas.get_renderer()
                bbox = ann.get_window_extent(renderer=renderer)
                delta = event.x - bbox.x1 + bbox.y1 - event.y
                new_size = max(6, drag_state["fontsize0"] + delta * 0.05)
                ann.set_fontsize(new_size)
            self.canvas.draw_idle()

        def on_release(event):
            drag_state["dragging"] = None
            drag_state["mode"] = None
            drag_state["corner"] = None
            drag_state.pop("idx", None)

        self.canvas.mpl_connect('motion_notify_event', on_move_hover)
        self.canvas.mpl_connect('button_press_event', on_press)
        self.canvas.mpl_connect('motion_notify_event', on_motion)
        self.canvas.mpl_connect('button_release_event', on_release)

    def _save_current_graph(self):
        if not hasattr(self, "saved_figures"):
            self.saved_figures = []
        fig_copy = copy.deepcopy(self.fig)
        self.saved_figures.append(fig_copy)

    # --- PDF Export ---
    def _generate_pdf(self):
        try:
            self._save_current_graph()

            from NanoVNA_UTN_Toolkit.exporters.latex_exporter import LatexExporter
            exporter = LatexExporter(figures=self.saved_figures)
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
