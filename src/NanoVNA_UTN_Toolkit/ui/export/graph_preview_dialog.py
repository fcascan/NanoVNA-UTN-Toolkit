from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from NanoVNA_UTN_Toolkit.exporters.latex_exporter import LatexExporter
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

        self.setWindowTitle("Export Graph Preview")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        label = QLabel(
            "Graph preview is ready.\n"
            "Click below to generate the final PDF report using LaTeX."
        )
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

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
        layout.addWidget(self.export_button)
        layout.addStretch()

    def _generate_pdf(self):
        """
        Called when user clicks 'Generate PDF Report'.
        Uses LatexExporter to actually build and compile the LaTeX file.
        """
        try:
            exporter = LatexExporter()

            # Validación previa
            if not self.output_path:
                QMessageBox.warning(self, "Missing Path", "No output path specified.")
                return

            # Generación del PDF
            logger.info(f"Starting LaTeX PDF export for {self.measurement_name}")
            success = exporter.export_to_pdf(
                freqs=self.freqs,
                s11_data=self.s11_data,
                s21_data=self.s21_data,
                measurement_name=self.measurement_name,
                output_path=self.output_path  # Usa la ruta seleccionada en latex_export_dialog
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
